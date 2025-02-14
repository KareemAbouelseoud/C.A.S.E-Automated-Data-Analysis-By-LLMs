from typing import Literal
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

system_prompt = hub.pull("planner").messages[0].content
class Splitter(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    test_size: float = Field(description="Test size for splitting the data")
    shuffle: bool = Field(description="Whether to shuffle the data before splitting")
    stratify: bool = Field(description="Whether to stratify the data before splitting")



async def planner_node(state):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    response = await llm.with_structured_output(Splitter).ainvoke(messages)
    goto = response.next
    return {'next':goto}