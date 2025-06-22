import pandas as pd
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def PandasAgentResponder(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Agent node started")
    try:
        df = state["df"]
        query = state["user_query"]
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            timeout=120
        )
        
        # Create agent
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            agent_type="tool-calling",
            verbose=False
        )

        # Get response
        response = await agent.ainvoke(query)
        output = response.get("output", "No response generated")
        logger.info(f"Agent response: {output[:100]}...")

        return {
            **state,
            "response": output,
            "method": "agent",
            "resulted_df": df
        }
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return {
            **state,
            "response": f"Error: {str(e)}",
            "method": "error"
        }