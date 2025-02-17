import operator
from langchain_core.messages import AnyMessage
from langgraph.graph import START, StateGraph
from typing import TypedDict, Annotated, NotRequired
from dotenv import load_dotenv
import os
import sys
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
from Selector import selector_node,should_continue  # Update with actual import path

load_dotenv()

class GraphState(TypedDict):
    """
    Represents the state of the model selection workflow using basic dict types
    """
    project_id: str
    problem_type: str
    mode: str
    recommendations: NotRequired[list]
    model_selection_messages: Annotated[list[AnyMessage], operator.add]


# Create workflow builder
builder = StateGraph(GraphState)

# Add nodes
builder.add_node("model_selector", selector_node)

# Set up edges
builder.add_edge(START, "model_selector")
builder.add_conditional_edges("model_selector", should_continue)

# Compile the graph
model_selection_graph = builder.compile()

async def execute_pipeline(project_id: str, problem_type: str, mode: str):
    """Production execution entry point"""
    initial_state = {
        "project_id": project_id,
        "problem_type": problem_type,
        "mode": mode.upper(),
        "model_selection_messages": ["I recommend the following models:"]
    }
    
    final_state = await model_selection_graph.ainvoke(initial_state)
    recommendations = final_state["recommendations"]
    for model in recommendations:
        final_state["model_selection_messages"].append(model)
    print(final_state)
    return (final_state) 

async def main():
    """Example execution with real parameters"""
    # Replace with your actual project ID and parameters
    final_state = await execute_pipeline(
        project_id=1,
        problem_type="classification",
        mode="ATHENA"
    )
    
    print("Model Selection Results:")
    print(json.dumps(final_state, indent=2))

if __name__ == "__main__":
    asyncio.run(main())