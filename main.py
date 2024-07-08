import requests
import re
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.utilities import SQLDatabase
import dbc
import model
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import altair as alt
import IPython
import TemplateConfig

print("===============================================================================================")

st.sidebar.image("logo-black.png")
# add_logo("logo-black.png")
st.markdown(TemplateConfig.page_bg, unsafe_allow_html=True)
column1,column2 =st.columns((2,1))

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  engine = create_engine(db_uri)
  return db_uri, SQLDatabase.from_uri(db_uri) , engine

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

def get_sql_response(schema,question):
        
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

        response = requests.post(model.url, json=sql_prompt, headers=model.headers)
        # print(response.json()['text'])
        print(response.json())
        return response.json()['text']


def get_plot_response(schema, question, query, sql_engine, db,data):
        
        plot_prompt = {
            "prompt":f"""You are a data analyst at a company. You are interacting with a user who wants to create python visualization report based on the data.
            Based on the below table schema,user question, sql query and the data output from sql query, write a python query to plot the output data in a python graph. 
            you can use the schema information from variable schema and use the "sql_engine" variable to establish connection to the db and create the dataframe.
            
            Consider the input sql query with out any line breaks.
            Give an alias name for each and every column used in the query. no exceptions
            
                User question: {question}
                SQL Query: <SQL>{query}</SQL>
                Data : {data}
                <SCHEMA>{schema}</SCHEMA>
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
            Always sort it with 'X' or 'Y' prefixes/alias
            Question: Create a bar chart using Altair        # 
            python query: 
                chart = alt.Chart(df).mark_bar().encode(
                x=('Language', sort = '-y'),
                y='TotalPopulation',
                color='Language'
    )

            Write the python query to create plots and graphs from the dataframe and nothing else. 
            Do not wrap the python query in any other text, not even backticks.
            Use only "altair" library to plot the graphs and "Pandas" for connection and dataframe handling using required orderby & groupby clauses.
            and while writing the sql query, consider it without any line breaks.

            priority: always assign the code compoents for charts under "chart" variable and always sort it by a numeric column based on user query
            
            You can return none if the data frame has just only 1 column or only 1 row or if the plot is more complicated to fit in traditional plotting style.
            Your turn:

            """.format(schema,question,query,sql_engine,db)
            }
        response = requests.post(model.url, json=plot_prompt, headers=model.headers)
        print(response.json()['text'])
        return response.json()['text']

def get_lang_response(schema, question, query, sql_engine, db, data):      
        lang_prompt = {
            "prompt":f"""You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
            Based on the table schema below, user question, sql query and data, Write a natural language response.
            Use the data provided below, it was generated as a output from the sql query, that would be your source of truth.

                User question: {question}
                SQL Query: <SQL>{query}</SQL>
                Data : {data}
                <SCHEMA>{schema}</SCHEMA>
                SQL Engine : {sql_engine}
                Database " {db}
            
            """.format(schema,question,query,sql_engine,db,data)
            }
        response = requests.post(model.url, json=lang_prompt, headers=model.headers)
        print(response.json()['text'])
        return response.json()['text']

#Setting page title
# st.set_page_config(layout="wide")
st.title("Chat with your data...")

#Checking if the chat history in session state, to identify if it's the beginning of the chat and display standard message
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [ AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),]  

# if "query_history" not in st.session_state:
#     st.session_state.query_history = [AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."), ]  


with st.sidebar:
    st.subheader("Connect to Database..")

    st.text_input("Host", value=dbc.Host, key="Host")
    st.text_input("Port", value=dbc.Port, key="Port")
    st.text_input("User", value=dbc.User, key="User")
    st.text_input("Password", type="password", value=dbc.Pwd, key="Password")
    st.text_input("Database", value=dbc.DB, key="Database")

    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            sql_connection = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = sql_connection
            st.success("Connected to database!")

# sql_connect = init_database(dbc.User,dbc.Pwd,dbc.Host,dbc.Port,dbc.DB)
sql_connect = init_database(user=st.session_state.User, password=st.session_state.Password,host=st.session_state.Host,port=st.session_state.Port,database=st.session_state.Database)
db = sql_connect[0]
schema = sql_connect[1].get_table_info()
sql_engine = sql_connect[2]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content = user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)
    
    with st.chat_message("AI"):
        # response = get_response(user)
        sql_response = get_sql_response(schema=schema,question= user_query)
        data =  pd.read_sql_query(sql_response, sql_engine)
        sql_response = get_plot_response(schema=schema, query=sql_response, sql_engine= sql_engine, db= db, question=user_query,data = data)  
        plot_response = extract_code_from_text(sql_response)
        lang_response = get_lang_response(schema=schema, query=sql_response, sql_engine= sql_engine, db= db, question=user_query, data = data)
        st.markdown(lang_response)
        try:
            exec(plot_response)
            if 'chart' in globals():
                    # Access the 'chart' object
                    chart = globals()['chart']
                    
                    # Check if 'chart' is an Altair chart object
                    if isinstance(chart, alt.Chart):
                        # Display the Altair chart
                        st.altair_chart(chart.interactive(), use_container_width=True)
                        chart.save("chart.html", embed_options={'renderer':'svg'})

                        # Append the chart object to the chat history
                        # st.session_state.chat_history.append(chart)
                    else:
                        # Handle the case where 'chart' is not an Altair chart object
                        st.error("The generated chart is not valid.")
            else:
                # Handle the case where 'chart' is not defined in the executed code
                 st.error("No chart found in the code output.")
        except Exception as e:
            print(e)
            st.markdown("No Plot for the above query")

    with st.expander("Check Code"):
        st.write(sql_response)

    # st.session_state.query_history.append(AIMessage(content = sql_response)
    st.session_state.chat_history.append(AIMessage(content = lang_response))

print("===============================================================================================")