# first line: 15
@memory.cache
async def get_dataset(project_id):
    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url + f"/project/{project_id}/fetchDataset")
            except Exception as e:
                print("Error in fetching dataset from backend:", e)
                response = await client.get(f"http://localhost:8005/project/{project_id}/fetchDataset")
        dataset = json.loads(response.json()["data"])
    except Exception as e:
        print(f"Error fetching dataset: {e}")
        raise e
        return None
    return pd.DataFrame(dataset)
