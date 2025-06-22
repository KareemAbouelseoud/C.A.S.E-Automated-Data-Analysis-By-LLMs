import os
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def rag_responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("RAG responder node started")
    try:
        # Check if insights data exists
        insights_path = "data/insight_cards.json"
        if not os.path.exists(insights_path):
            logger.warning("Insights data not found")
            return {
                **state,
                "use_agent": True,
                "response": ""
            }
            
        # Load stored insights
        with open(insights_path, 'r') as f:
            insights = json.load(f)
        
        # If no insights, use agent
        if not insights:
            logger.info("No insights available")
            return {
                **state,
                "use_agent": True,
                "response": ""
            }
        
        # Create Gemini-compatible prompt (no system messages)
        prompt = f"""
        USER: You are an AI assistant that decides whether a user query can be answered using available insights.
        Query: {state["user_query"]}
        
        Available Insights:
        {json.dumps(insights, indent=2)}
        
        INSTRUCTION: 
        Can the query be answered with these insights? 
        Respond only with YES or NO.
        """
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1
        )
        
        # Get decision from judge LLM
        response = await llm.ainvoke(prompt)
        decision = response.content.strip().upper()
        logger.info(f"Judge decision: {decision}")
        
        # If judge says YES, return the first insight
        if "YES" in decision:
            return {
                **state,
                "response": f"{insights[0].get('question', '')}\n{insights[0].get('reason', '')}",
                "insights": [insights[0]],
                "method": "rag",
                "use_agent": False
            }
        
        # If judge says NO, use the agent
        logger.info("No relevant insights found, using agent")
        return {
            **state,
            "use_agent": True,
            "response": ""
        }
        
    except Exception as e:
        logger.error(f"RAG error: {str(e)}")
        return {
            **state,
            "use_agent": True,
            "response": ""
        }