import streamlit as st
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os 
from dotenv import load_dotenv
load_dotenv(".env")

# Lansmith Tracking
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_PROJECT="Basic Project"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# PromptTemplate
prompt = ChatPromptTemplate(
    [
        ("system", "you are Helpfull assistant .Response to the user queries"),
        ("user","Questions:{question}")
    ]
)

# Response 
def generate_response(question,api_key,engine,temperature,max_tokens):
    openai.api_key=api_key
    llm = ChatOpenAI(model=engine)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    answer = chain.invoke({'question':question})
    return answer

# Title of the app
st.title("Enhanced Q&A Chatbot with OpenAI")

#SiderBar
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API KEY:",type="password")

#Select the OpenAI model
engine= st.sidebar.select_slider("Select OpenAI Model",["gpt-4o","gpt-5","gpt-4-turbo"])
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7,step=0.1)
max_tokens=st.sidebar.slider("Max Tokens", min_value=50,max_value=300,value=150)

# MainInterface for user input
st.write("Ask Questions")
user_input=st.text_input("You:")

if user_input and api_key:
    response=generate_response(user_input,api_key,engine,temperature,max_tokens)
    st.write(response)

elif user_input:
    st.warning("Please Enter the OpenAI API KEY in the side bar")
else:
    st.write("Plese Provide the user input")




