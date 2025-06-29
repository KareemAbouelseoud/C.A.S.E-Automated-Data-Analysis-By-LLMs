import asyncio
import json
import logging
import os
import sys
import pandas as pd
from langgraph.graph import StateGraph, END
from Rag.rag_node import rag_responder_node
from ChatResponder.node import PandasAgentResponder
from typing import Any, TypedDict, List, Dict, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
sys.path.append(os.getcwd())
load_dotenv()

# Define state structure
class AgentState(TypedDict):
    df: pd.DataFrame
    user_query: str
    response: str
    method: str
    use_agent: bool
    insights: Optional[List[Dict[str, Any]]]
    resulted_df: Optional[Any]

async def get_dataset(file_path: str) -> pd.DataFrame:
    """
    Load dataset from a local CSV file path.
    """
    logger.info(f"Attempting to load dataset from local file: {file_path}")
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, on_bad_lines='skip')
            logger.info(f"Dataset loaded with shape {df.shape}")
            return df
        else:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except Exception as e:
        logger.error(f"Failed to load dataset from '{file_path}': {e}")
        # Return an empty DataFrame on any error
        return pd.DataFrame()

# Build the graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("rag_responder", rag_responder_node)
graph_builder.add_node("agent_responder", PandasAgentResponder)

# Define the conditional edge
def should_continue(state: AgentState) -> str:
    if state.get("use_agent", False):
        return "agent_responder"
    else:
        return END

# Set the entry point
graph_builder.set_entry_point("rag_responder")

# Add conditional edge
graph_builder.add_conditional_edges(
    "rag_responder",
    should_continue,
    {
        "agent_responder": "agent_responder",
        END: END
    }
)

# Add edge from agent to end
graph_builder.add_edge("agent_responder", END)

# Compile the graph
graph = graph_builder.compile()




async def respond_to_UserQuery(project_id: str, user_query: str):
    df = await get_dataset(project_id)
    if df.empty:
        logger.warning(f"Could not load data from '{project_id}'. The agent may not function correctly.")

    initial_state = AgentState(
        df=df,
        user_query=user_query,
        response="",
        method="",
        use_agent=False,
        insights=None,
        resulted_df=None
    )

    final_state = initial_state
    try:
        # Execute the graph with error suppression
        async for chunk in graph.astream(initial_state):
            for key, value in chunk.items():
                if key not in ["__start__", "__end__"]:  # Skip internal nodes
                    logger.info(f"--- Graph Node '{key}' Finished ---")
                    final_state = value
    except KeyError as e:
        if '__start__' in str(e):
            logger.warning("Ignoring '__start__' key error")
        else:
            logger.error(f"Graph execution error: {str(e)}")
            final_state["response"] = f"System error: {str(e)}"
    except Exception as e:
        logger.error(f"Graph execution error: {str(e)}")
        final_state["response"] = f"System error: {str(e)}"
        
        
        
        
    resulted_df_json = None
    if final_state and final_state.get("resulted_df") is not None:
        if isinstance(final_state["resulted_df"], pd.DataFrame):
            resulted_df_json = final_state["resulted_df"].to_json(orient='split')
        else:
            resulted_df_json = str(final_state["resulted_df"])

    response = {
        "user_query": user_query,
        "response": "",
        "method": "error",
        "insights": [],
        "resulted_df": None
    }
    
    if final_state:
        response = {
            "user_query": final_state["user_query"],
            "response": final_state["response"],
            "method": final_state.get("method", "Unknown"),
            "insights": final_state.get("insights", []),
            "resulted_df": resulted_df_json
        }

    yield json.dumps(response)