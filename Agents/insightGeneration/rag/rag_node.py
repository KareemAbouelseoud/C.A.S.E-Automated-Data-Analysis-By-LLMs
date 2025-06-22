import logging
from .config import VectorStoreManager
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any

# --- Configuration ---
logger = logging.getLogger(__name__)
# Initialize the LLM once to be reused.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5, timeout=120)

def format_insights_for_prompt(insights: list) -> str:
    """Formats the list of insight dictionaries into a single string for the prompt."""
    if not insights:
        return "No specific insights were found."
    
    formatted_string = "Here are the relevant insights found:\n\n"
    for i, insight in enumerate(insights, 1):
        formatted_string += f"Insight {i} (Relevance Score: {insight['score']:.4f}):\n"
        formatted_string += f"\"{insight['content']}\"\n\n"
    return formatted_string

async def rag_responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    This node orchestrates the RAG response. It retrieves documents, decides whether
    to use RAG or fallback to an agent, and generates a response if applicable.
    """
    logger.info("--- Executing RAG Responder Node ---")
    try:
        query = state["user_query"]
        insights = VectorStoreManager.retrieve_insights(query)
        
        # If no relevant insights are found, set flag to use the agent and return.
        if not insights:
            logger.info("No relevant insights found. Routing to agent.")
            return {**state, "use_agent": True, "method": "Agent (Fallback)"}
        
        logger.info(f"Found {len(insights)} insights. Preparing to generate RAG response.")
        
        # --- THIS IS THE CRITICAL FIX ---
        # The retrieved insights are now included in the prompt.
        insights_context = format_insights_for_prompt(insights)
        
        prompt_template = f"""
You are an AI assistant. Your task is to answer the user's query based *only* on the provided context.
Be concise and directly address the query. If the context does not contain the answer, state that clearly. Do not use any external knowledge.

CONTEXT:
{insights_context}

QUERY:
{query}

ANSWER:
"""
        
        # Invoke the LLM with the augmented prompt
        response = await llm.ainvoke(prompt_template)
        
        # Update the state with the RAG response and retrieved insights
        return {
            **state,
            "response": response.content,
            "insights": insights,
            "method": "RAG",
            "use_agent": False  # Signal that the agent is not needed
        }
    except Exception as e:
        logger.error(f"Error in RAG responder node: {e}", exc_info=True)
        # Fallback to the agent on any error
        return {**state, "use_agent": True, "method": "Agent (Error Fallback)"}

