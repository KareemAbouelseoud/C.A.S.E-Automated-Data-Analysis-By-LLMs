from vizGeneration.mainTools import make_serializable
from vizGeneration import pipeline
class vizService:

    async def createVisualizations(self,data_report,project_id):
        visualizations = await pipeline.generate_visualizations(data_report,project_id)
        visualizations = [ [v] if isinstance(v,dict) else v  for v in visualizations ]
        serializable_visualizations = [make_serializable(v) for v in visualizations]
        return serializable_visualizations
    
        