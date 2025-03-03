import requests
import json
url="http://Backend:8005"

async def get_history(thread_id):
    response = requests.get(url + f"/project/{thread_id}/get_model_history")
    if response.json():
        return json.loads(response.json())['data']
    else:
        return None