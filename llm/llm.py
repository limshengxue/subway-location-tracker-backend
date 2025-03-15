import os
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


@tool
def get_distance_between_two_outlets(id1: str, id2: str) -> str:
    """Use to get distance between 2 outlets in kilometers""" 
    df = pd.read_csv(os.getenv("DISTANCE_MATRIX_FILE_PATH"), index_col=0)
    print(df)
    return df.at[id1, id2]

@tool
def get_current_time() -> str:
    """Use to get current time"""
    # set timezone
    import pytz
    timezone = pytz.timezone(os.getenv("TIMEZONE"))

    # get current time
    import datetime
    now = datetime.datetime.now(timezone)
    return now.strftime("%Y-%m-%d %H:%M:%S")
    

class QAAgent():
    _instance = None  # Class-level variable to hold the singleton instance
    
    def __new__(cls) -> "QAAgent":
        if cls._instance is None:  # Only create a new instance if it doesn't exist
            cls._instance = super(QAAgent, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.prepare_qa_agent()
        
    def prepare_qa_agent(self):
        # prepare db connection
        db = SQLDatabase.from_uri(os.getenv("DB_CONN"))
        # get LLM instance
        qa_agent_llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
        # instantiate SQL database toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=qa_agent_llm)
        # combine the SQL database tools with the self-defined tools
        tools = toolkit.get_tools() + [get_distance_between_two_outlets]

        # prompt
        qa_agent_prompt_prefix = """
        You are an experienced and helpful assistant that answer user questions about Subway Outlets. 
        You have the access to interact with a SQL database which give you access to the outlets records.
        The table `outlets` contains all the outlets records.
        The operating hours indicate the opening and closing time of each outlet, at the specified days.
        Becareful with the operating hours as they are unstructured. You often need to read all the rows to truly understand the operating hours.
        The table `overlappingoutlets` indicate outlet that overlaps with each other within a 5km radius of each other.
        Given an input question, create a syntactically correct mysql query to run, then look at the results of the query and return the answer.
        Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
        To start you should ALWAYS look at the tables in the database to see what you can query.
        Always use database tool to check out the schema before deciding that you do not have enough information to answer the question
        """

        self.qa_agent = create_react_agent(qa_agent_llm, tools, prompt=qa_agent_prompt_prefix)
        
    def invoke(self, query: str) -> str:
        message =  [HumanMessage(content=query)]
        # invoke the leave status qa app
        response = self.qa_agent.invoke({"messages": message})

        return response["messages"][-1].content
    

