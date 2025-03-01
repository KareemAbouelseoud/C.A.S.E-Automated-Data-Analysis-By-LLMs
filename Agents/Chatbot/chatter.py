"""
Chatbot.py

This module sets up a language model to act as a chatbot with memory, responding to the user input.

Dependencies:
- langchain_groq
- dotenv

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the caller_node function to invoke tools based on the state messages.

Functions:
- load_dotenv: Loads environment variables from a .env file.
- caller_node: Invokes tools based on the state messages and returns the response.

Variables:
- ChatID : ID associated with the chat session for a specific user.
- chat_history: The chat history for the current chat session.
- systemprompt: The system prompt.
- model: An instance of Grog Llama3.
- chatBaseTemplate: A template for the chat history, ensuring that the system prompt is passed to the model in it's appropriate place.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import END
from langchain import hub
from langchain_core.runnables import RunnableConfig
from .botTools import tools
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gpt-4o-mini",
}
llm=ChatOpenAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("chatbot-chatter").messages[0].prompt.template



async def chatter_node(state,config: RunnableConfig):
    data_report=state['data_report']
    old_messages = state["messages"]
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" }
    ]+old_messages
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages,config)
    return {"messages": [response]}
    


async def should_continue(state)->Literal['tools','__end__']:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls!=[]:
        return "tools"
    return END




