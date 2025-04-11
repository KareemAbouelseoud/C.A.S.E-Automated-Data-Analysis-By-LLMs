import asyncio
import multiprocessing as mp
import httpx
from config import *
import requests

class insGenService:
    def __init__(self):
        self.project_repository = ProjectRepository()
        self.project_service=ProjectService()
        self.url="http://Agents:8006/InsGen"
        self.connection_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_str)
    def extract_description_sections(self,text):
        """Extracts structured information from text by splitting it into predefined sections.

        This function parses a text string and splits it into sections based on predefined
        section headers. It's particularly useful for processing structured documentation
        or text with known section markers.

        Args:
            text (str): The input text to be processed.

        Returns:
            dict: A dictionary where keys are section names (without colons) and values
                are the corresponding section contents. If no predefined sections are
                found, returns a dictionary with a single 'text' key containing the
                original text. Any content not belonging to predefined sections is
                stored under 'other_info'.

        Example:
            >>> text = '''
                Overview:
                This is an overview.
                Key Patterns:
                These are patterns.
                '''
            >>> extract_description_sections(text)
            {'Overview': 'This is an overview.', 'Key Patterns': 'These are patterns.'}
        """
        # Split the text into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Define the important sections we want to capture
        important_sections = ["Column Explanation:", "Overview:", "Key Patterns:", "Quality Issues:"]
        
        # If none of the important sections are in the text, return the text as is
        if not any(section in text for section in important_sections):
            return {'text': text.strip()}
        
        # Initialize dictionary and current section
        sections = {}
        current_section = None
        current_content = []
        other_content = []
        
        for line in lines:
            if line in important_sections:
                # If we were processing a previous section, save it
                if current_section is not None:
                    if current_section in important_sections:
                        sections[current_section.rstrip(':')] = '\n'.join(current_content).strip()
                    else:
                        other_content.extend(current_content)
                    current_content = []
                current_section = line
            else:
                current_content.append(line)
        
        # Don't forget to add the last section
        if current_section is not None:
            if current_section in important_sections:
                sections[current_section.rstrip(':')] = '\n'.join(current_content).strip()
            else:
                other_content.extend(current_content)
        
        # If there's any content not belonging to important sections, add it to other_info
        if other_content:
            sections['other_info'] = '\n'.join(other_content).strip()
        
        return sections
    
    async def update_project(self, project_id: str, updated_description: dict,description_confirmed:bool=False,report:dict=None):
            """Updates the project description in the database.
            This is now designed to be called as a background task.
            """
            try:
                # Fetch project
                project = await self.project_repository.get_by_id(project_id)

                if project is None:
                    print(f"Project with id '{project_id}' not found.")
                    return # Or raise an exception if not found

                # Update project attributes
                project.dataset_description = updated_description
                project.created_Date = datetime.strptime(project.created_Date,"%d %B %Y")
                project.model_Chat.last_update = datetime.strptime(project.model_Chat.last_update,"%d %B %Y")
                project.streamlit_Chat.last_update = datetime.strptime(project.streamlit_Chat.last_update,"%d %B %Y")
                
                project.description_confirmed = description_confirmed
                if report:
                    project.data_report=await self.save_report(project_id, report) 
                elif description_confirmed:
                    report=f"{project_id}_Raw_report.json"

                    blob_client=self.blob_service_client.get_blob_client(container="reports", blob=report)
                    try:
                        report = json.loads(blob_client.download_blob().readall().decode('utf-8'))
                        
                        report["dataset_description"] = updated_description["description"]
                        project.data_report=await self.save_report(project_id, report) 
                    except azure.core.exceptions.ResourceNotFoundError:
                        # Return None if the blob doesn't exist
                        return None
                # Persist changes to database
                updated_project = await self.project_repository.update(project_id, project)

                if not updated_project:
                    print(f"Failed to update project with id '{project_id}'.")

            except Exception as e:
                print(f"Error updating project '{project_id}': {e}")
             
    async def save_report(self, project_id: str, report: dict):
        description = report.get("dataset_description")
        if type(description)== dict:
            
            joined_description = f"""
            **1. Column Explanations:**\n{description['col_explanation']}\n
            **2. Dataset Overview:**\n{description['overview']}\n
            **3. Key Patterns in Data Distribution (Based on the Snippet and General Knowledge):**\n{description['key_patterns']}\n
            **4. Notable Data Quality Issues:**\n{description['qual_issues']}
            """
            report["dataset_description"] = joined_description
        
        container_client = self.blob_service_client.get_container_client("reports")
        blob_name = f"{project_id}_Raw_report.json"

        try:
            # Ensure report is properly formatted JSON
            report_json = json.loads(json.dumps(report))  # ✅ Validate JSON
            formatted_report = json.dumps(report_json, indent=4)
            report_bytes = formatted_report.encode('utf-8')

            # Upload to blob storage
            blob_client= container_client.upload_blob(name=blob_name, data=report_bytes, overwrite=True)
            return blob_client.url  # Return the URL of the uploaded blob

        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON report: {e}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading model report to blob storage: {str(e)}")  

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
                _responseFrontend={
                    "description": joined_description.replace("*", ""),
                    "thread_id": result[1].get("thread_id"),
                    "feedback": [],
                }
                asyncio.create_task(self.update_project(project_id, _responseFrontend,False,result[0].get("report")))
                
                return _responseFrontend
                
                
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    async def contact_feedbackEndpoint(self,feedback:Feedback):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/description/feedback",
                timeout=None,
                json=feedback.model_dump(mode="json")  # Add timeout

            )
            response.raise_for_status()  # Raise for bad status codes
            return response.json()
        
    async def  get_updated_description(self,feedback:Feedback):
        try:
            result = await self.contact_feedbackEndpoint(feedback)
                        
            description = result[0].get("description")
            joined_description = f"""
            Column Explanation:\n{description['col_explanation']}
            Overview:\n{description['overview']}
            Key Patterns:\n{description['key_patterns']}
            Quality Issues:\n{description['qual_issues']}
            """
            asyncio.create_task(self.save_report(feedback.project_id, result[0].get("report")))
            _responseFrontend={
            "description": joined_description.replace("*", ""),
            "thread_id": result[1].get("thread_id"),
            "feedback_history": feedback.feedback,
            }
            return _responseFrontend
        except httpx.RequestError as e:
            return {
                "description": "",
                "thread_id": "",
                }
    
    async def accept_human_feedback(self,_feedback:Feedback):
        # return requests.post().json()
        try:
            if _feedback.feedback[-1] != "done":
                _responseFrontend = await self.get_updated_description(_feedback)
                asyncio.create_task(self.update_project(_feedback.project_id, _responseFrontend))
                
                return _responseFrontend
            else:
                current_state={
                "description": _feedback.description,
                "thread_id": _feedback.thread_id,
                "feedback_history": _feedback.feedback,
                }
                asyncio.create_task(self.update_project(_feedback.project_id, current_state, True))
                asyncio.create_task(self.contact_feedbackEndpoint(_feedback))    
                return current_state
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    async def save_Insights(self,Insights:SaveInsights, project_id:str):
        
        container_client = self.blob_service_client.get_container_client("insights")
        blob_name = f"{project_id}_Insights.json"

        try:
            # Ensure report is properly formatted JSON
            insights_json = Insights.model_dump(mode="json")
            formatted_report = json.dumps(insights_json, indent=4)
            report_bytes = formatted_report.encode('utf-8')

            # Upload to blob storage
            blob_client= container_client.upload_blob(name=blob_name, data=report_bytes, overwrite=True)
            return blob_client.url  # Return the URL of the uploaded blob

        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON report: {e}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading model report to blob storage: {str(e)}")  
            
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise