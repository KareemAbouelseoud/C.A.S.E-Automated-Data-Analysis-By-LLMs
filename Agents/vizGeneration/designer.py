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
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from dotenv import load_dotenv
import json
load_dotenv()


CONFIGURATIONS={
    'temperature':0.7,
    'model':"deepseek-ai/deepseek-r1",
}

# The Designer should respond with this sturcture of a List of json strings


system_prompt = hub.pull("viz-generation-designer").messages[0].prompt.template

async def designer_node(data_report):
    print("Designing visualizations")
    llm=ChatNVIDIA(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'],max_tokens=4096)

    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "Here is the data report, based on it write the visualizations needed by following the system instruction:\n\n {data_report}"),
    ])

    designer_chain = prompt | llm
    response=await designer_chain.ainvoke({'data_report':data_report})
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