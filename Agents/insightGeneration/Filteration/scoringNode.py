from scoringFunctions import (
    score_attribution, 
    score_distribution_difference,
    score_trend,
    score_outstanding_value
)
from ..QUGEN.prompts import InsightCard

class ScoringNode:
    def __init__(self):
        self.scoring_functions = {
            'attribution': score_attribution,
            'distribution_difference': score_distribution_difference,
            'trend': score_trend,
            'outstanding_value': score_outstanding_value
        }

    def process_state(self, state):
        """
        Process the graph state and score each card based on its insight type
        
        Args:
            state (dict): Dictionary containing cards and their data
            
        Returns:
            dict: Updated state with scored cards
        """
        if 'insight_cards' not in state:
            return state

        scored_cards = []
        
        for card in state['insight_cards']:
            # Handle both dict and InsightCard objects
            if isinstance(card, dict):
                card = InsightCard(**card)
            
            score = 0.0
            insight_type = card.insight_type

            # Access resulted_df from the InsightCard object
            if not card.resulted_df.empty:
                if insight_type == 'attribution':
                    score = self.scoring_functions['attribution'](card)
                    if score >= 0.5:
                        card.Considered = True
                
                elif insight_type == 'distribution_difference' and card.aggregation == 'COUNT':
                    # Assuming the resulted_df has initial and final values columns
                    if 'initial_values' in card.resulted_df.columns and 'final_values' in card.resulted_df.columns:
                        score = self.scoring_functions['distribution_difference'](
                            card.resulted_df['initial_values'].tolist(),
                            card.resulted_df['final_values'].tolist()
                        )
                
                elif insight_type == 'trend':
                    # Assuming resulted_df has values in a single column or series
                    if len(card.resulted_df.columns) > 0:
                        values = card.resulted_df[card.resulted_df.columns[0]].tolist()
                        score = self.scoring_functions['trend'](values)

                elif insight_type == 'outstanding_value':
                    # Assuming resulted_df has values in a single column or series
                    if len(card.resulted_df.columns) > 0:
                        values = card.resulted_df[card.resulted_df.columns[0]].tolist()
                        score = self.scoring_functions['outstanding_value'](values)
                        if score >= 1.4:
                            card.Considered = True

            # Create new dict with score added
            
            card.Score = float(score)
            

        # Update state with scored cards
        
        return state

    def process(self, state):
        """Main entry point for processing the state"""
        return self.process_state(state)