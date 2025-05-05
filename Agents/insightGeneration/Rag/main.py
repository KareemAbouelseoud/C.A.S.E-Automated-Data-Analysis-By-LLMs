
import os
import sys
import traceback

from rag_system import GenericCsvRAGSystem
import config 
def run_queries(rag_system_instance: GenericCsvRAGSystem, query_list: list):
    """Runs a list of queries through the RAG system and prints results."""
    for i, q in enumerate(query_list):
        print(f"\n--- Query {i+1} / {len(query_list)} ---")
        try:
            response = rag_system_instance.query(q)
            print(f"\nAnalysis Results {i+1}:\n", response)
        except Exception as e:
            print(f"\nError executing query {i+1}: {e}")
            print("Traceback:")
            traceback.print_exc() 
        print("-" * 30) 


if __name__ == "__main__":
    print("Starting Generic CSV RAG System...")

   
    csv_file_path = "Titanic-Dataset.csv"
  
    if not os.path.exists(csv_file_path):
        print(f"\nError: The specified CSV file was not found at '{csv_file_path}'.")
        print("Please ensure the file exists at this location or update the 'csv_file_path' variable in main.py.")
        sys.exit(1) # Exit if file not found
   
    try:
       
        rag_system = GenericCsvRAGSystem()

     
        rag_system.load_and_process_data(csv_file_path, force_reindex=False)

        example_queries = [
            "Summarize the survival rate based on passenger class (Pclass).",
            "List the names and ages of female passengers in Pclass 1 who survived.",
            "How many passengers paid a fare greater than 100?",
            "What was the embarkation port for passenger ID 5?",
            "Compare the average age of male survivors in Pclass 1 versus male non-survivors in Pclass 3.",
            "Which passenger had the highest fare, and what was it?",
        ]

        run_queries(rag_system, example_queries)

        print("\n--- RAG System Finished ---")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please ensure the CSV file exists and the path is correct.")
    except ValueError as e:
        print(f"\nConfiguration or Value Error: {e}")
    except ImportError as e:
        print(f"\nImport Error: {e}. Have you installed all required packages?")
        print("Try: pip install pandas python-dotenv langchain langchain-google-genai langchain-community chromadb tiktoken numpy")
    except Exception as e:
        
        print(f"\nAn unexpected error occurred: {e}")
        print("Traceback:")
        traceback.print_exc() 
        sys.exit(1)