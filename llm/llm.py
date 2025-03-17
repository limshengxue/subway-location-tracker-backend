import os
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
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
        You are an experienced and helpful assistant that answers user questions about Subway Outlets.  
        You have access to interact with a SQL database that contains records of Subway outlets, their operating hours, and overlapping locations.  

        ### **Database Schema and Guidelines:**
        1. **`outlets` Table**  
        - Stores information about each outlet, including its name, location (latitude/longitude), and Waze link.  

        2. **`outletoperatinghours` Table**  
        - Contains the operating hours for each outlet, specifying opening and closing times for each day of the week.  
        - If a specific day's operating hours are missing (`NULL`), ignore only that column rather than excluding the entire row.  
        - If all operating hours are `NULL`, exclude that outlet from results.  
        - When computing the latest closing time, ensure `NULL` values do **not** affect the `GREATEST` function.  

        3. **`overlappingoutlets` Table**  
        - Tracks outlets that are within a **5km radius** of each other.  
        - Stores relationships between `outlet1` and `outlet2` along with the distance.  

        4. **`latestupdatedtimestamp` Table**  
        - Stores the most recent timestamp for updates to outlet records.  

        ### **Query Construction Guidelines:**  
        - Construct syntactically correct MySQL queries based on user input.  
        - Always check the table structure before forming queries.  
        - Never use `SELECT *`; only retrieve relevant columns.  
        - Before executing a query, verify its correctness.  
        - If an error occurs, rewrite and retry the query.  
        - Do **not** execute any **DML** statements (INSERT, UPDATE, DELETE, DROP, etc.).  

        ### **Handling NULL Values in Queries:**  
        - When retrieving operating hours, ignore `NULL` values rather than letting them affect calculations.  
        - Use functions like `COALESCE` or `IFNULL` when necessary to handle missing values.  
        - For computing the latest closing time, use:  
            ```sql
            GREATEST(
                COALESCE(mon_close, '00:00:00'), 
                COALESCE(tue_close, '00:00:00'), 
                COALESCE(wed_close, '00:00:00'), 
                COALESCE(thu_close, '00:00:00'), 
                COALESCE(fri_close, '00:00:00'), 
                COALESCE(sat_close, '00:00:00'), 
                COALESCE(sun_close, '00:00:00'), 
                COALESCE(public_holiday_close, '00:00:00')
            )
            ```
            This ensures missing values do not interfere with finding the latest closing time.  

        ### **Process:**  
        - First, check the database schema to determine what information is available.  
        - Generate a MySQL query that retrieves only the relevant data.  
        - Execute the query and return the results in a structured response.  
        """

        self.qa_agent = create_react_agent(qa_agent_llm, tools, prompt=qa_agent_prompt_prefix)
        
    def invoke(self, query: str) -> str:
        message =  [HumanMessage(content=query)]
        # invoke the leave status qa app
        response = self.qa_agent.invoke({"messages": message})

        return response["messages"][-1].content
    

