import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from .visualizationRequests import fetch_chat_visualizations
import requests
import json
import copy
url='http://Backend:8005'

def chat(prompt,project_id,thread_id):
    
    response=requests.post(url + "/chat", json={"prompt": prompt,'project_id': project_id,'thread_id':thread_id},stream=True)    
    return response

def recommender(prompt,project_id,thread_id):
    response=requests.post(url+"/recommend", json={"prompt": json.dumps(prompt),'project_id':project_id,'thread_id':thread_id})
    ## This is the response and it is a dict like that => {'data': '["Summarize data", "Show correlations", "Find outliers"]'}
    return eval(response.json()['data'])



def get_streamlit_chat_history(project_id):
    """
    Retrieves Streamlit chat history for a specific chat ID.

    Parameters
    ----------
    project_id : str
        The chat ID to retrieve history for.

    Returns
    -------
    list
        The Streamlit chat history.
    """
    response=requests.get(url+f"/project/{project_id}/get_streamlit_history")
    chat_viz=fetch_chat_visualizations(project_id)
    streamlit_chat=eval(response.json()['data'])
    for message in streamlit_chat:
        if message['role']=='visualizer':
            message['content']=chat_viz[int(message['content'])]
            
    return streamlit_chat

def create_new_chat(user_id):
    """
    Creates a new chat session for the given user ID.

    Parameters
    ----------
    user_id : str
        The user ID to create a new chat for.
    Returns
    -------
    Response
        The response from the backend service.
    """
    response=requests.get(url+f"/create_new_chat/{user_id}")
    return response

def update_user_st_history(project_id,last_conv,user_id):
    """
    Updates Streamlit chat history for a specific chat ID.

    Parameters
    ----------
    project_id : str
        The chat ID to update history for.
    last_conv : str
        The last conversation to update.

    Returns
    -------
    None
    """
    ## FIXME: This is a temporary fix to update the Chat including visualizations
    viz_count=0
    last_conv_copy = copy.deepcopy(last_conv)

    for i,message in enumerate(last_conv_copy):
            if message['role']=='visualizer':
                message['content']=viz_count
                viz_count+=1
    
    response=requests.post(url+f"/project/{project_id}/chat_streamlit/?user_id={user_id}",json={'project_id':project_id,'last_conv':json.dumps(last_conv_copy)})


def clear_history(project_id,user_id):
    """
    Clear chat history for a specific chat ID.

    Parameters
    ----------
    Project_id: str
        The chat ID to update history for.
    last_conv : str
        The last conversation to update.

    Returns
    -------
    None
    """
    response=requests.get(url+f"/project/{project_id}/chat/clear?user_id={user_id}")
    return response.json()['data']



