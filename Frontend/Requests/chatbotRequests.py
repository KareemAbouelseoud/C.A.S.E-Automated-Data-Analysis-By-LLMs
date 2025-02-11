import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json
url='http://127.0.0.1:8000'

def chat(prompt,project_id,messages=None):
    if messages:
        response=requests.post(url + "/chat", json={"prompt": prompt, 'messages': json.dumps(messages), 'project_id': project_id},stream=True)
    else:
        response=requests.post(url + "/chat", json={"prompt": prompt, 'project_id': project_id},stream=True)
        
    return response

def recommender(prompt,project_id):
    response=requests.post(url+"/recommend", json={"prompt": json.dumps(prompt),'project_id':project_id})
    return json.loads(response.json()['data'])



def get_model_history(project_id):
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
    response=requests.get(url+f"/get_model_history/{project_id}")
    return response.json()['data']

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

def update_user_st_history(project_id,last_conv):
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
    response=requests.post(url+"/update_user_st_history",json={'project_id':project_id,'last_conv':json.dumps(last_conv)})

    # print("CONV: ",last_conv)
    # requests.post(url+f"/update_st_history/{chat_id}",json={'conv':last_conv})


def clear_history(user_id):
    """
    Updates Streamlit chat history for a specific chat ID.

    Parameters
    ----------
    chat_id : str
        The chat ID to update history for.
    last_conv : str
        The last conversation to update.

    Returns
    -------
    None
    """
    requests.get(url+f"/clear_history/{user_id}")



