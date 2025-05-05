import asyncio
from typing import Tuple, TypedDict
from typing_extensions import Any

from dotenv import load_dotenv

from .config import *
from QUGEN.node import qugen_node,should_continue
from SubSpaceSearch.node import SubspaceSearchNode
from Explainer.node import ExplainerNode
from Reports.node import ReportNode
from models import InsightCard, InsightCards
import loggerModule
logger=loggerModule.setup_logging(module_name="InsightGeneration")
sys.path.append(os.getcwd())
load_dotenv()

#define states
class AgentGraphState(TypedDict):
    df: str
    description: str
    human_feedback: Annotated[list[str], add_messages]
    schema: list[str]
    insight_cards: List[object]
    advanced_insight_cards: Dict[str, List[Tuple[Dict[str,List],object]]]
    insights_explanation: Dict[str, Dict[str,Any]]
    num_cards: int
    report: str
   

#GRAPH PIPELINE
graph_builder = StateGraph(AgentGraphState)
#define nodes
graph_builder.add_node("data_description", data_description_generator_node)
graph_builder.add_node("Report_Node", ReportNode)
graph_builder.add_node("human_node", human_input)
graph_builder.add_node("qugen_node", qugen_node)
graph_builder.add_node("filteration_node", filterationA_node)
graph_builder.add_node("SubSbaceSearch_Node", SubspaceSearchNode)
graph_builder.add_node("explainer_node", ExplainerNode)
graph_builder.add_node("Finalize_output", finalize_output)

#define edges
graph_builder.add_edge(START, "Report_Node")
graph_builder.add_edge("Report_Node", "data_description")
graph_builder.add_edge("data_description","human_node")
graph_builder.add_edge("human_node", "qugen_node")
graph_builder.add_conditional_edges("qugen_node", should_continue, {"qugen_node": "qugen_node", "filteration_node": "filteration_node"})
graph_builder.add_edge("filteration_node", "SubSbaceSearch_Node")
graph_builder.add_edge("SubSbaceSearch_Node", "explainer_node")
graph_builder.add_edge("explainer_node","Finalize_output")
graph_builder.add_edge("Finalize_output", END)
#verify and display the graph
#compile the graph
checkpointer=MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)


async def Start_Auto_InsightGen(project_id:str=None):
    df = await get_dataset(project_id)
    logger.info("Dataset loaded")
    state = AgentGraphState({"df": df.to_json()})  
    thread_config= {"configurable": {"thread_id": uuid.uuid4()}}
    try:
        async for chunk in graph.astream(state, config=thread_config):
            for node_id, value in chunk.items():
                logger.info(f"Processing node {node_id}")  # Debug logging
                if node_id == "__interrupt__":
                    yield tuple((value[0].value,{"thread_id":thread_config["configurable"]["thread_id"]}))
                else:
                    logger.info(f"Node {node_id} output: {value}")
    except Exception as e:
        logger.error(f"Error in test(): {str(e)}")
        raise e

async def Continue_Auto_InsightGen(_feedback: Feedback, thread_id: str):
    config = {'configurable': {'thread_id': uuid.UUID(thread_id)}}
    result = graph.get_state(config=config)
    
    if not result[0]:
        logger.error(f"No state found for thread_id: {thread_id}")
        raise ValueError(f"No state found for thread_id: {thread_id}")
    
    # Get the current state directly from result[0]
    current_state = result[0]
    
    
    # Preserve existing state and append new _feedback
    updated_state = AgentGraphState({
        'df': current_state.get('df', ''),
        'description': _feedback.description,
        "schema": current_state.get('schema', []),
        'human_feedback': _feedback.feedback,
        'insight_cards': current_state.get('insight_cards', [])
    })
    
    try:
        # Use await instead of async for with ainvoke
        logger.info("Continuing Pipeline ...")
        result = await graph.ainvoke(Command(resume=_feedback.feedback,update=updated_state), config=config)
        backend_dict={
            "insight_cards":result["insight_cards"],
            "advanced_insight_cards":result["advanced_insight_cards"],
            "insights_explanation":result["insights_explanation"],
            "num_cards":result["num_cards"],}
        _SaveInsights=SaveInsights(
            insight_cards=result["insight_cards"],
            advanced_insight_cards=result["advanced_insight_cards"],
            insights_explanation=result["insights_explanation"],
            num_cards=result["num_cards"]
        )
        print("Saving insights to the database...")
        print(f"Saving insights to the database...{_SaveInsights.model_dump()}")
        await save_insights(project_id=_feedback.project_id,insights=_SaveInsights)
        return tuple((backend_dict, {"thread_id": str(config["configurable"]["thread_id"])}))
        
    except Exception as e:
        logger.error(f"Error in Continue_Auto_InsightGen: {str(e)}")
        raise e

async def change_desc_on_feedback(_feedback:Feedback=None, thread_id:str=None):
    config = {'configurable': {'thread_id': uuid.UUID(thread_id)}}
    result = graph.get_state(config=config)
    
    if not result[0]:
        logger.error(f"No state found for thread_id: {thread_id}")
        raise ValueError(f"No state found for thread_id: {thread_id}")
    
    # Get the current state directly from result[0]
    current_state = result[0]
    
    
    # Preserve existing state and append new feedback
    updated_state = AgentGraphState({
        'df': current_state.get('df', ''),
        'description': current_state.get('description', ''),
        'human_feedback': _feedback.feedback,
        'insight_cards': current_state.get('insight_cards', [])
    })
    try:
        async for chunk in graph.astream(updated_state, config=config):
                for node_id, value in chunk.items():
                    if node_id == "__interrupt__":
                        yield tuple((value[0].value,{"thread_id":config["configurable"]["thread_id"]}))
                    else:
                        logger.info(f"Node {node_id} output: {value}")
    except Exception as e:
        logger.error(f"Error in Generating New Descritpion for the user: {str(e)}")
        raise e


