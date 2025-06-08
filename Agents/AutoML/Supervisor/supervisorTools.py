import sys
import os
from langchain_core.messages import ToolMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Splitting.splitter import splitter_node
from Preprocessing.pipeline import preprocessing_node
from HPO.tuner import tuner_node
from ModelSelection.selector import model_selector_node
from modelEvaluation.evaluator import evaluator_node
from modelTraining.trainer import trainer_node
from featureSelection.selector import feature_selector_node


tools = [splitter_node,
         preprocessing_node,
         tuner_node,
         model_selector_node,
         trainer_node,
         feature_selector_node]


async def tool_node(state):
    old_state=state.copy()
    tools_by_name = {tool.name: tool for tool in tools}
    messages = state["messages"]
    # get the last message of this state
    last_message = messages[-1]
    output_messages = []
    new_state = state.copy()
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["state"] = new_state
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])

            output_messages.append(
                ToolMessage(
                    content=tool_result[0],
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            new_state.update(tool_result[1])

        except Exception as e:
            raise e
            # Return the error if the tool call fails
            output_messages.append(
                ToolMessage(
                    content=f"an error occurred while running the tool: {str(e)}",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    status="error",
                )
            )
    new_state['messages']=old_state['messages']+output_messages
    return new_state