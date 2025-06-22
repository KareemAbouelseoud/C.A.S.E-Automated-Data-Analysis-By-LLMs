import os
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_PATH = DATA_DIR / "vector_store"
INSIGHTS_DATA_PATH = DATA_DIR / "insight_cards.json"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Embedding model configuration
EMBEDDING_MODEL = "BAAI/bge-large-en"