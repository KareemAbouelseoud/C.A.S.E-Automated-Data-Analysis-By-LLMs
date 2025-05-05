import os
import shutil
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.self_query.base import SelfQueryRetriever
from typing import List, Dict, Any

import config
from data_processing import (
    load_csv_robustly,
    prepare_documents_and_metadata,
    save_metadata,
    load_metadata
)

class GenericCsvRAGSystem:
   
    def __init__(self,
                 embedding_model: str = config.DEFAULT_EMBEDDING_MODEL,
                 llm_model: str = config.DEFAULT_LLM,
                 persist_directory: str = config.CHROMA_PERSIST_DIR,
                 metadata_save_path: str = config.METADATA_PKL_FILE):
        """
        Initializes the RAG system components.

        Args:
            embedding_model: Name of the Google Generative AI embedding model.
            llm_model: Name of the Google Generative AI chat model.
            persist_directory: Directory to save/load the Chroma database.
            metadata_save_path: Path to save/load the metadata field info.
        """
        if not config.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not found in environment variables. Langchain components might fail if it's required and not implicitly found.")

        # Initialize embedding models (separate for query and document)
        self.query_embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            task_type="retrieval_query",
            google_api_key=config.GOOGLE_API_KEY 
        )
        self.doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            task_type="retrieval_document",
            google_api_key=config.GOOGLE_API_KEY 
        )

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model,
            google_api_key=config.GOOGLE_API_KEY, 
            temperature=0.1, # Low temperature for more factual responses
            convert_system_message_to_human=True 
        )

        # Initialize other attributes
        self.vector_store = None
        self.metadata_field_info = []
        self.document_content_description = config.DOCUMENT_CONTENT_DESCRIPTION
        self.persist_directory = persist_directory
        self.metadata_save_path = metadata_save_path

        # prompt template for the RAG chain
        self.prompt_template = ChatPromptTemplate.from_template(
            """Analyze the provided context, which consists of rows retrieved from a larger dataset based on the question, to answer the question comprehensively.

            Consider the following aspects of the retrieved data:
            - Identify key entities, values, and relationships mentioned.
            - Summarize relevant numerical data, ranges, or trends if present.
            - Note any categorical distinctions or patterns.
            - Extract information directly addressing the question.

            Context Rows:
            ----------------
            {context}
            ----------------

            Question: {question}

            Provide a structured response:
            1.  **Direct Answer:** Concisely answer the question based *only* on the provided context rows. If the context doesn't contain the answer, state that clearly.
            2.  **Supporting Evidence:** Quote or reference specific data points from the context that support your answer.
            3.  **Confidence:** Estimate your confidence (High/Medium/Low) that the provided context is sufficient to fully answer the question.
            4.  **Limitations:** Mention any potential limitations based *only* on the provided context (e.g., "Context only includes data for [specific category]", "Numerical data is limited"). Do not speculate about the full dataset unless the question asks for it.
            """
        )
        print("GenericCsvRAGSystem initialized.")

    def _load_vector_store(self):
        """Loads the Chroma vector store from the persistence directory."""
        print(f"Attempting to load Chroma database from: {self.persist_directory}")
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.doc_embeddings # Crucial: Use the same embedder used for creation
            )
            # Verify collection exists and has data (optional but recommended)
            try:
                 collection_name = self.vector_store._collection.name
                 count = self.vector_store._client.get_collection(collection_name).count()
                 if count == 0:
                     print(f"Warning: Loaded Chroma collection '{collection_name}' is empty.")
                 else:
                      print(f"Loaded collection '{collection_name}' with {count} items.")
            except Exception as chroma_err:
                print(f"Warning: Could not verify count of loaded Chroma collection: {chroma_err}")
            print("Chroma DB loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load Chroma DB from {self.persist_directory}: {e}")
            self.vector_store = None # Ensure it's None if loading fails
            return False

    def _create_vector_store(self, documents: List[Any]):
        """Creates and persists a new Chroma vector store from documents."""
        print(f"Creating new Chroma index in: {self.persist_directory}...")
        try:
            os.makedirs(self.persist_directory, exist_ok=True)

            # --- Batching for large datasets ---
            num_batches = (len(documents) + config.BATCH_SIZE - 1) // config.BATCH_SIZE
            print(f"Adding {len(documents)} documents in {num_batches} batches of size {config.BATCH_SIZE}...")

            for i in range(num_batches):
                start_idx = i * config.BATCH_SIZE
                end_idx = min((i + 1) * config.BATCH_SIZE, len(documents))
                batch_docs = documents[start_idx:end_idx]

                if not batch_docs: # Skip empty batches
                    continue

                if i == 0:
                    # Create the store with the first batch
                    self.vector_store = Chroma.from_documents(
                        documents=batch_docs,
                        embedding=self.doc_embeddings, # Use document embedder
                        persist_directory=self.persist_directory

                    )
                else:
                    # Add subsequent batches to the existing store
                    # Ensure vector_store is initialized
                    if self.vector_store is None:
                         raise RuntimeError("Vector store was not initialized in the first batch.")
                    self.vector_store.add_documents(batch_docs)


                print(f"  Batch {i+1}/{num_batches} added ({len(batch_docs)} documents).")

            # Persist changes explicitly after all batches (recommended)
            if self.vector_store:

                 pass 

            print("Chroma index created and persisted successfully.")

        except Exception as e:
            print(f"Error creating or persisting Chroma DB: {e}")

            if os.path.exists(self.persist_directory):
                print(f"Cleaning up potentially corrupted directory: {self.persist_directory}")
                try:
                    shutil.rmtree(self.persist_directory)
                except OSError as oe:
                    print(f"Error removing Chroma directory during cleanup: {oe}")
            self.vector_store = None # Ensure vector store is None after failure
            raise # Re-raise the exception to signal failure


    def load_and_process_data(self, file_path: str, force_reindex: bool = False):
        """
        Loads CSV data, processes it, and creates/loads the vector store and metadata.

        Args:
            file_path: Path to the CSV file.
            force_reindex: If True, ignores existing index/metadata and re-processes.
        """
        print("-" * 50)
        print(f"Starting data loading and processing for: {file_path}")
        print(f"Force Re-index: {force_reindex}")
        print("-" * 50)

        #  Cleanup if forcing reindex 
        if force_reindex:
            print("Force re-index enabled. Removing existing persisted data...")
            if os.path.exists(self.persist_directory):
                try:
                    shutil.rmtree(self.persist_directory)
                    print(f"Removed directory: {self.persist_directory}")
                except OSError as e:
                    print(f"Error removing directory {self.persist_directory}: {e}")
            if os.path.exists(self.metadata_save_path):
                try:
                    os.remove(self.metadata_save_path)
                    print(f"Removed file: {self.metadata_save_path}")
                except OSError as e:
                    print(f"Error removing file {self.metadata_save_path}: {e}")
            self.vector_store = None # Reset in-memory store if forcing reindex

        # Attempt to load existing data 
        loaded_from_disk = False
        if not force_reindex and not self.vector_store: # Only load if not already in memory
            if os.path.exists(self.persist_directory) and os.path.exists(self.metadata_save_path):
                print("Persisted data found. Attempting to load...")
                try:
                    # Load metadata first
                    self.metadata_field_info, self.document_content_description = load_metadata(self.metadata_save_path)
                    # Then load vector store
                    loaded_vs = self._load_vector_store()
                    if loaded_vs and self.metadata_field_info:
                        loaded_from_disk = True
                        print("Successfully loaded vector store and metadata from disk.")
                    else:
                         print("Loading from disk failed. Proceeding to re-index.")
                         # Clean up potentially inconsistent state
                         self.vector_store = None
                         self.metadata_field_info = []
                except Exception as e:
                    print(f"Error loading persisted data: {e}. Proceeding to re-index.")
                    # Clean up potentially inconsistent state
                    self.vector_store = None
                    self.metadata_field_info = []
            else:
                print("No complete persisted data found (missing directory or metadata file).")

        # Process and index if not loaded 
        if not loaded_from_disk:
            print("Processing and indexing new data...")
            try:
                df = load_csv_robustly(file_path)

                documents, self.metadata_field_info = prepare_documents_and_metadata(df)

                # 3. Create Vector Store
                self._create_vector_store(documents)

                # 4. Save Metadata Info
                save_metadata(self.metadata_field_info, self.document_content_description, self.metadata_save_path)

                print("Data processing and indexing complete.")

            except Exception as e:
                print(f"FATAL: An error occurred during data processing/indexing: {e}")
                # Ensure state is clean after failure
                self.vector_store = None
                self.metadata_field_info = []
               
                raise 

        print("-" * 50)
        print("Data loading and processing finished.")
        print("-" * 50)


    def query(self, question: str, k: int = 10) -> str:
        """
        Executes a RAG query using the SelfQueryRetriever.

        Args:
            question: The user's question.
            k: The maximum number of documents (rows) to retrieve.

        Returns:
            The LLM's generated answer as a string.

        Raises:
            ValueError: If the system is not properly initialized (no vector store or metadata).
        """
        print("-" * 50)
        print(f"Executing query (k={k}): '{question}'")
        print("-" * 50)

        if not self.vector_store:

            print("Vector store not in memory. Checking disk...")
            loaded = self._load_vector_store()
            if not loaded:
                 raise ValueError("Vector store not initialized and could not be loaded from disk. Run 'load_and_process_data()' first.")

        if not self.metadata_field_info:

             if os.path.exists(self.metadata_save_path):
                 print("Metadata not in memory. Checking disk...")
                 try:
                     self.metadata_field_info, self.document_content_description = load_metadata(self.metadata_save_path)
                     print("Loaded metadata from disk.")
                 except Exception as e:
                     raise ValueError(f"Metadata not available and failed to load from disk: {e}. Run 'load_and_process_data()' first.")
             else:
                raise ValueError("Metadata field info not available. Run 'load_and_process_data()' first.")




        print("Using SelfQueryRetriever with Chroma...")
        try:
            retriever = SelfQueryRetriever.from_llm(
                llm=self.llm,
                vectorstore=self.vector_store,
                document_contents=self.document_content_description,
                metadata_field_info=self.metadata_field_info,
                verbose=True,
                
                enable_limit=True, # Allow 'limit' in generated query (maps to k)

            )
            print("SelfQueryRetriever instantiated successfully.")
        except Exception as e:
             print(f"Error creating SelfQueryRetriever: {e}")
             print("Falling back to basic vector store retriever.")

             retriever = self.vector_store.as_retriever(search_kwargs={'k': k})



      
        
        rag_chain = (
            # The input to the chain is expected to be a dictionary, e.g., {"question": "user query"}
            # 1. Pass the question through to the retriever context assignment
            # 2. Retrieve context based on the question
            # 3. Assemble prompt inputs
            # 4. Call LLM
            RunnablePassthrough.assign(
                # The retriever takes the question string as input
                context=(lambda inputs: inputs['question']) | retriever
            )
            | self.prompt_template 
            | self.llm            
            
        )
        #  End RAG Chain Definition 


        print("\nInvoking RAG chain...")
        try:
            # Pass the question in the expected dictionary format
            response = rag_chain.invoke({"question": question})

            # Extract content from the response object (often AIMessage)
            if hasattr(response, 'content'):
                result = response.content
            else:
                print(f"Warning: LLM response object type is {type(response)}. Converting to string.")
                result = str(response)

            print("\nQuery execution finished.")
            print("-" * 50)
            return result

        except Exception as e:
            print(f"\nFATAL: Error during RAG chain invocation: {e}")
            # Attempt to get retrieved docs for debugging context
            try:
                print("\nAttempting to retrieve documents directly for debugging...")
                retrieved_docs = retriever.invoke(question) # Pass question string directly
                print("\n--- Retrieved Documents (for debugging) ---")
                if retrieved_docs:
                    for i, doc in enumerate(retrieved_docs):
                        print(f"Doc {i+1}:")
                        page_content_snippet = getattr(doc, 'page_content', 'N/A')[:200] + "..."
                        metadata_repr = getattr(doc, 'metadata', {})
                        print(f"  Content: {page_content_snippet}")
                        print(f"  Metadata: {metadata_repr}")
                else:
                    print("No documents were retrieved by the retriever.")
                print("------------------------------------------")
            except Exception as re:
                print(f"Could not retrieve documents for debugging: {re}")

            # Return a meaningful error message yarab n5lasss
            error_message = f"An error occurred while processing the query: {e}. Please check logs or try rephrasing shokran."
            print("-" * 50)
            return error_message