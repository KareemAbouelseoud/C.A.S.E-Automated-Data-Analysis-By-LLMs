# first line: 11
@memory.cache
async def get_dataset(project_id):
    response = requests.get(url + f"/project/{project_id}/fetchDataset")
    dataset=response.json()['data']
    return pd.read_json(StringIO(dataset))