"""
This module defines a Designer class and sets up a language model to generate ideas of visualizations based on a data report.
The Designer class is used to structure the output of the language model, which is expected to be a list of JSON strings.

Dependencies:
- langchain_google_genai
- langchain_core.prompts
- langchain
- pydantic
- dotenv

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the designer_chain to generate visualizations based on a data report.

Classes:
- Designer: A Pydantic model to structure the output of the language model.

Functions:
- load_dotenv: Loads environment variables from a .env file.

Variables:
- CONFIGURATIONS: A dictionary containing the configuration for the language model.
- system_prompt: The system prompt template pulled from the hub.
- llm: An instance of ChatGoogleGenerativeAI configured with the specified model and temperature.
- prompt: A ChatPromptTemplate created from the system and user messages.
- designer_chain: A chain that combines the prompt and the language model with structured output.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from pydantic import BaseModel
from typing import List

from dotenv import load_dotenv
load_dotenv()


CONFIGURATIONS={
    'temperature':0.6,
    'model':"gemini-2.0-flash",
}

# The Designer should respond with this sturcture of a List of json strings
class Designer(BaseModel):
    response: List[str]


system_prompt = hub.pull("viz-generation-designer").messages[0].prompt.template

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "Here is the data report, based on it write the visualizations needed by following the system instruction:\n\n {data_report}"),
])

designer_chain = prompt | llm.with_structured_output(Designer)

