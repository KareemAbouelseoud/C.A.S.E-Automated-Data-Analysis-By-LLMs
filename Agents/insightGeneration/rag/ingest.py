# This is a one-time script you run to process and store your insight cards.
# It reads data, converts it into the langchain.docstore.document.Document format, and uses the VectorStoreManager to save it.
import logging
from rag.config import VectorStoreManager
from langchain.docstore.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_data():
    """
    Reads insight cards, converts them to Document objects,
    and adds them to the vector store.
    """
    logger.info("Starting data ingestion process...")

    # --- Sample Insight Cards ---
    # In a real application, you would load this from a file, database, or API.
    insight_cards_data = [
        "In Q2, sales of 'Product A' increased by 25% in the North America region, primarily driven by the new marketing campaign.",
        "Customer satisfaction scores for 'Service B' have dropped by 10% this quarter, with main complaints centered around long wait times.",
        "The recent 'Project Phoenix' was completed 2 weeks ahead of schedule and 5% under budget.",
        "Analysis shows that customers who purchase 'Product A' are 60% more likely to also buy 'Accessory C'.",
        "Website traffic from organic search grew by 15% month-over-month, but the bounce rate on the pricing page remains high at 75%."
    ]

    # Convert the raw text into Document objects
    documents = [Document(page_content=text) for text in insight_cards_data]
    
    if not documents:
        logger.warning("No data to ingest.")
        return

    # Add documents to the vector store
    try:
        VectorStoreManager.add_documents(documents)
        logger.info("Data ingestion completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during ingestion: {e}")

if __name__ == "__main__":
    ingest_data()
