import asyncio
import json
import logging
import os
import sys
import pandas as pd
from langgraph.graph import StateGraph, END
from rag.rag_node import rag_responder_node
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
    insight_cards: List[object]
    insights_explanation: Dict[str, str]
    logs: list

async def get_dataset(file_path: str) -> pd.DataFrame:
    """
    Load dataset from a local CSV file path.
    """
    logger.info(f"Attempting to load dataset from local file: {file_path}")
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path, on_bad_lines='skip')
        else:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except Exception as e:
        logger.error(f"Failed to load dataset from '{file_path}': {e}")
        # Return an empty DataFrame on any error
        return pd.DataFrame()


graph_builder = StateGraph(AgentState)

# --- Add all nodes to the graph ---

graph_builder.add_node("rag_responder", rag_responder_node)
graph_builder.add_node("agent_responder", PandasAgentResponder)

# --- Define the graph's flow ---


def should_continue(state: AgentState) -> str:
    """
    This function decides the next step after the RAG responder runs.
    If the 'use_agent' flag is True, it routes to the agent.
    Otherwise, it ends the graph execution.
    """
    if state.get("use_agent", False):
        return "agent_responder"
    else:
        return END

# 2. Define the conditional edge. After 'rag_responder' runs, call 'should_continue'.

graph_builder.add_edge("__start__", "rag_responder")


graph_builder.add_conditional_edges(
    "rag_responder",
    should_continue,
    {
        "agent_responder": "agent_responder",
        END: END
    }
)

graph_builder.add_edge("agent_responder", END)

 
graph = graph_builder.compile()

async def respond_to_UserQuery(project_id: str, user_query: str):
    # The project_id is in the local file path
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
        resulted_df=None,
        insight_cards=[],
        insights_explanation={},
        logs=[]
    )

    final_state = None
    async for chunk in graph.astream(initial_state):
        for key, value in chunk.items():
            logger.info(f"--- Graph Node '{key}' Finished ---")
            final_state = value

    resulted_df_json = None
    if final_state.get("resulted_df") is not None:
        if isinstance(final_state["resulted_df"], pd.DataFrame):
            resulted_df_json = final_state["resulted_df"].to_json(orient='split')
        else:
            resulted_df_json = str(final_state["resulted_df"])

    yield json.dumps({
        "user_query": final_state["user_query"],
        "response": final_state["response"],
        "method": final_state.get("method", "Unknown"),
        "insights": final_state.get("insights", []),
        "resulted_df": resulted_df_json
    })