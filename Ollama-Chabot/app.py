import os
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import openai
from langchain_community.llms import ollama
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_PROJECT="Basic Project"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

#prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "Question: {question}")
    ]
)

def generate_response(question,llm,temperature,max_tokens):
    llm = OllamaLLM(model=llm)
    output_parser=StrOutputParser()
    chain = prompt | llm | output_parser
    answer=chain.invoke({'question':question})
    return answer


#title of the app
st.title("Enhanced Q&A Chatbot with Ollama")

llm = st.sidebar.selectbox(
    "Select Open Source Model",
    ["mistral", "llama3.2", "gemma3"]
)

temperature = st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7,step=0.1)
max_tokens = st.sidebar.slider("Max_Tokens",min_value=50,max_value=300,value=150)

st.write("Go ahead and ask any question")
user_input = st.text_input("You:")


if user_input:
    response = generate_response(user_input,llm,temperature,max_tokens)
    st.write(response)
else:
    st.write("Please Provide the user input")