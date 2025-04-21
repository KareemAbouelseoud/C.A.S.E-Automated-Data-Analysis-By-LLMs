import asyncio
from API.Requests import projectRequests
from API.Requests.projectRequests import get_dataset
from dotenv import load_dotenv
import asyncio
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
load_dotenv()
async def test():
    df = await get_dataset("1")
    print(f"Dataset type: {type(df)}")
    print(f"Data contents:\n{df}")

asyncio.run(test())