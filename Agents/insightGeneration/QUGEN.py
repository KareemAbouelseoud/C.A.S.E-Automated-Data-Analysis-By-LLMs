from typing import Dict, List
import re
from data_description_generator import AgentGraphState
import numpy as np
from data_description_generator import AgentGraphState
from scoringFunction import score_attribution, score_distribution_difference


class QUGEN:
    def __init__(self, model, iterations=3, questions_per_iter=5, temperature=0):
        self.model = model
        self.iterations = iterations
        self.questions_per_iter = questions_per_iter
        self.temperature = temperature

    def invoke(self, state: AgentGraphState) -> AgentGraphState:
        # Validate input state
        required_keys = ["schema", "description", "df", "basic_stats"]
        if any(key not in state for key in required_keys):
            raise ValueError("Missing required dataset information in state")

        df = state["df"]
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        insights = []
        for iteration in range(self.iterations):
            new_insights = self._generate_insights(
                state,
                previous_insights=insights[-self.questions_per_iter :],
                numeric_cols=numeric_cols,
            )
            insights.extend(new_insights)

        # Pass the df parameter here
        state["insight_cards"] = self._filter_insights(
            insights,
            state["schema"],
            numeric_cols,
            df,  # Added df argument
        )[:10]

        return state

    def _generate_insights(self, state, previous_insights, numeric_cols):
        """Generate insights with context from previous iterations"""
        example_context = (
            "\n\n".join(
                f"REASON: {insight['reason']}\nQUESTION: {insight['question']}"
                f"\nBREAKDOWN: {insight['breakdown']}\nMEASURE: {insight['measure']}"
                for insight in previous_insights
            )
            if previous_insights
            else "First iteration - no previous examples"
        )

        prompt = f"""**Dataset Context**
Schema: {state["schema"]}
Numeric Columns: {numeric_cols}
Description: {state["description"]}
Basic Statistics:\n{"basic_stats"}

**Previous Insights**
{example_context}

**Task**
Generate {self.questions_per_iter} NEW insight cards following EXACT format:

REASON: The rationale behind the question.
QUESTION: <natural language question>
BREAKDOWN: <aggregation>(<numeric_column>)
MEASURE: <categorical/temporal_column>

**Rules**
1. Use different aggregations (MIN/MAX/MEAN/COUNT/SUM/STD)
2. Measure columns must from the dataset
3. No duplicate combinations of breakdown/measure
4. Prioritize under-utilized columns from schema: {state["schema"]}"""

        response = self.model.generate_content(prompt)
        return self._parse_insight_cards(response.text, state["schema"], numeric_cols)

    def _format_basic_stats(self, basic_stats):
        """Safely format basic statistics for prompts"""
        stats_str = []

        if "numerical" in basic_stats and not basic_stats["numerical"].empty:
            stats_str.append(
                "Numerical Statistics:\n" + basic_stats["numerical"].to_string()
            )

        if "categorical" in basic_stats and not basic_stats["categorical"].empty:
            stats_str.append(
                "Categorical Statistics:\n" + basic_stats["categorical"].to_string()
            )

        return "\n\n".join(stats_str) if stats_str else "No statistics available"

    def _insight_to_text(self, insight):
        """Convert insight card to text format"""
        return "\n".join(
            [
                f"REASON: {insight['reason']}",
                f"QUESTION: {insight['question']}",
                f"BREAKDOWN: {insight['breakdown']}",
                f"MEASURE: {insight['measure']}",
            ]
        )

    def _parse_insight_cards(self, text, schema, numeric_cols):
        """Robust parsing with regex validation"""
        cards = []
        current_card = {}

        # n2sem el states mn el cards
        card_blocks = re.split(r"(?=\nREASON:|^REASON:)", text.strip())

        for block in card_blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]

            for line in lines:
                if line.startswith("REASON:"):
                    current_card["reason"] = line.split(":", 1)[1].strip()
                elif line.startswith("QUESTION:"):
                    current_card["question"] = line.split(":", 1)[1].strip()
                elif line.startswith("BREAKDOWN:"):
                    breakdown = line.split(":", 1)[1].strip()
                    current_card["breakdown"] = breakdown
                    # Extract aggregation and column
                    match = re.match(r"(\w+)\((\w+)\)", breakdown)
                    if match:
                        current_card["aggregation"] = match.group(1).upper()
                        current_card["measure_column"] = match.group(2)
                elif line.startswith("MEASURE:"):
                    current_card["measure"] = line.split(":", 1)[1].strip()

            if self._validate_insight(current_card, schema, numeric_cols):
                cards.append(current_card)
                current_card = {}

        return cards

    def _validate_insight(self, insight, schema, numeric_cols):
        """Strict validation of insight structure"""
        required_keys = ["reason", "question", "breakdown", "measure"]
        if any(key not in insight for key in required_keys):
            return False

        # Validate measure column exists and is categorical
        if insight["measure"] not in schema or insight["measure"] in numeric_cols:
            return False

        # Validate breakdown components
        if "measure_column" not in insight or "aggregation" not in insight:
            return False

        valid_aggregations = {
            "MEAN",
            "MEDIAN",
            "SUM",
            "COUNT",
            "MIN",
            "MAX",
            "STD",
            "VAR",
        }
        return (
            insight["aggregation"] in valid_aggregations
            and insight["measure_column"] in numeric_cols
        )

    def _filter_insights(self, insights, schema, numeric_cols, df):  # Now receives df
        seen = set()
        filtered = []

        for insight in insights:
            if not self._validate_insight(insight, schema, numeric_cols):
                continue

            uid = (
                insight["measure"],
                insight["breakdown"],
                insight["question"].lower().replace("?", "").strip(),
            )

            if uid in seen:
                continue
            seen.add(uid)

            score = self._calculate_insight_score(insight, df)
            if score is None:
                continue

            filtered.append(
                {
                    **insight,
                    "score": score,
                }
            )

        return sorted(filtered, key=lambda x: -x["score"])

    def _calculate_insight_score(self, insight, df):
        try:
            measure_col = insight["measure"]
            agg_type = insight["aggregation"]

            if agg_type == "COUNT":
                counts = df[measure_col].value_counts(normalize=True).values
                uniform = np.ones_like(counts) / len(counts)
                return score_distribution_difference(counts, uniform)
            else:
                numeric_col = insight["measure_column"]
                grouped = df.groupby(measure_col)[numeric_col]
                values = getattr(grouped, agg_type.lower())().values
                return score_attribution(values)

        except Exception as e:
            print(f"Scoring error: {e}")
            return None
