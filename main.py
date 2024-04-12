from dotenv import load_dotenv
import requests
from langchain_core.prompts import PromptTemplate
import re
import subprocess
from langchain_community.utilities import SQLDatabase
import dbc
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import matplotlib
import altair as alt
import IPython
matplotlib.use('agg')  # Set backend to Agg

url = "http://10.101.11.23:8000/deepseek_ai_model"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  engine = create_engine(db_uri)
  return db_uri, SQLDatabase.from_uri(db_uri) , engine

from sqlalchemy import create_engine
from sqlalchemy import inspect

sql_connect = init_database(dbc.User,dbc.Pwd,dbc.Host,dbc.Port,dbc.DB)
db = sql_connect[0]
schema = sql_connect[1].get_table_info()
sql_engine = sql_connect[2]
print(sql_engine)

def get_plotresponse():
    # Sending POST request
    response = requests.post(url, json=plot_prompt, headers=headers)
    print(response.json())
    return response.json()

def get_sqlresponse():
    # Sending POST request
    response = requests.post(url, json=sql_prompt, headers=headers)
    print(response.json())
    query_response=lambda vars: db.run(vars["query"])
    print(query_response)
    return response.json(), query_response

def extract_code_from_text(text):
    # Regular expression pattern to match code between triple single quotes
    pattern = r'```python\n(.*?)```'
    
    # Use re.search to find the first match of the pattern in the text
    match = re.search(pattern, text, re.DOTALL)
    
    # If a match is found, return the code inside triple quotes, otherwise return None
    if match:
        return match.group(1)
    else:
        return None

question = st.text_input("Question")
# question = """what is the 10 spoken languages based on population?"""
# st.write(question)

if question:
    sql_prompt = {
        "prompt":f"""You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, write a SQL query that would answer the user's question. 

        <SCHEMA>{schema}</SCHEMA>
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks. Generate the sql query without any line breaks
        
        For example:
        Question: which 3 artists have the most tracks?
        SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
        Question: Name 10 artists
        SQL Query: SELECT Name FROM Artist LIMIT 10;
        
        Your turn:
        {question}
    
        """.format(schema,question)}
    
    output = get_sqlresponse()
    query = output[0]
    query_response = output[1]

    df = pd.read_sql_query(query, sql_engine)
    st.table(df)
            # SQL Response: {query_response}
    plot_prompt = {
        "prompt":f"""You are a python data analyst at a company. You are interacting with a user who wants to create python visualization report based on the data.
        Based on the below table schema,user question, sql query and sql response, write a python query to plot the output data in a python graph. 
        you can use the schema information from variable schema and use the "sql_engine" variable to establish connection to the db and create the dataframe.
        
        Consider the input sql query with out any line breaks
        
            <SCHEMA>{schema}</SCHEMA>
            User question: {question}
            SQL Query: <SQL>{query}</SQL>
            SQL Engine : {sql_engine}
            Database " {db}
        
            
        For example:
        Question: Presenting categorical data using a bar chart to compare different categories or groups
        Python Query: 
                    categories = ['A', 'B', 'C', 'D']
                    values = [20, 30, 25, 35]

                    # Create a bar chart
                    fig = go.Figure(data=[go.Bar(x=categories, y=values)])
                    fig.update_layout(title='Bar Chart', xaxis_title='Categories', yaxis_title='Values')
                    fig.show()

        Question: Create a bar chart using Altair        # 
        python query: 
            chart = alt.Chart(df).mark_bar().encode(
            x='Language',
            y='TotalPopulation',
            color='Language'
)

        Write the python query to create plots and graphs from the dataframe and nothing else. Do not wrap the python query in any other text, not even backticks.
        Use only "altair" library to plot the graphs and "Pandas" for connection and dataframe handling using required orderby & groupby clauses.
        and while writing the sql query, consider it without any line breaks.
        always assign the code compoents for charts under "chart" variable.
        Your turn:

        """.format(schema,question,query,sql_engine,db)
        }
    
    # code_output = extract_code_from_text(get_plotresponse())
    # exec(code_output)
    # st.altair_chart(chart, use_container_width= True)

    code_output = extract_code_from_text(get_plotresponse())

    # Use eval() to execute the code and capture the variables defined within
    # exec_globals = {}
    exec(code_output)

    # Extract the 'chart' variable from the executed code
    if 'chart' in globals():
        chart = globals()['chart']
        # Now 'chart' is defined in the current scope, you can use it with st.altair_chart()
        st.altair_chart(chart.interactive(), use_container_width=True)
    else:
        # Handle the case where 'chart' is not defined in the executed code
        st.error("No chart found in the code output.")

        # Check if the request was successful (status code 200)
        # if response.status_code == 200:
        #     # response = response.json()
        #     # lines = response.splitlines()
        #     # lines = lines[1:-1]
        #     # response = '\n'.join(lines)
        #     print(response.json())
        #     # return response
        # else:
        #     print("Request failed with status code:", response.status_code)

    # script = get_response()
    # with open("gencode.py","w") as f:
    #     for line in script.splitlines():
    #         f.write(line + '\n')

    # subprocess.run("streamlit run gencode.py")