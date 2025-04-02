import requests
import pandas as pd
from io import StringIO
from joblib import Memory
url="http://localhost:8005"

# Create a memory cache in a temporary directory
memory = Memory(location='./.cache', verbose=0)

# Apply caching to the requests function
@memory.cache
async def get_dataset(project_id):
    response = requests.get(url + f"/project/{project_id}/fetchDataset")
    dataset=response.json()['data']
    return pd.read_json(StringIO(dataset))