import os
from dotenv import load_dotenv

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 

DEFAULT_EMBEDDING_MODEL = "models/text-embedding-004"
DEFAULT_LLM = "gemini-2.0-flash" 

CHROMA_PERSIST_DIR = "chroma_db_persist"
METADATA_PKL_FILE = "vectorstore_metadata.pkl" 

DOCUMENT_CONTENT_DESCRIPTION = "Represents a single row from a data table."
BATCH_SIZE = 500 
MAX_PAGE_CONTENT_LENGTH = 512

ENCODINGS_TO_TRY = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']