from helperFunctions import *
from .config import *
import loggerModule
logger=loggerModule.setup_logging(module_name="InsightGeneration")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=1)

async def PandasAgentResponder(state: dict) -> str:
    """
    This function is responsible for generating advanced insights based on the original insight card.
    It uses the LangChain framework to interact with the LLM and generate new insights.
    """
    agent_executor = create_pandas_dataframe_agent(
                    llm,
                    state["df"],
                    agent_type="tool-calling",
                    allow_dangerous_code=True,
                    verbose=True,
                )
    response = agent_executor.invoke(state["user_query"])
    step = response["intermediate_steps"][-1]
    try:
        output_df = extract_dataframe_from_output(step[1])
    except Exception as e:
        logger.error(f"Error in extracting dataframe from output: {e}")
        output_df = pd.DataFrame()
    return {"response": response["output"], "resulted_df": output_df}