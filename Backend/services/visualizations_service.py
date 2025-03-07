from config import *
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go
import numpy as np

def get_repo():
    repo = VisualizationRepository()
    return repo
class visualizationsService:
    def __init__(self):
        self.viz_repository = get_repo()
        self.project_repository = ProjectRepository()
        self.project_service=ProjectService()
        self.url="http://Agents:8006"

    
    #region Vizualizations Get functions
    
    async def get_project_Visualizations(self, project_id: str) -> Optional[visualizations]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")

        return project_Visualizations.model_dump()

    async def get_Auto_Gen_Viz(self,project_id:str) -> List[str]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        return project_Visualizations.Auto_generated_viz
    
    async def get_Chat_Viz(self,project_id:str) -> List[str]:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        return project_Visualizations.Chat_visualizations
    #endregion    
    
    #region Vizualizations Update functions
    
    async def update_Chat_Viz(self, project_id: str, new_viz: ChatViz) -> bool:
        if new_viz==None:
            raise HTTPException(status_code=500, detail=f"Can not insert a None Visualization into MongoDB: {e}")
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Chat_visualizations.append(new_viz.viz)
        try:
            return await self.viz_repository.update(project_id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    
    async def update_Auto_Gen_Viz(self, project_id: str) -> Tuple[bool, List[str]]:
        try:
            data_report=await self.project_service.fetch_data_report(project_id)

            response=requests.post(f"{self.url}/visualizations/createDashboard",json={'data_report':data_report,'project_id':project_id})
            serializable_visualizations=json.loads(response.json())['visualizations']
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error from Agents Module: {e}")
        
        print("THIS IS SERIALIZABLE VISUALIZATION IN VIZ SERVICE",len(serializable_visualizations))
        print("THIS IS SERIALIZABLE VISUALIZATION IN VIZ SERVICE",type(serializable_visualizations))
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Auto_generated_viz=serializable_visualizations
        try:
            return (await self.viz_repository.update(project_id, project_Visualizations),serializable_visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    #endregion
    
    #region Vizualizations Clear functions
    async def clear_Auto_Gen_Viz(self, project_id: str) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Auto_generated_viz=[]
        try:
            return await self.viz_repository.update(id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    
    async def clear_Chat_Viz(self, project_id: str) -> bool:
        try:
            project = await self.project_repository.get_by_id(project_id) 
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project==None:
            raise HTTPException(status_code=400, detail="Invalid project_id Please provide an existing Project id.")
        try:
            project_Visualizations=await self.viz_repository.get_by_project_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project Visualizations and data to MongoDB: {e}")
        project_Visualizations.Chat_visualizations=[]
        try:
            return await self.viz_repository.update(id, project_Visualizations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Updating project Visualizations and data to MongoDB: {e}")
    #endregion

    #region Vizualizations Dataset Creation functions
    async def plot_column_types(self, project_id: str) -> str:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
        
        try:
            dataframe = await self.project_service.fetch_dataset(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dataset: {e}")
        
            # Get data types and count them
        dtypes = dataframe.dtypes.astype(str)
        dtype_counts = dtypes.value_counts().reset_index()
        dtype_counts.columns = ['Data Type', 'Count']

        # Create the histogram
        fig = px.bar(
            dtype_counts,
            x='Data Type',
            y='Count',
            title='Distribution of Column Data Types',
            text_auto=True,
            color='Data Type',
            labels={'Count': 'Number of Columns', 'Data Type': 'Data Type'}
        )

        fig.update_layout(
            xaxis_title='Data Type',
            yaxis_title='Number of Columns',
            plot_bgcolor='rgba(0,0,0,0.05)',
            font=dict(size=12)
        )
        
        # Return the figure as JSON
        return make_serializable(fig.to_json())

    async def plot_missing_column(self, project_id: str, column_name: str, plot_type: str = 'Pie Chart') -> str:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
        
        try:
            dataframe = await self.project_service.fetch_dataset(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dataset: {e}")
            
        # Get the column
        column = dataframe[column_name]

        # Get the missing values
        missing_values = column.isnull().sum()
        present_values = column.count()
        missing_percentage = round((missing_values / (missing_values + present_values)) * 100, 2)
        present_percentage = 100 - missing_percentage

        # Create the plot
        if plot_type == 'Pie Chart':
            fig = px.pie(
                values=[missing_percentage, present_percentage],
                names=['Missing', 'Present'],
                title=f'Missing Values in {column_name}',
                labels={'value': 'Percentage', 'names': 'Status'}
            )
        elif plot_type == 'Bar Chart':
            fig = px.bar(
                x=['Missing', 'Present'],
                y=[missing_percentage, present_percentage],
                title=f'Missing Values in {column_name}',
                labels={'y': 'Percentage', 'x': 'Status'}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid plot type. Please provide either 'pie' or 'bar'.")
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0.05)',
            font=dict(size=12)
        )

        # Return the figure as JSON
        return make_serializable(fig.to_json())


    async def plot_distribution(self, project_id: str, column_name: str, plot_type: str = 'Histogram') -> str:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
        
        try:
            dataframe = await self.project_service.fetch_dataset(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dataset: {e}")
        
        # Get the column
        column = dataframe[column_name]
        
        # Create the plot
        if plot_type == 'Histogram' or plot_type == 'Bar Chart':
            fig = px.histogram(
                column,
                title=f'Distribution of {column_name}',
                labels={'value': 'Value', 'count': 'Frequency'}
            )
        elif plot_type == 'Box Plot':
            fig = px.box(
                column,
                title=f'Distribution of {column_name}',
                labels={'value': 'Value'}
            )
        elif plot_type == 'Violin Plot':
            fig = px.violin(
                column,
                title=f'Distribution of {column_name}',
                labels={'value': 'Value'}
            )
        elif plot_type == 'Pie Chart':
            # Count the frequency of each value
            value_counts = column.value_counts().reset_index()
            value_counts.columns = ['category', 'count']
            
            # Create the pie chart
            fig = px.pie(
                value_counts,
                values='count',
                names='category',
                title=f'Distribution of {column_name}',
                hole=0.3  # Optional: makes it a donut chart
            )
    
            # Add percentage to hover information
            fig.update_traces(
                textinfo='percent+label', 
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
            )

        elif plot_type == 'Density Plot':
            fig = px.density_contour(
                column,
                title=f'Distribution of {column_name}',
                labels={'value': 'Value'}
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid plot type.")
        

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0.05)',
            font=dict(size=12)
        )

        # Return the figure as JSON
        return make_serializable(fig.to_json())
        
    async def plot_top_n(self, project_id: str, column_name: str,plot_type='Words') -> str:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retriving project from MongoDB: {e}")
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")
        
        try:
            dataframe = await self.project_service.fetch_dataset(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dataset: {e}")
        
        # Get the column
        column = dataframe[column_name]

        # Get the top 10 most common words (max)
        if plot_type == 'Word Frequency':
            top_n = 10
            words = column.str.split(expand=True).stack().value_counts().head(top_n)

            # Create the plot
            fig = px.bar(
                words,
                x=words.index,
                y=words.values,
                title=f'Top {top_n} Words in {column_name}',
                labels={'x': 'Word', 'y': 'Frequency'}
            )
            
        else:
            # Characters
            top_n = 10
            # Concatenate all strings and then explode into individual characters
            all_text = ''.join(column.dropna().astype(str))
            # Filter out whitespace characters and get character frequency
            chars = pd.Series(list(all_text)).replace(' ', 'Space').value_counts().head(top_n)
            

            # Create the plot
            fig = px.bar(
                chars,
                x=chars.index,
                y=chars.values,
                title=f'Top {top_n} Characters in {column_name}',
                labels={'x': 'Character', 'y': 'Frequency'}
            )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0.05)',
            font=dict(size=12),
            xaxis=dict(tickangle=45)  # Rotate x-axis labels 45 degrees
        )
        # Return the figure as JSON
        return make_serializable(fig.to_json())

    async def plot_word_cloud(self,project_id: str, column_name: str) -> str:
        try:
            project = await self.project_repository.get_by_id(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error Retrieving project from MongoDB: {e}")
        if project is None:
            raise HTTPException(status_code=400, detail="Invalid project_id. Please provide an existing Project id.")

        try:
            dataframe = await self.project_service.fetch_dataset(project_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching dataset: {e}")

        # Get the column
        column = dataframe[column_name]
        # Combine all text into one string
        text = ' '.join(column.dropna().astype(str))
        
        # Generate the word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='black',
            colormap='viridis',
            max_words=100
        ).generate(text)
        
        # Convert the word cloud to an image
        img_bytes = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(img_bytes, format='png')
        plt.close()
        img_bytes.seek(0)
        
        # Convert to base64 for Plotly
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('ascii')
        
        # Create a Plotly figure with the image using base64 encoding
        fig = go.Figure()
        
        fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{img_base64}',
                xref="paper", yref="paper",
                x=0, y=1,
                sizex=1, sizey=1,
                sizing="stretch",
                layer="below"
            )
        )
        
        fig.update_layout(
            title=f'Word Cloud for {column_name}',
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            width=800,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        # For testing in the playground
        fig.show()
        
        # For your service
        return fig.to_json()
    #endregion

    