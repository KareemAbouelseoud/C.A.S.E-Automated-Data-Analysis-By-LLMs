import requests
import json

url = 'http://Backend:8005/insGen'

def get_description(project_id):
    """
    Fetches the description for a specific project ID.
    
    Parameters
    ----------
    project_id : str
        The project ID to fetch the description for.

    """
    response = requests.get(f"{url}/project/{project_id}/description")
    if response.status_code == 200:
        
        result = json.loads(response.content)
        description = result.get("description")
        thread_id = result.get("thread_id")
        return description,thread_id
    else:
        print(f"Failed to fetch insights: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        return None

def fetch_insights(project_id):
    """
    Fetches insights for a specific project ID.
    
    Parameters
    ----------
    project_id : str
        The project ID to fetch insights for.

    Returns
    -------
    list
        A list of insights for the specified project ID.
    """
    #TODO: Uncomment the following lines to enable the API call.
    # response = requests.get()
    # if response.status_code == 200:
    #     return json.loads(response.json()['data'])
    # else:
    #     print(f"Failed to fetch insights: HTTP {response.status_code}")
    #     print(f"Response: {response.text}")
    #     return None

    file_path = 'static/response_1743535680381.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('feedback', [])[0]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None