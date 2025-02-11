import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
from langchain import hub

CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-1.5-flash",
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

rec_sys=hub.pull("recommender").messages[0].prompt.template
class RECOMMENDER(BaseModel):
    rec: list[str]

def recommender(messages,project_id) -> dict:
    data_report=mainDatabase.fetch_data_report(project_id)
    total_messages = [
        {"role": "system", "content": rec_sys+f"\n\n Data Report:\n {data_report}" },
     ]+ messages
    response = llm.with_structured_output(RECOMMENDER).invoke(total_messages)
    return response.rec
    