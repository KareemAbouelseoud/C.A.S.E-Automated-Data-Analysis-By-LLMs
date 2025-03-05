import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

GENAI_API_KEY = "AIzaSyDphGovO3le5oZMfdCdVSuObg_9kz2tBWg"

def configure_model():
    genai.configure(api_key=GENAI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash-exp")

model = configure_model()

CONFIGURATIONS={
    'temperature':0.0,
    'model':"gemini-2.0-flash",
    'number of retries':3
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

