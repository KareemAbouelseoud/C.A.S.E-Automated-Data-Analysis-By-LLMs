import asyncio
from typing import Any, Tuple, TypedDict

from dotenv import load_dotenv

from .config import *
from ChatResponder.node import *
from models import InsightCard, InsightCards
import loggerModule
logger=loggerModule.setup_logging(module_name="InsightGeneration")
sys.path.append(os.getcwd())
load_dotenv()

class AgentGraphState(TypedDict):
    df: str
    user_query: str
    response: str
    resulted_df: Any 
    insight_cards: List[object]
    advanced_insight_cards: Dict[str, List[Tuple[Dict[str,List],object]]]
    insights_explanation: Dict[str, str]

graph_builder = StateGraph(AgentGraphState)
# Define nodes
graph_builder.add_node("responder", PandasAgentResponder)
graph_builder.add_edge(START, "responder")
graph_builder.add_edge("responder", END)
# Compile the graph
graph = graph_builder.compile()

async def respond_to_UserQuery(project_id: str, user_query: str):
    """
    This function is responsible for generating advanced insights based on the original insight card.
    It uses the LangChain framework to interact with the LLM and generate new insights.
    """
    df = await get_dataset(project_id)
    logger.info("Dataset loaded")
    # Create a state dictionary with the required keys
    state = {
        "df": df,
        "user_query": user_query,
        "response": None,
        "resulted_df": None,
        "insight_cards": [],
        "advanced_insight_cards": {},
        "insights_explanation": {}
    }
    
    # Run the graph pipeline with the initial state
    async for chunk in graph.astream(state, stream_mode=['updates','values']):
        if chunk[0] == 'values':
            result=chunk[1]
        elif chunk[0] == 'updates':
            for node,update in chunk[1].items():
                yield node
    
    yield json.dumps({
        "user_query": result["user_query"],
        "response": result["response"],
        "resulted_df": result["resulted_df"]
    })