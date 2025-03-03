from vizGeneration import pipeline
import json
import pandas as pd
from io import StringIO

class vizService:

    async def createVisualizations(self,data_report,dataframe):
        df=pd.read_json(StringIO(dataframe))
        visualizations = await pipeline.generate_visualizations(data_report,df)
        visualizations = [ [v] if isinstance(v,dict) else v  for v in visualizations ]
        serializable_visualizations = [pipeline.make_serializable(v) for v in visualizations]
        return serializable_visualizations
    
        