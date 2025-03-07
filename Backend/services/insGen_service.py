from config import *
import requests

class insGenService:
    def __init__(self):
        self.project_repository = ProjectRepository()
        self.project_service=ProjectService()
        self.url="http://Agents:8006/InsGen"
    
    async def get_description(self):
        return requests.get(f"{self.url}/description").json()
    
    async def accept_human_feedback(self,feedback:Feedback):
        return requests.post(f"{self.url}/description/feedback",json=feedback.model_dump(mode="json")).json()
