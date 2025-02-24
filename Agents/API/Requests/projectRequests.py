import requests
import pandas as pd
from io import StringIO
url="http://Backend:8005"

async def get_dataset(project_id):
    response = requests.get(url + f"/project/{project_id}/fetchDataset")
    dataset=response.json()['data']
    return pd.read_json(StringIO(dataset))