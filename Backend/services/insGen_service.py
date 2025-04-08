import httpx
from config import *
import requests

class insGenService:
    def __init__(self):
        self.project_repository = ProjectRepository()
        self.project_service=ProjectService()
        self.url="http://Agents:8006/InsGen"
    
    async def get_description(self,project_id:str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.url}/project/{project_id}/description",
                    timeout=30.0  # Add timeout
                )
                response.raise_for_status()  # Raise for bad status codes
                
                result = response.json()
                 
                description = result[0].get("description")
                joined_description = f"""
                        Column Explanation:\n{description['col_explanation']}
                        Overview:\n{description['overview']}
                        Key Patterns:\n{description['key_patterns']}
                        Quality Issues:\n{description['qual_issues']}
                """
                
                return {
                    "description": joined_description,
                    "thread_id": result[1].get("thread_id"),
                }
                
                
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def accept_human_feedback(self,feedback:Feedback):
        return requests.post(f"{self.url}/description/feedback",json=feedback.model_dump(mode="json")).json()
