import os
import json
import pandas as pd
import random
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

def generate_insight_cards(df: pd.DataFrame, num_cards=5) -> list:
    """Generate meaningful insight cards based on dataset columns"""
    cards = []
    columns = df.columns.tolist()
    
    if len(columns) < 2:
        print("Dataset needs at least 2 columns to generate insights")
        return cards
    
    # Generate meaningful insights
    for i in range(num_cards):
        if i % 3 == 0:  # Distribution insights
            col = random.choice(columns)
            cards.append({
                "question": f"What is the distribution of {col}?",
                "reason": f"Understanding how values are distributed in the {col} column"
            })
        elif i % 3 == 1:  # Correlation insights
            col1, col2 = random.sample(columns, 2)
            cards.append({
                "question": f"How does {col1} relate to {col2}?",
                "reason": f"Exploring the relationship between {col1} and {col2}"
            })
        else:  # Aggregate insights
            agg_col = random.choice(columns)
            agg_func = random.choice(["average", "sum", "max", "min"])
            group_col = random.choice(columns)
            cards.append({
                "question": f"What is the {agg_func} of {agg_col} by {group_col}?",
                "reason": f"Analyzing {agg_col} aggregated by {group_col}"
            })
    
    return cards

def main():
    dataset_path = input("Enter path to CSV file: ").strip()
    
    if not os.path.exists(dataset_path):
        print(f"File not found: {dataset_path}")
        return
    
    try:
        df = pd.read_csv(dataset_path, on_bad_lines='skip')
        print(f"✅ Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        
        # Generate insight cards
        insight_cards = generate_insight_cards(df, num_cards=5)
        
        if not insight_cards:
            print("⚠️ No insight cards generated")
            return
        
        # Create data directory if needed
        os.makedirs("data", exist_ok=True)
        insights_path = "data/insight_cards.json"
        
        # Save insights to JSON
        with open(insights_path, 'w') as f:
            json.dump(insight_cards, f, indent=2)
        print(f"💾 Saved {len(insight_cards)} insights to {insights_path}")
        
        print("📥 RAG system is ready to use")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()