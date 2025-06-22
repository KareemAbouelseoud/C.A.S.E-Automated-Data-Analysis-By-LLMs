import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import VECTOR_STORE_PATH, INSIGHTS_DATA_PATH, EMBEDDING_MODEL

def ingest_insights(insight_cards):
    """Ingest insight cards into vector store"""
    # Create texts for embedding
    texts = [f"{card.question}\nREASON: {card.reason}" for card in insight_cards]
    
    # Create embeddings - with settings for BGE model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create and save vector store
    vector_store = FAISS.from_texts(texts, embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"✅ Ingested {len(insight_cards)} insights into vector store")