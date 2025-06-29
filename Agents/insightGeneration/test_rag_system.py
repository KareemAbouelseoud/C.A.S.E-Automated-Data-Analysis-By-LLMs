import os
import sys
import asyncio
import json
import time
import traceback
import pandas as pd
from Chat_Pipeline import respond_to_UserQuery

# Add current directory to path
sys.path.append(os.getcwd())

async def main():
    print("=" * 60)
    print("             AI Insights & Analysis Test Interface")
    print("=" * 60)
    
    # Check for RAG data
    insights_path = "data/insight_cards.json"
    print(f"Checking for RAG insights at: '{os.path.abspath(insights_path)}'")
    if os.path.exists(insights_path):
        print("[SUCCESS] RAG system initialized")
    else:
        print("\n[WARNING] Insights data not found.")
        print("To enable RAG features, please run:")
        print(f"    python generate_insights.py")

    # Get dataset path
    dataset_path = ""
    while not dataset_path:
        path_input = input("\nEnter path to CSV file: ").strip()
        if os.path.exists(path_input) and path_input.endswith('.csv'):
            dataset_path = path_input
            print(f"[SUCCESS] Using dataset: {dataset_path}")
        else:
            print(f"[ERROR] File not found: '{path_input}'. Please try again.")

    # Start chat session
    print("\n--- Starting Chat Session ---")
    print("Type questions below or 'exit' to quit")
    
    while True:
        query = input("\n[You]: ").strip()
        if query.lower() == 'exit':
            break
            
        start_time = time.time()
        print("\n[AI is thinking...]")
        
        try:
            final_response = None
            async for response_json in respond_to_UserQuery(dataset_path, query):
                final_response = json.loads(response_json)

            if final_response:
                method = final_response.get('method', 'Unknown').upper()
                response_text = final_response.get('response', 'No response')
                
                print("\n" + "=" * 25 + f" RESPONSE ({method}) " + "=" * 25)
                print(f"\n{response_text}")
                
                # Format insights better
                if method == "RAG":
                    insights = final_response.get("insights", [])
                    if insights:
                        print("\n--- Relevant Insights ---")
                        for i, insight in enumerate(insights, 1):
                            print(f"  {i}. {insight.get('question', 'No question')}")
                            print(f"     {insight.get('reason', 'No reason')}")
                
                # Show data results if available
                if method == "AGENT":
                    print("\n--- Resulting Data ---")
                    print(final_response.get("response"))
                elapsed = time.time() - start_time
                print("\n" + "-" * 60)
                print(f"Time: {elapsed:.2f}s")
            else:
                print("[ERROR] No response generated")
                
        except Exception as e:
            print(f"\n[ERROR] {e}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
