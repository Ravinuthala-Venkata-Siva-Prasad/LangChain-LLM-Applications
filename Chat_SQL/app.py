import streamlit as st
from pathlib import Path
from urllib.parse import quote_plus
from sqlalchemy import create_engine

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent


# Streamlit UI
st.set_page_config(
    page_title="LangChain: Chat with SQL DB",
    page_icon="🦜"
)

st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLite 3 Database - student.db",
    "Connect to your MySQL Database"
]

selected_opt = st.sidebar.radio(
    label="Choose the DB which you want to chat",
    options=radio_opt
)

db_uri = LOCALDB if selected_opt == radio_opt[0] else MYSQL


# MySQL Configuration
mysql_host = mysql_user = mysql_password = mysql_db = None

if db_uri == MYSQL:
    mysql_host = st.sidebar.text_input("Provide MySQL Host", value="localhost")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")


# Groq API Key
api_key = st.sidebar.text_input(
    label="Groq API Key",
    type="password"
)

if not api_key or not api_key.strip():
    st.info("Please enter your Groq API key.")
    st.stop()


# LLM Model
llm = ChatGroq(
    api_key=api_key.strip(),
    model="openai/gpt-oss-20b",
    temperature=0,
    streaming=False
)


# Database Configuration
@st.cache_resource(ttl=7200)
def configure_db(
    db_uri,
    mysql_host=None,
    mysql_user=None,
    mysql_password=None,
    mysql_db=None
):
    if db_uri == LOCALDB:

        db_path = (Path(__file__).parent / "student.db").resolve()

        if not db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {db_path}"
            )

        engine = create_engine(
            f"sqlite:///{db_path.as_posix()}"
        )

        return SQLDatabase(engine)

    elif db_uri == MYSQL:

        if not all([
            mysql_host,
            mysql_user,
            mysql_password,
            mysql_db
        ]):
            raise ValueError(
                "Please provide all MySQL connection details."
            )

        user = quote_plus(mysql_user)
        password = quote_plus(mysql_password)
        database = quote_plus(mysql_db)

        connection_url = (
            f"mysql+mysqlconnector://{user}:{password}"
            f"@{mysql_host}/{database}"
        )

        engine = create_engine(connection_url)

        return SQLDatabase(engine)

    raise ValueError("Unsupported database selection.")


# Connect to Database
try:
    db = configure_db(
        db_uri,
        mysql_host,
        mysql_user,
        mysql_password,
        mysql_db
    )

except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()


# Display Database Tables
try:
    with st.expander("View Database Tables"):
        st.write(db.get_usable_table_names())

except Exception as e:
    st.error(f"Could not read database tables: {e}")
    st.stop()


# SQL Toolkit
toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm
)


# SQL Agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="tool-calling",
    verbose=True
)


# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Ask me anything about your SQL database."
        }
    ]


# Clear Chat History
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Ask me anything about your SQL database."
        }
    ]


# Display Previous Messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# User Input
user_query = st.chat_input(
    "Ask anything about your database..."
)


if user_query:

    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):

        callback = StreamlitCallbackHandler(
            st.container()
        )

        try:
            response = agent.invoke(
                {"input": user_query},
                config={
                    "callbacks": [callback]
                }
            )

            answer = response["output"]

            st.write(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(f"Error generating answer: {e}")