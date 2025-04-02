import httpx
import json
url="http://Backend:8005"

async def get_history(thread_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(url + f"/project/{thread_id}/get_model_history")
        if response.json():
            return json.loads(response.json())['data']
        else:
            return None