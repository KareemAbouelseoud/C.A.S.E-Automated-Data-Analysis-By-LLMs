import os
import json
import pandas as pd
import random
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from rag.config import VECTOR_STORE_PATH, EMBEDDING_MODEL, INSIGHTS_DATA_PATH

# Load environment variables first
load_dotenv()

def generate_insight_cards(df: pd.DataFrame, num_cards=10) -> list:
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
        insight_cards = generate_insight_cards(df, num_cards=15)
        
        if not insight_cards:
            print("⚠️ No insight cards generated")
            return
        
        # Create data directory if needed
        os.makedirs(os.path.dirname(INSIGHTS_DATA_PATH), exist_ok=True)
        
        # Save insights to JSON
        with open(INSIGHTS_DATA_PATH, 'w') as f:
            json.dump(insight_cards, f, indent=2)
        print(f"💾 Saved {len(insight_cards)} insights to {INSIGHTS_DATA_PATH}")
        
        # Create and save the vector store
        print("Generating embeddings and creating vector store...")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Use the 'question' from each insight card for embedding
        insight_questions = [card['question'] for card in insight_cards]
        
        vector_store = FAISS.from_texts(texts=insight_questions, embedding=embeddings, metadatas=insight_cards)
        vector_store.save_local(VECTOR_STORE_PATH)
        
        print(f"✅ Vector store created and saved to {VECTOR_STORE_PATH}")
        
        print("📥 RAG system is ready to use")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()