from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal
import sys
import os
import pandas as pd
from io import StringIO
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from ..codeGeneration.pipeline import viz_graph
import json
from typing import Annotated
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

@tool
async def visualizer(
    visualization_request: Annotated[str,'The visualization request created by the assistant according to the user intent and data report'],
    project_id:str=None
    ):
    """
     Visualizes the user's query using a graph.
    Args:
        visualization_request (str): The visualization request created by the assistant according to the user intent and data report.
        project_id (str, optional): The ID of the project. Defaults to None.
    Returns:
        list: A list containing a message and the visualization data. If the visualization is generated, the message informs the user and includes the visualization data. Otherwise, the message informs the user that no visualization was generated and suggests trying again later.

    """
    graph_response=await viz_graph.ainvoke({'project_id':str(project_id),'messages':[{"role":"human","content":visualization_request}]})
    if graph_response['visualization']:
        return ['YOU MUST Inform the user that the visualization has been generated',graph_response['visualization']]
    else:
        return ['No visualization generated, inform the user to try again later',None]
    


tools = [visualizer,
         ]


async def tool_node(state):
    tools_by_name = {visualizer.name: visualizer,
                     }
    
    messages = state["messages"]
    # get the last message of this state
    last_message = messages[-1]
    output_messages = []
    visual_results=[]
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["project_id"] = state["project_id"]
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            if not isinstance(tool_result, list):
                tool_result=[tool_result]
            else:

                visual_results.append(tool_result[1])

            output_messages.append(
                ToolMessage(
                    content=tool_result[0],
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        except Exception as e:
            # Return the error if the tool call fails
            output_messages.append(
                ToolMessage(
                    content=f"an error occurred while running the tool: {str(e)}",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    status="error",
                )
            )
    return {'messages':output_messages,'visual':[visual_results]}
