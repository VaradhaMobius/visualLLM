# URL of the endpoint
url = "http://10.101.11.23:8000/deepseek_ai_model"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
        }

# ------------------------------

# "prompt":f"""You are a data analyst at a company. you are responsible for extracting data from database and create visualizations.
#             You are interacting with a user who is asking you questions about the company's database.
#             Based on the below table schema & user question, You will do a 2 step process. 

#             Step 1: Write SQL Query to extract data. You can use the schema information from variable "schema" given below
#                     <SCHEMA>{schema}</SCHEMA>
#                     Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks. Generate the sql query without any line breaks
            
#             Step 2: Write a python query to plot the output data in a python graph. Use the "sql_engine" variable to establish connection to the db and create the dataframe.
#                     Use the below "sql_engine" connection and "db" information to generate the query for plotting the graphs
#                 SQL Engine : {sql_engine}
#                 Database " {db}
                        
#             For example:
#             Question1 : Give me the top 10 cities with highest population 

#             Answer : 
#             # Establish connection to the database and create dataframe
#             df = pd.read_sql_query("SELECT Name, Population FROM city ORDER BY Population DESC LIMIT 10;", sql_engine)

#             # Create a bar chart
#             chart = alt.Chart(df).mark_bar().encode(
#                 x='Name',
#                 y='Population',
#                 color='Name')

#             Question2 : What are the top 10 languages spoken by population
#             Answer : 
#             df = pd.read_sql_query("SELECT cl.Language, SUM(c.Population * cl.Percentage / 100) as TotalPopulation FROM countrylanguage cl JOIN country c ON cl.CountryCode = c.Code GROUP BY cl.Language ORDER BY TotalPopulation DESC LIMIT 10;", sql_engine)

#             # Create a bar chart
#             chart = alt.Chart(df).mark_bar().encode(
#                 x='Language',
#                 y='TotalPopulation',
#                 color='Language'
#             )

            
#             Your turn:
#             {question}
