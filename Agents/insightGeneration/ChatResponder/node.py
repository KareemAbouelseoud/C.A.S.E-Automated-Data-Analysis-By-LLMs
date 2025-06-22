import pandas as pd
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from typing import Dict, Any

logger = logging.getLogger(__name__)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, timeout=120)

async def PandasAgentResponder(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent responder node for state graph"""
    try:
        # Extract state elements
        df = state["df"]
        query = state["user_query"]
        
        # Create and invoke agent
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            agent_type="tool-calling",
            verbose=False,
        )
        
        response = await agent.ainvoke(query)
        output = response.get("output", "No response generated")
        
        # Update state
        return {
            **state,
            "response": output,
            "method": "agent",
            "resulted_df": df,  # Agent might modify df in future
            "use_agent": False  # Agent processing complete
        }
    except Exception as e:
        logger.error(f"Agent failed: {str(e)}")
        return {
            **state,
            "response": f"Error processing query: {str(e)}",
            "method": "agent (with error)"
        }