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
from dotenv import load_dotenv
import json
load_dotenv()


CONFIGURATIONS={
    'model':"gemini-2.5-pro-preview-03-25",
}

# The Designer should respond with this sturcture of a List of json strings


system_prompt = hub.pull("viz-generation-designer").messages[0].prompt.template

async def designer_node(data_report,features=None):
    print("Designing visualizations")
    llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'])
    feature_request = f"The user has requested to focus on the following features: {features}, you can still add more features to the visualizations. but make it focused around the features mentioned." if features else ""
    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "Here is the data report, based on it write the visualizations needed by following the system instruction:\n\n {data_report}\n\n\n"+feature_request),
    ])

    designer_chain = prompt | llm
    response=await designer_chain.ainvoke({'data_report':data_report,'features':features})
    try:
        start = response.content.find('[')
        end = response.content.rfind(']') + 1
        json_string = response.content[start:end]
        visualizations = json.loads(json_string)
        print("Visualizations generated",visualizations)
    except Exception as e:

        visualizations = []
        print("Failed to parse the response. Please check the format of the response.")
    return visualizations