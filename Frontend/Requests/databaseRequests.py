import requests
import streamlit as st
import json
import pandas as pd
from io import StringIO

url = 'http://127.0.0.1:8000'
def check_login(username,password):
    """
    Validates user login credentials.

    Parameters
    ----------
    username : str
        The username to validate.
    password : str
        The password to validate.

    Returns
    -------
    str
        The login validation response.
    """
    response=requests.post(url+"/login",json={'username':username,'password':password})
    return response.json()['data']

def check_signup(first_name,last_name,email,username,password):
    """
    Registers a new user with the provided information.

    Parameters
    ----------
    first_name : str
        The first name of the user.
    last_name : str
        The last name of the user.
    email : str
        The email address of the user.
    username : str
        The username for the new account.
    password : str
        The password for the new account.

    Returns
    -------
    str
        The signup response.
    """
    response=requests.post(url+"/signup",json={'first_name':first_name,'last_name':last_name,
                                                                'email':email,'username':username,                                                           
                                                                'password':password})
    return response.json()['data']


def get_user_id(username):
    """
    Retrieves the user ID based on the provided username.

    Parameters
    ----------
    username : str
        The username to retrieve the ID for.

    Returns
    -------
    str
        The User ID
    """
    response=requests.get(url+f"/get_id/{username}")
    return response.json()['data']

def get_name(user_id):
    """
    Gets the first name of account with the given id.

    Parameters
    ----------
    user_id : str
        The user's id.
    

    Returns
    -------
    str
        First_NAME
    """
    response=requests.get(url+f"/get_name/{user_id}")
    return response.json()['data']


def create_project(user_id,name,uploaded_file):
        print(user_id,name)
        files = {"file": uploaded_file}
        data={
             'user_id': str(user_id),
             'name': name
        }

        # Send the POST request
        response = requests.post(url+'/createProject', files=files,data=data)

def read_projects(user_id):
     response=requests.get(url+f'/readProjects/{str(user_id)}')
     projects=json.loads(response.json())['data']
     return projects

def get_project_details(project_id):
     response=requests.get(url+f'/projectDetails/{str(project_id)}')
     project=json.loads(response.json())['data']
     return project


def fetch_dataset(project_id):
    response=requests.get(url+f'/fetchDataset/{str(project_id)}')
    df=pd.read_json(StringIO(response.json()['data']))
    return df

