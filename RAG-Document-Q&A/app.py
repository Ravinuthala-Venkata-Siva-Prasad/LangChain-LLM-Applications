import streamlit as st
import os
import time
import tempfile
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY is missing in .env file")
    st.stop()

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="openai/gpt-oss-20b",
    temperature=0
)

prompt = ChatPromptTemplate.from_template("""
Answer the question using the provided context.
If the answer is not available, say you cannot find it.

Context:
{context}

Question:
{input}
""")

if "vectors" not in st.session_state:
    st.session_state.vectors = None

st.title("RAG Document Q&A with Groq")

uploaded_files = st.file_uploader(
    "Upload your research papers",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Document Embedding"):
    if not uploaded_files:
        st.warning("Please upload PDF files first")
    else:
        try:
            docs = []

            for file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                    temp.write(file.getvalue())
                    temp_path = temp.name

                try:
                    pdf_docs = PyPDFLoader(temp_path).load()
                    for doc in pdf_docs:
                        doc.metadata["source"] = file.name
                    docs.extend(pdf_docs)
                finally:
                    os.remove(temp_path)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            final_documents = text_splitter.split_documents(docs)

            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            st.session_state.vectors = FAISS.from_documents(
                final_documents, embeddings
            )

            st.success("Vector Database is ready!")

        except Exception as e:
            st.error(f"Error: {e}")

user_prompt = st.text_input("Enter your query from the research paper")

if st.button("Get Answer"):
    if not user_prompt:
        st.warning("Please enter your question")
    elif st.session_state.vectors is None:
        st.warning("Please upload PDFs and click Document Embedding first")
    else:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever(search_kwargs={"k": 3})
        retriever_chain = create_retrieval_chain(retriever, document_chain)

        start = time.perf_counter()

        try:
            response = retriever_chain.invoke({"input": user_prompt})
            st.write("### Answer")
            st.write(response["answer"])
            st.write(f"Response time: {time.perf_counter() - start:.2f} seconds")

            with st.expander("Document Similarity Search"):
                for i, doc in enumerate(response["context"], 1):
                    st.write(f"Document {i}: {doc.metadata.get('source', '')}")
                    st.write(doc.page_content)
                    st.write("---")

        except Exception as e:
            st.error(f"Error generating answer: {e}")