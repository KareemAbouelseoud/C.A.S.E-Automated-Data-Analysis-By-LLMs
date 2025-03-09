from typing import TypedDict

from .config import *
sys.path.append(os.getcwd())


#define states
class AgentGraphState(TypedDict):
    df: str
    description: str
    human_feedback: Annotated[list[str], add_messages]
    insight_cards: List[Dict[str, str]]
   

#GRAPH PIPELINE
graph_builder = StateGraph(AgentGraphState)
#define nodes
graph_builder.add_node("data_description", data_description_generator_node)
graph_builder.add_node("human_node", human_input)
graph_builder.add_node("qugen_node", qugen_node)
graph_builder.add_node("filteration_node", filterationA_node)
#define edges
graph_builder.add_edge(START, "data_description")
graph_builder.add_edge("data_description", "human_node")
graph_builder.add_edge("human_node", "qugen_node")
graph_builder.add_conditional_edges("qugen_node", should_continue, {"qugen_node": "qugen_node", "filteration_node": "filteration_node"})
graph_builder.add_edge("filteration_node", END)
#verify and display the graph
#compile the graph
checkpointer=MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

#TEST

#mock dataset
# file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
# dataset = pd.read_csv(file_path)

async def Start_Auto_InsightGen(project_id:str=None):
    df = await get_dataset(project_id)
    print("Dataset loaded")
    state = AgentGraphState({"df": df.to_json()})  
    thread_config= {"configurable": {"thread_id": uuid.uuid4()}}
    try:
        async for chunk in graph.astream(state, config=thread_config):
            for node_id, value in chunk.items():
                print(f"Processing node {node_id}")  # Debug logging
                if node_id == "__interrupt__":
                    yield tuple((value[0],{"thread_id":thread_config["configurable"]["thread_id"]}))
                else:
                    print(f"Node {node_id} output: {value}")
    except Exception as e:
        print(f"Error in test(): {str(e)}")
        raise

async def Continue_Auto_InsightGen(feedback: str, thread_id: str):
    config = {'configurable': {'thread_id': uuid.UUID(thread_id)}}
    result = graph.get_state(config=config)
    
    if not result[0]:
        raise ValueError(f"No state found for thread_id: {thread_id}")
    
    # Get the current state directly from result[0]
    current_state = result[0]
    
    
    # Preserve existing state and append new feedback
    updated_state = AgentGraphState({
        'df': current_state.get('df', ''),
        'description': current_state.get('description', ''),
        'human_feedback': current_state.get('human_feedback', []) + [feedback],
        'insight_cards': current_state.get('insight_cards', [])
    })
    
    try:
        if feedback.lower() == 'done':
            # Use await instead of async for with ainvoke
            result = await graph.ainvoke(Command(resume=feedback), config=config)
            yield tuple((result, {"thread_id": str(config["configurable"]["thread_id"])}))
        else:
            async for chunk in graph.astream(updated_state, config=config):
                for node_id, value in chunk.items():
                    if node_id == "__interrupt__":
                        yield tuple((value[0], {"thread_id": config["configurable"]["thread_id"]}))
    except Exception as e:
        print(f"Error in Continue_Auto_InsightGen: {str(e)}")
        raise


