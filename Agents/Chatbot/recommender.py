from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from API.Requests import projectRequests
load_dotenv()
from pydantic import BaseModel
from langchain import hub
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

rec_sys=hub.pull("chatbot-recommender").messages[0].prompt.template
class RECOMMENDER(BaseModel):
    rec: list[str]

async def recommender(messages,project_id) -> dict:
    data_report=await projectRequests.get_data_report(project_id)
    filtered_messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
    total_messages = [
        {"role": "system", "content": rec_sys+f"\n\n Data Report:\n {data_report}" },
     ]+ filtered_messages
    response = await llm.with_structured_output(RECOMMENDER).ainvoke(total_messages)
    return response.rec
    