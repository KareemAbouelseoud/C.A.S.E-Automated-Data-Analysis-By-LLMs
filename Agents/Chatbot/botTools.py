import sys
import os
from langchain_core.tools import tool,InjectedToolArg
from langchain_core.messages import ToolMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vizGeneration.pipeline import coder_pipeline,caller_pipeline,planner_node
from AutoML.pipeline import automl
from typing import Annotated,Optional
from API.Requests import projectRequests
import json
# from langgraph.config import get_stream_writer

@tool
async def visualizer(
    visualization_request: Annotated[str,'The visualization request created by the assistant according to the user intent and data report, atleast give plot type and columns to plot. Specify the columns as they are in the data report.'],
    data_report:Annotated[str,InjectedToolArg] = None,
    project_id:Annotated[str,InjectedToolArg] = None
    ):
    """
     Visualizes the user's query using a graph. Write the column names as given in the data report
    Args:
        visualization_request (str): The visualization request created by the assistant according to the user intent and data report.
    Returns:
        list: A list containing a message and the visualization data. If the visualization is generated, the message informs the user and includes the visualization data. Otherwise, the message informs the user that no visualization was generated and suggests trying again later.

    """
    print(f"VISUALIZER IS BEING CALLED WITH request: {visualization_request}")
    response=await planner_node(visualization_request)
    if 'coder' in response:
        graph_response = await coder_pipeline.ainvoke({'project_id':project_id,'messages':[{"role":"human","content":f"Here is the design needed {visualization_request}"}], 'data_report':data_report})
    else:
        graph_response = await caller_pipeline.ainvoke({'project_id':project_id,'messages':[{"role":"human","content":f"Here is the design needed {visualization_request}, and here is the data report crucial for the naming convention: {data_report}"}]})

    if graph_response['visualization']:
        return ['YOU MUST Inform the user that the visualization has been generated',graph_response['visualization']]
    else:
        return ['No visualization generated, inform the user to try again later',None]
    
@tool
async def builder(mode:Annotated[str,'The mode that the user has selected.There are 3 modes "HERMES" which is the fastest mode but sacrifices accuracy, "ATHENA" the balanced mode, and "HEPHAESTUS" which is the slowest mode but best accuracy.'],
            target_feature:Annotated[str,'The Target feature to predict'],
            exclude_features:Annotated[list[str],'The features to exclude from the training data. Do not suggest features to remove the user is only responsible for that.']=None,
            preferences:Optional[Annotated[str,'Any preferences the user has specified for the training process']]=None,
            project_id:Annotated[str,InjectedToolArg]=None,
            data_report:Annotated[str,InjectedToolArg]=None,
            ):
    """builds a ML model based on the user's query. The mode, and target featue are required. The exclude features and preferences are optional. If the user wants to predict, call the predictor tool. not this one."""
    print(f"Trainer IS BEING CALLED WITH mode: {mode}, target_feature: {target_feature}, exclude_features: {exclude_features}, preferences: {preferences}")    
    #TODO LATER ON USE DATA REPORT TO GET THE FEATURES rather than df
    df=await projectRequests.get_dataset(project_id)
    # Get all features from the dataframe
    all_features = df.columns.tolist()

    # Filter out the features to exclude, ignoring any that are not in the dataframe
    features_to_include = [feature for feature in all_features if feature not in (exclude_features or []) and feature != target_feature]

    # Log the features being included
    print(f"Features to include in training: {features_to_include}")

    # Call the automl pipeline with the filtered features
    training_response = automl(project_id=project_id,
                                    data_report=data_report,
                                    mode=mode,
                                    label=target_feature,
                                    features=features_to_include,
                                    user_preferences=preferences)
    
    finish=False
    async for word in training_response:
            
            if "{" not in word and not finish:
                 print("WORD:",word)
                #  writer({'status':word})
            else:
                finish=True
                eval_report=json.loads(word)
    model_eval=eval_report['evaluation_reports']
    return ['You Must Inform the user that the training has been completed, and if they want more information they can go to the autoML tab',model_eval]


@tool
async def predictor(project_id:Annotated[str,InjectedToolArg]=None):
    """"This function is used to make predictions or inferences based on an already trained model. It can be called without prior training and focuses solely on generating predictions. Use this when you want to make predictions using a pre-existing model.
    This function does not require any additional parameters, as it will use the project_id to fetch the necessary data and make predictions. If the user says that they want to predict then call this function. If the user wants to train a model, use the builder tool instead.
    The user does not need to provide any additional information, as the function will handle the prediction process internally. The function will return a message indicating that the model is ready for predictions and provide the necessary details for making predictions."""
    print("Predictor IS BEING CALLED")
    report=await projectRequests.get_model_report(project_id)
    if report:
        deployment_dict={"deployment":{}}
        for model in report['models']:
            deployment_dict["deployment"][list(model.keys())[0]]={'features':model['deployment'],'feature_columns':model['X_columns']}

        return ['You must inform the user that the model is ready for prediction, and they can find the form below',deployment_dict]
    else:
        return 'You MUST inform the user that they should train the model first before making predictions. You can suggest them to go to the AutoML tab and train the model or tell you to train one.'


    


tools = [visualizer,builder,predictor]


async def tool_node(state):
    tools_by_name = {tool.name: tool for tool in tools}
    
    messages = state["messages"]
    # get the last message of this state
    last_message = messages[-1]
    output_messages = []
    visual_results=[]
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["data_report"] = state["data_report"]
            tool_call['args']['project_id']=state['project_id']
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
    return {'messages':output_messages,'visual':visual_results if isinstance(visual_results,list) else [visual_results] }
