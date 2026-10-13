import os
import time
import tempfile
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Streamlit page configuration
st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG Document Q&A with Groq")
st.write("Upload your research paper and ask questions about it.")

# Check API key
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing. Check your .env file.")
    st.stop()

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="openai/gpt-oss-20b",
    temperature=0
)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
Answer the question using only the following document context.

If the answer is not available in the context, say:
"I could not find the answer in the uploaded document."

Context:
{context}

Question:
{input}

Answer:
""")

# Initialize session state
if "vectors" not in st.session_state:
    st.session_state.vectors = None

if "uploaded_names" not in st.session_state:
    st.session_state.uploaded_names = []

# Upload PDF files
st.subheader("1. Upload your PDF")

uploaded_files = st.file_uploader(
    "Choose PDF files from your computer",
    type=["pdf"],
    accept_multiple_files=True
)

# Create embeddings
if st.button("Create Document Embeddings", type="primary"):

    if not uploaded_files:
        st.warning("Please upload at least one PDF file.")

    else:
        all_documents = []

        try:
            with st.spinner("Reading your PDF files..."):

                for uploaded_file in uploaded_files:

                    # Save the uploaded PDF temporarily
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(uploaded_file.getvalue())
                        temp_path = temp_file.name

                    try:
                        loader = PyPDFLoader(temp_path)
                        documents = loader.load()

                        # Preserve the original filename in metadata
                        for doc in documents:
                            doc.metadata["source"] = uploaded_file.name

                        all_documents.extend(documents)

                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

            if not all_documents:
                st.error("No readable text was found in the PDF files.")
                st.stop()

            # Split PDF text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            chunks = text_splitter.split_documents(all_documents)

            if not chunks:
                st.error("No text chunks were created from the PDFs.")
                st.stop()

            # Create embeddings
            with st.spinner("Creating document embeddings..."):

                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

                # Create FAISS vector database
                vectors = FAISS.from_documents(
                    chunks,
                    embeddings
                )

            # Save in session state
            st.session_state.vectors = vectors
            st.session_state.uploaded_names = [
                f.name for f in uploaded_files
            ]

            st.success("Document embeddings created successfully!")
            st.write(f"PDF files: {len(uploaded_files)}")
            st.write(f"Pages loaded: {len(all_documents)}")
            st.write(f"Text chunks: {len(chunks)}")

        except Exception as e:
            st.error(f"Error processing PDFs: {e}")


# Ask questions
st.subheader("2. Ask a question about your PDF")

question = st.text_input(
    "Enter your question",
    placeholder="Example: What is the main objective of this research paper?"
)

if st.button("Get Answer"):

    if not question.strip():
        st.warning("Please enter a question.")

    elif st.session_state.vectors is None:
        st.warning(
            "Please upload your PDF and click Create Document Embeddings first."
        )

    else:
        try:
            # Create document chain
            document_chain = create_stuff_documents_chain(
                llm,
                prompt
            )

            # Retrieve relevant document chunks
            retriever = st.session_state.vectors.as_retriever(
                search_kwargs={"k": 3}
            )

            # Create retrieval chain
            retrieval_chain = create_retrieval_chain(
                retriever,
                document_chain
            )

            start_time = time.perf_counter()

            with st.spinner("Searching your PDF and generating an answer..."):
                response = retrieval_chain.invoke({
                    "input": question
                })

            elapsed_time = time.perf_counter() - start_time

            # Display answer
            st.subheader("Answer")
            st.write(response["answer"])

            st.caption(
                f"Response time: {elapsed_time:.2f} seconds"
            )

            # Display retrieved text
            with st.expander("View relevant text from your PDF"):

                for i, doc in enumerate(
                    response["context"],
                    start=1
                ):
                    st.markdown(f"**Retrieved section {i}**")
                    st.write(
                        f"Source: {doc.metadata.get('source', 'Unknown')}"
                    )
                    st.write(
                        f"Page: {doc.metadata.get('page', 'Unknown')}"
                    )
                    st.write(doc.page_content)
                    st.divider()

        except Exception as e:
            st.error(f"Error generating answer: {e}")