"""
caller.py

This module sets up a language model to invoke tools based on the state messages.
The language model is configured to choose from a set of tools and generate a response.

Dependencies:
- langchain_google_genai
- mainTools
- dotenv
- langchain

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the caller_node function to invoke tools based on the state messages.

Functions:
- load_dotenv: Loads environment variables from a .env file.
- caller_node: Invokes tools based on the state messages and returns the response.

Variables:
- CONFIGURATIONS: A dictionary containing the configuration for the language model.
- system_prompt: The system prompt template pulled from the hub.
- llm: An instance of ChatGoogleGenerativeAI configured with the specified model and temperature.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from Agents.codeGeneration.mainTools import tools
from dotenv import load_dotenv
from langchain import hub

load_dotenv()

CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-1.5-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

system_prompt = hub.pull("caller").messages[0].content

def caller_node(state):
    messages = [
        {"role": "system", "content": system_prompt},
    ]+state['messages']
    # the model can now see the tools, and is forced to choose one
    model_with_tools=llm.bind_tools(tools,tool_choice='any')
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


    
