import google.generativeai as genai

GENAI_API_KEY = "AIzaSyDphGovO3le5oZMfdCdVSuObg_9kz2tBWg"


def configure_model():
    genai.configure(api_key=GENAI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash-exp")


model = configure_model()
