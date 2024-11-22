from flask import Flask
from google.cloud import bigquery
from sqlalchemy import create_engine
import os
from langchain.agents import AgentType
from langchain_community.chat_models import ChatOpenAI  # Updated import for ChatOpenAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent  # Updated import for create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit  # Updated import for SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase  # Updated import for SQLDatabase

# Initialize Flask app
app = Flask(__name__)


# Set environment variables for Google Cloud and OpenAI
service_account_file  = "./service-account-key.json"
os.environ["OPENAI_API_KEY"] = "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"
project = "spf-cli"
dataset = "retail_sales_dataset"

# SQLAlchemy connection
sqlalchemy_url = f'bigquery://{project}/{dataset}?credentials_path={service_account_file}'

# Define the route to execute the code
@app.route('/', methods=['GET'])
def execute_code():
    try:
        # Create an Engine and SQLDatabaseToolkit 
        engine = create_engine(sqlalchemy_url)
        db = SQLDatabase(engine)
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        # Create a SQLDatabaseToolkit
        toolkit = SQLDatabaseToolkit(llm=llm, db=db)

        # Create SQL AgentExecutor 
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            top_k=1000,
            handle_parsing_errors=True 
        )

        # Run the agent
        agent_executor.run('Quel est la plus grosse transaction ? Renvoie moi le client id, transaction id et montant')
        return 'OK', 200
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)