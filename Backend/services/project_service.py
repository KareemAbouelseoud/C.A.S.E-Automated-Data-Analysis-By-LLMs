import azure.core
from config import *
import uuid
import asyncio

def get_repo():
    repo = ProjectRepository()
    return repo
class ProjectService:
    def __init__(self):
        self.project_repository = get_repo()
        self.userRepository = UserRepository()
        self.vizRepository= VisualizationRepository()
        self.connection_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_str)

    #region Project functions

    async def get_project(self, id: str) -> Optional[Project]:
        project=await self.project_repository.get_by_id(id)
        return project.model_dump()

    async def get_user_projects(self,userId:str) -> List[Project]:
        projects=await self.project_repository.Filter({"user_id":userId})
        return projects

    async def create_project(self,file:UploadFile = File(...), user_id: str = Form(...), name: str = Form(...)) -> Project:

        user = await self.userRepository.get_by_id(user_id)

        if user==None:
            raise HTTPException(status_code=400, detail="Invalid user_Id Please provide an existing user id.")
        # 1. Validate file type (ensure it's a CSV)
        if file.filename[-4:].lower().strip() != ".csv":
            raise HTTPException(status_code=500, detail="Invalid file type. Only CSV files are allowed.")
        # 2. Upload CSV to the BlobStorage
        try:
            container_client = self.blob_service_client.get_container_client("datasets")
            # Generate unique blob name
            # NOTE: Used user_id and current timestamp to ensure uniqueness as Project ID is not available yet
            blob_name = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            
            contents = await file.read()
            # Upload to blob storage
            blob_client = container_client.upload_blob(name=blob_name, data=contents)
            
            # Read the CSV content for processing
            
            dataframe = blob_client.url
            
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Uploading the csv to the blob storage: {e}")
        
        new_project = Project(name=name, user_id=user_id,Dataset=dataframe,created_Date=datetime.now())
        new_project.model_Chat=projectChat(last_update=datetime.now())
        new_project.streamlit_Chat=projectChat(last_update=datetime.now())
        ## BUG: The below code is for testing purposes only we will remove it later
       
        new_project.data_report = ""
        new_project.thread_id = str(uuid.uuid4())
        # 5.  Important: Save ٍProject to MongoDB
        try:       
            project = await self.project_repository.create(new_project)         
            if project:
                user.Projects.append(str(project.id))
                asyncio.create_task(self.userRepository.update(user_id, user))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating project and data to MongoDB: {e}")
        try:
            asyncio.create_task(self.vizRepository.create(str(project.id), user_id=user_id))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating project visualization and data to MongoDB: {e}")

        return project.model_dump(mode="json")
        

    async def update_project(self, id: str, project: Project) -> bool:
        return await self.project_repository.update(id, project)
    
    async def delete_project(self, id: str) -> bool:
        return await self.project_repository.delete(id)
    #endregion
    
    #region Chat Functions

    async def clearChatHistory(self, project_id: str,user_id:str) -> str:
        try:
            user, project_data, project_viz = await asyncio.gather(
            self.userRepository.get_by_id(user_id),
            self.get_project(project_id),
            self.vizRepository.get_by_project_id(project_id)
            )
            project = Project.from_dict(project_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving data from MongoDB: {e}")
        
        
        project.model_Chat=projectChat(last_update=datetime.now())
        project.streamlit_Chat=projectChat(last_update=datetime.now())
        project_viz.Chat_visualizations=[]
        project.thread_id=str(uuid.uuid4())

        try:
            asyncio.gather(
                 self.project_repository.update(project_id, project),
                 self.vizRepository.update(project_id, project_viz)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating project and visualization data in MongoDB: {e}")
        return project.thread_id
    
    async def updateChatHistory(self, project_id: str, user_id:str,last_conv:list) -> bool:
        try:
            user, project_data = await asyncio.gather(
            self.userRepository.get_by_id(user_id),
            self.get_project(project_id)
            )
            project = Project.from_dict(project_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving data from MongoDB: {e}")
            
        if user==None:
            raise HTTPException(status_code=400, detail="Invalid user_Id Please provide an existing user id.")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        hist_dict={'st_history':[],'model_history':[]}
        for i,message in enumerate(last_conv):
            hist_dict['st_history'].append({'role':message['role'],'content':message['content']})
            if i==0:
                continue
            if 'visualizer'!=message['role']:
                hist_dict['model_history'].append({'role':message['role'],'content':message['content']})
        project.model_Chat=projectChat()
        project.streamlit_Chat=projectChat()
        project.model_Chat.messages=json.dumps(hist_dict['model_history'])
        project.streamlit_Chat.messages=json.dumps(hist_dict['st_history'])
        
        project.model_Chat.last_update=datetime.now()
        project.streamlit_Chat.last_update=datetime.now()
        
        try:
            asyncio.create_task(self.project_repository.update(project.id, project))
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project's chat to MongoDB: {e}")
    
    async def get_model_chat_history(self, thread_id: str) -> Optional[List[str]]:
        try:
            project = await self.project_repository.get_by_thread_id(thread_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
        if project==[]:
            return []
        return [project.model_Chat.messages if project.model_Chat.messages else [],project.data_report,str(project.id)]
    
    async def get_streamlit_chat_history(self, project_id: str) -> Optional[Project]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        if project.streamlit_Chat.messages==None:
            return '[]'
        return project.streamlit_Chat.messages
    #endregion

    #region other fetches
    async def fetch_data_report(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        return project.data_report
    
    async def fetch_dataset(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        datasetUrl=f"{project.Dataset}{os.environ.get('AZURE_STORAGE_SAS_TOKEN')}"
        # print(datasetUrl)
        return pd.read_csv(datasetUrl)

    async def fetch_thread_id(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        return project.thread_id
    #endregion

    #region AutoML
    async def save_model_report(self, project_id: str, report: dict) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id)
            if project is None:
                raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
            
            container_client = self.blob_service_client.get_container_client("model-reports")
            blob_name = f"{project_id}_model_report.json"

            try:
                # Ensure report is properly formatted JSON
                report_json = json.loads(json.dumps(report))  # ✅ Validate JSON
                formatted_report = json.dumps(report_json, indent=4)
                report_bytes = formatted_report.encode('utf-8')

                # Upload to blob storage
                container_client.upload_blob(name=blob_name, data=report_bytes, overwrite=True)
                return True

            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON report: {e}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading model report to blob storage: {str(e)}")
    
    async def fetch_model_report(self, project_id: str) -> Optional[str]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrieving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")

        model_report=f"{project_id}_model_report.json"

        blob_client=self.blob_service_client.get_blob_client(container="model-reports", blob=model_report)
        try:
            model_report = blob_client.download_blob().readall().decode('utf-8')
        except azure.core.exceptions.ResourceNotFoundError:
            # Return None if the blob doesn't exist
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading model report from blob storage: {str(e)}")
        return model_report
    
    async def save_preprocessing_pipeline(self, project_id: str,pipeline_type:str ='X',contents=None )-> bool:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        container_client = self.blob_service_client.get_container_client("pipelines")
        # Generate unique blob name
        if pipeline_type=='X':
            blob_name = f"{project_id}_Xpreprocessing_pipeline.pkl"
        else:
            blob_name = f"{project_id}_Ypreprocessing_pipeline.pkl"
        try:
            # Upload to blob storage
            blob_client = container_client.upload_blob(name=blob_name, data=contents, overwrite=True)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error uploading Xpreprocessing pipeline to blob storage.")
        return True

    async def fetch_pipeline(self,project_id: str,pipeline_type:str ='X'):
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
            
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        #TODO: Fetch pipelines according to models for now we only have one
        if pipeline_type=='X':
            blob_name = f"{project_id}_Xpreprocessing_pipeline.pkl"
        else:
            blob_name = f"{project_id}_Ypreprocessing_pipeline.pkl"
        blob_client = self.blob_service_client.get_blob_client(container="pipelines", blob=blob_name)

        try:
            pipeline = blob_client.download_blob().readall()
            return pipeline
        except azure.core.exceptions.ResourceNotFoundError:
            # Return None if the blob doesn't exist
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading pipeline from blob storage: {str(e)}")

    async def save_model(self, project_id: str, contents=None, model_name=str )-> Optional[bool]:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrving project from MongoDB: {e}")
        
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        container_client = self.blob_service_client.get_container_client("models")
        # Generate unique blob name
        blob_name = f"{project_id}_{model_name}_model.pkl"
        try:
            # Upload to blob storage
            blob_client = container_client.upload_blob(name=blob_name, data=contents, overwrite=True)
            
        except:
            raise HTTPException(status_code=500, detail="Error uploading model to blob storage.")
        
        return True
    
    async def fetch_model(self, project_id: str, model_name: str):
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrieving project from MongoDB: {e}")
            
        if project == None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        
        blob_name = f"{project_id}_{model_name}_model.pkl"
        blob_client = self.blob_service_client.get_blob_client(container="models", blob=blob_name)

        try:
            model = blob_client.download_blob().readall()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading model from blob storage: {e}")
        
        return model
    
    async def delete_automl_data(self, project_id: str) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrieving project from MongoDB: {e}")
            
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
        
        delete_tasks = []

        # Delete model report
        try:
            report_blob_name = f"{project_id}_model_report.json"
            report_blob_client = self.blob_service_client.get_blob_client(container="model-reports", blob=report_blob_name)
            delete_tasks.append(asyncio.to_thread(report_blob_client.delete_blob, delete_snapshots="include"))
        except azure.core.exceptions.ResourceNotFoundError:
            # If the blob doesn't exist, continue without error
            pass
        except Exception as e:
            print(f"Warning: Failed to delete model report: {e}")

        # Delete X and Y preprocessing pipelines
        for pipeline_type in ['X', 'Y']:
            try:
                pipeline_blob_name = f"{project_id}_{pipeline_type}preprocessing_pipeline.pkl"
                pipeline_blob_client = self.blob_service_client.get_blob_client(container="pipelines", blob=pipeline_blob_name)
                delete_tasks.append(asyncio.to_thread(pipeline_blob_client.delete_blob, delete_snapshots="include"))
            except azure.core.exceptions.ResourceNotFoundError:
                # If the blob doesn't exist, continue without error
                pass
            except Exception as e:
                print(f"Warning: Failed to delete {pipeline_type} pipeline: {e}")

        # Delete all models - get list of models first then delete
        try:
            container_client = self.blob_service_client.get_container_client("models")
            model_prefix = f"{project_id}_"
            
            # List all blobs with the project ID prefix
            model_blobs = container_client.list_blobs(name_starts_with=model_prefix)
            
            # Delete each model blob
            for blob in model_blobs:
                blob_client = self.blob_service_client.get_blob_client(container="models", blob=blob.name)
                delete_tasks.append(asyncio.to_thread(blob_client.delete_blob, delete_snapshots="include"))
        except Exception as e:
            print(f"Warning: Failed to delete models: {e}")

        # Run all delete tasks in parallel
        await asyncio.gather(*delete_tasks,return_exceptions=True)
        return True
    #endregion

    