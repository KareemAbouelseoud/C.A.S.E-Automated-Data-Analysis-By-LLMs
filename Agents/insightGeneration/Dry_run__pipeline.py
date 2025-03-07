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
graph_builder.add_node("data_description",  data_description_generator_node)
graph_builder.add_node("human_node", human_input)
graph_builder.add_node("QUGEN",qugen_node)
#define edges
graph_builder.add_edge(START, "data_description")
graph_builder.add_edge("data_description", "human_node")

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
    
    print(f"Retrieved state: {type(result)}")  # Debug logging
    
    if not result[0]:
        raise ValueError(f"No state found for thread_id: {thread_id}")
    
    state = result[0].values()  # Get the actual state
    
    # Create a new state with the required fields
    updated_state = AgentGraphState({
        'human_feedback': [feedback],  # Add new feedback as a list
    })
    if feedback.lower()=='done':
        try:
            async for chunk in graph.invoke(Command(resume=feedback), config=config):
                print(f"Received chunk: {chunk}")  # Debug logging
                for node_id, value in chunk.items():
                    print(f"Processing node {node_id}")  # Debug logging
                    if node_id == "__interrupt__":
                        yield tuple((value[0], {"thread_id": str(config["configurable"]["thread_id"])}))
                    else:
                        print(f"Node {node_id} output: {value}")
        except Exception as e:
            print(f"Error in Continue_Auto_InsightGen: {str(e)}")
            raise
    else:
        try:
            async for chunk in graph.astream(updated_state, config=config):
                for node_id, value in chunk.items():
                    print(f"Processing node {node_id}")  # Debug logging
                    if node_id == "__interrupt__":
                        yield tuple((value[0],{"thread_id":config["configurable"]["thread_id"]}))
                    else:
                        print(f"Node {node_id} output: {value}")
        except Exception as e:
            print(f"Error in test(): {str(e)}")
            raise


