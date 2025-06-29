import os
import json
import logging
from typing import Dict, Any, List
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)

def get_relevant_insights(user_query: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant insights from the vector store.
    """
    try:
        if not os.path.exists("data/vector_store"):
            logger.warning("Vector store not found. Please generate insights first.")
            return []
            
        vector_store = get_vector_store()
        # Retrieve top 3 most similar insights
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        relevant_docs = retriever.get_relevant_documents(user_query)
        
        # The metadata of the documents contains our original insight cards
        return [doc.metadata for doc in relevant_docs]

    except Exception as e:
        logger.error(f"Error retrieving insights from vector store: {e}")
        return []

async def rag_responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG node that uses a vector store to find relevant insights.
    """
    logger.info("--- RAG RESPONDER ---")
    user_query = state.get("user_query")
    
    # Retrieve relevant insights using semantic search
    relevant_insights = get_relevant_insights(user_query)
    
    if relevant_insights:
        logger.info(f"Found {len(relevant_insights)} relevant insights.")
        # For now, we'll just use the most relevant insight
        top_insight = relevant_insights[0]
        
        return {
            **state,
            "response": f"I found a relevant insight for your query:\n\n"
                        f"**Question:** {top_insight.get('question')}\n"
                        f"**Reason:** {top_insight.get('reason')}",
            "insights": relevant_insights,
            "method": "RAG",
            "use_agent": False
        }
    else:
        # If no relevant insights are found, delegate to the agent
        logger.info("No relevant insights found. Delegating to agent.")
        return {
            **state,
            "use_agent": True,
        }