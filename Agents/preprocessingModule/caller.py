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
from mainTools import tools
from dotenv import load_dotenv
from langchain import hub

load_dotenv()

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

system_prompt = hub.pull("preprocessing-caller").messages[0].prompt.template

async def caller_node(state):
    print("Calling tools")
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state['messages']
    # the model can now see the tools, and is forced to choose one
    model_with_tools = llm.bind_tools(tools, tool_choice='any')
    
    try:
        response = await model_with_tools.ainvoke(messages)
        print(f"---TOOL CALL DEBUG: {response.tool_calls if hasattr(response, 'tool_calls') else 'No tool call'}---")
    except Exception as e:
        print(f"[Caller Node Error]: {e}")
        return {"messages": [{"role": "assistant", "content": "Something went wrong calling the tools."}]}

    return {"messages": [response]}
