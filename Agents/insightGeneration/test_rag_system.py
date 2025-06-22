import asyncio
import json
import os
import time
import traceback
import pandas as pd
from Chat_Pipeline import respond_to_UserQuery

async def main():
    print("=" * 50)
    print("RAG System Test Interface")
    print(f"Vector store path: '{os.path.abspath('insight_vector_store')}'")
    print("=" * 50)

    # Check if the vector store for RAG exists
    if not os.path.exists("insight_vector_store"):
        print("\nWARNING: Vector store not found.")
        print("RAG will not find insights. Please run 'python -m rag.ingest' first.")
    
    # --- NEW: Get local CSV file path from user for the agent ---
    dataset_path = ""
    while not dataset_path:
        path_input = input("Enter the path to the local CSV file for the agent to use: ").strip()
        # Normalize the path to handle different OS formats (e.g., slashes)
        path_input = os.path.normpath(path_input)
        if os.path.exists(path_input):
            dataset_path = path_input
        else:
            print(f"Error: File not found at '{path_input}'. Please enter a valid path.")

    # The project_id is now the local file path
    project_id = dataset_path
    print(f"Agent will use data from: {project_id}")

    # Start chat session
    while True:
        query = input("\nYour question (type 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break
        if not query:
            continue
            
        start_time = time.time()
        print(f"\nProcessing: '{query}'...")
        
        try:
            final_response = None
            # Pass the file path as the project_id
            async for response_json in respond_to_UserQuery(project_id, query):
                final_response = json.loads(response_json)

            if final_response:
                print("\n" + "=" * 20 + " FINAL RESPONSE " + "=" * 20)
                print(f"METHOD: {final_response.get('method', 'Unknown')}")
                print(f"\nRESPONSE:\n{final_response.get('response', 'No response text.')}")
                
                insights = final_response.get("insights", [])
                if insights:
                    print("\n--- Retrieved Insights (from RAG) ---")
                    for i, insight in enumerate(insights, 1):
                        print(f"[{i}] Score: {insight.get('score', 0):.4f} | Content: {insight.get('content', '')}")

                df_result = final_response.get('resulted_df')
                if df_result:
                    print("\n--- Resulting Data (from Agent) ---")
                    try:
                        df = pd.read_json(df_result, orient='split')
                        print(df.to_string())
                    except:
                        print(df_result)
                
                print("-" * 56)
                elapsed = time.time() - start_time
                print(f"Processing time: {elapsed:.2f} seconds")
                print("=" * 56)
            else:
                print("No final response was generated.")
                
        except Exception as e:
            print(f"\nAn unhandled error occurred: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

