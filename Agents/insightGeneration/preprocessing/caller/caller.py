"""
caller.py

This module sets up a language model to invoke tools based on the state messages.
The language model is configured to choose from a set of tools and generate a response.

Dependencies:
- langchain_openai 
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
- llm: An instance of ChatOpenAI configured with the specified model and temperature.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from preprocessing.caller.mainTools import tools
from dotenv import load_dotenv
from langchain import hub
from typing import Literal
from langgraph.graph import END

load_dotenv()

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

system_prompt = hub.pull("preprocessing-caller").messages[0].prompt.template

async def caller_node(state):
    """
    Process a single preprocessing task using tools.
    
    Args:
        state (dict): The current state containing:
            - preprocessing_tasks: The task to process
            - target_column: The column to process
            - strategy: The strategy to use
            - dataframe: The input DataFrame
            - messages: List of messages in the conversation
    
    Returns:
        dict: Updated state with:
            - preprocessed_dataframe: The processed DataFrame
            - messages: Updated message history
            - error: Error status
    """
    print("Calling tools \n")
    print(f"state in caller: {state}")
    task = state['preprocessing_tasks']
    column = state['target_column']
    strategy = state['strategy']
    # Prepare messages for tool invocation
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"here is the task: {task}, here is the column: {column}, here is the strategy: {strategy}"}
    ]
    
    # Bind tools to the model
    model_with_tools = llm.bind_tools(tools)
    response = await model_with_tools.ainvoke(messages)
    return {"caller_response": response}