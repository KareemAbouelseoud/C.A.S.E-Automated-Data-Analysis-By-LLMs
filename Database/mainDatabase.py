import pandas as pd
from datetime import datetime
import bcrypt
import shutil
import csv
import os
import json
from joblib import dump
from joblib import load

user_directory=r'Database\Users\users.csv' #temp until we create a real database
project_directory=r'Database\Projects\projects.csv' #temp until we create a real database
raw_datasets_directory=r'Database\rawDatasets'
processed_datasets_directory=r'Database\processedDatasets'
data_reports_directory=r'Database\dataReports'
chat_directory=r'Database\Users\Chats.csv'
preprocessor_pipelines_directory=r'Database\preprocessorPipelines'
def check_login(username,password):
    df=pd.read_csv(user_directory)
    row=df[(df['username'] == username)]
    if row.shape[0] > 0:
        return bcrypt.checkpw(password.encode(), row.password.values[0].encode())
    
def get_user_id(username):
    df=pd.read_csv(user_directory)

    return str(df[df['username']==username]['user_id'].values[0])


def delete_user(user_id):
    df=pd.read_csv(user_directory)
    # Drop rows where the 'user_id' column is equal to user_id
    df = df[df['user_id'] != user_id]
    df.to_csv(user_directory,index=False)

def change_user_data(user_id,email,first_name,last_name,username,password):
    df=pd.read_csv(user_directory)
    df.loc[df['user_id'] == user_id, ['email', 'first_name','last_name','username','password']]\
    = [email,first_name,last_name,username,password]
    df.to_csv(user_directory,index=False)

def add_user(email, first_name, last_name, username, password):
    df=pd.read_csv(user_directory)
    if len(df)>0:
        ID=int(df.user_id.tail(1).values[0])+1
    else:
        ID=1
    with open(user_directory, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ID,email,first_name,last_name,username,password]) 

def username_exist(username):
    df=pd.read_csv(user_directory)
    return df[(df['username'] == username)].shape[0] > 0

def email_exist(email):
    df=pd.read_csv(user_directory)
    return df[(df['email'] == email)].shape[0] > 0

def signup(email, first_name, last_name, username, password):
    if email_exist(email):
        return "Email already exists."
    elif username_exist(username):
        return "Username already exists."
    else:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        add_user(email,first_name,last_name,username,hashed_password)
        return "Signup successful!"

def fetch_name(user_id):
    df=pd.read_csv(user_directory)
    return df[df['user_id'].astype(str)==user_id]['first_name'].values[0]

def fetch_username(user_id):
    df=pd.read_csv(user_directory)
    return df[df['user_id'].astype(str)==str(user_id)]['username'].values[0]

def fetch_email(user_id):
    df=pd.read_csv(user_directory)
    return df[df['user_id'].astype(str)==user_id]['email'].values[0]

def create_project(name,user_id,uploaded_file):
    df=pd.read_csv(project_directory)
    if len(df)>0:
        ID=int(df.project_id.tail(1).values[0])+1
    else:
        ID=1
    current_date = datetime.now().strftime("%d-%m-%Y")

    with open(project_directory, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ID,user_id,name,current_date])
    
    file_path = raw_datasets_directory+f"raw_dataset_{ID}.csv"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)    

def read_projects(user_id):
    df = pd.read_csv(project_directory)
    user_projects = df[df['user_id'].astype(str) == str(user_id)]
    
    projects_dict = {}
    for _, row in user_projects.iterrows():
        projects_dict[row['project_id']] = {
            'name': row['name'],
            'date': row['date']
        }
    
    return projects_dict


def get_project(project_id):
    # Read project details from the project directory
    df = pd.read_csv(project_directory)
    project = df[df['project_id'].astype(str) == str(project_id)].iloc[0]
    project_details = {
        'name': project['name'],
        'date': project['date']
    }
    
    # Get raw dataset
    raw_dataset_path = os.path.join(raw_datasets_directory, f"raw_dataset_{project_id}.csv")
    if os.path.exists(raw_dataset_path):
        raw_dataset = pd.read_csv(raw_dataset_path)
        project_details['raw_dataset'] = raw_dataset.to_json()
    else:
        project_details['raw_dataset'] = None
    
    # Get processed dataset
    processed_dataset_path = os.path.join(processed_datasets_directory, f"processed_dataset_{project_id}.csv")
    if os.path.exists(processed_dataset_path):
        processed_dataset = pd.read_csv(processed_dataset_path)
        project_details['processed_dataset'] = processed_dataset.to_json()
    else:
        project_details['processed_dataset'] = None
    
    return project_details


def fetch_dataset(project_id):
    raw_dataset_path = raw_datasets_directory+r"\raw_dataset_{}.csv".format(project_id)
    if os.path.exists(raw_dataset_path):
        raw_dataset = pd.read_csv(raw_dataset_path)
        return raw_dataset
    else:
        return None

def fetch_data_report(project_id):
    raw_data_report_path = data_reports_directory+r"\data_report_{}.json".format(project_id)
    if os.path.exists(raw_data_report_path):
        with open(raw_data_report_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
            json_string = json.dumps(json_content)
            return json_string
    else:
        return None

def create_new_chat_id(project_id):
    with open(chat_directory, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([project_id])

def clear_history(project_id):
    df=pd.read_csv(chat_directory)
    df_filtered = df[df['project_id'].astype(str)!=str(project_id)]
    df_filtered.to_csv(chat_directory,index=False)

def get_model_chat_history(project_id):
    df=pd.read_csv(chat_directory)
    if df[df['project_id'].astype(int)==int(project_id)]['st_history'] is not None:
        try:
            return json.loads(df[df['project_id'].astype(int)==int(project_id)]['st_history'].values[0])
        except:
            return []

def update_st_chat_history(project_id,last_conv : list):
    df=pd.read_csv(chat_directory)
    hist_dict={'st_history':[],'model_history':[]}
    for message in last_conv:
        hist_dict['st_history'].append({'role':message['role'],'content':message['content']})
        if 'visualizer'!=message['role']:
            hist_dict['model_history'].append({'role':message['role'],'content':message['content']})

    project_index = df[df['project_id'].astype(str) == project_id].index
    if not project_index.empty:
        df.at[project_index[0], 'st_history'] = json.dumps(hist_dict['st_history'])
        df.at[project_index[0], 'model_history'] = json.dumps(hist_dict['model_history'])
        df.at[project_index[0], 'last_date'] = datetime.now()
    else:
        # Handle the case where the project_id is not found
        print(f"Project ID {project_id} not found in chat history.")

    df.to_csv(chat_directory, index=False)

def save_pipeline(pipeline, project_id):
    pipeline_path = os.path.join(preprocessor_pipelines_directory, f"pipeline_{project_id}.joblib")
    dump(pipeline, pipeline_path)

def fetch_pipeline(project_id):
    pipeline_path = os.path.join(preprocessor_pipelines_directory, f"pipeline_{project_id}.joblib")
    if os.path.exists(pipeline_path):
        return load(pipeline_path)
    else:
        return None
