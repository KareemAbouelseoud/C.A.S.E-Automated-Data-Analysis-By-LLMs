
# import os
# import pandas as pd
# import google.generativeai as genai
# from langchain_community.vectorstores import FAISS
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document
# # Initialize Gemini client with free API key
# class GeminiEmbeddings:
#     """Custom embedding class using Gemini's free API"""
    
#     def __init__(self, model_name="models/embedding-001"):
#         self.model_name = model_name
        
#     def embed_documents(self, texts):
#         return [self.embed_query(text) for text in texts]
    
#     def embed_query(self, text):
#         response = genai.embed_content(
#             model=self.model_name,
#             content=text
#         )
#         return response['embedding']

# def create_dataset_chunks(df):
#     """Create optimized document chunks with metadata"""
#     # Create base documents
#     docs = []
    
#     # 1. Schema documentation
#     schema_content = f"Dataset Schema:\n{df.dtypes.to_string()}"
#     docs.append(Document(schema_content, metadata={"type": "schema"}))
    
#     # 2. Statistical analysis
#     stats = df.describe(include='all').to_dict()
#     for col in df.columns:
#         col_stats = "\n".join([f"{k}: {v}" for k, v in stats[col].items()])
#         docs.append(Document(
#             f"Statistics for {col}:\n{col_stats}",
#             metadata={"type": "stats", "column": col}
#         ))
    
#     # 3. Cross-feature relationships
#     survival_rates = df.groupby(['Pclass', 'Sex'])['Survived'].mean()
#     analysis_content = "Survival Analysis:\n" + survival_rates.to_string()
#     docs.append(Document(analysis_content, metadata={"type": "analysis"}))
    
#     # Split documents
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         separators=["\n\n", "\n", ". ", " "]
#     )
#     return splitter.split_documents(docs)

# def rag_query(query, vector_store, k=3):
#     """Execute RAG query with context"""
#     # Retrieve relevant documents
#     docs = vector_store.similarity_search(query, k=k)
    
#     # Prepare context
#     context = "\n\n".join([d.page_content for d in docs])
    
#     # Generate answer
#     response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=[{
#             "parts": [{
#                 "text": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
#             }]
#         }]
#     )
    
#     return response.text, docs

# if __name__ == "__main__":
#     # Load Titanic dataset
#     df = pd.read_csv("Titanic-Dataset.csv")
    
#     # Create chunks
#     chunks = create_dataset_chunks(df)
    
#     # Initialize embeddings and vector store
#     embeddings = GeminiExperimentalEmbeddings()
#     vector_store = FAISS.from_documents(chunks, embeddings)
    
#     # Test embeddings
#     test_embed = embeddings.embed_query("Test embedding")
#     print(f"Embedding dimension: {len(test_embed)}")
    
#     # Example queries
#     queries = [
#         "What's the survival rate for females in 3rd class?",
#         "Compare age distributions between survivors and non-survivors",
#         "What's the most common embarkation port for survivors?"
#     ]
    
#     for query in queries:
#         answer, sources = rag_query(query, vector_store)
#         print(f"\nQuestion: {query}")
#         print(f"Answer: {answer}")
#         print("Source Contexts:")
#         for doc in sources:
#             print(f"- [{doc.metadata['type']}] {doc.page_content[:80]}...")

from google import genai



client = genai.Client(api_key="GEMINI_API_KEY")

result = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents="What is the meaning of life?")

print(result.embeddings)