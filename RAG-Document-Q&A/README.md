# RAG Document Q&A Chatbot 📚

## Overview

An AI-powered document question-answering application built using Python, Streamlit, LangChain, Hugging Face embeddings, FAISS, and Groq.

The application allows users to upload PDF research papers, retrieve relevant document sections, and generate answers using Retrieval-Augmented Generation (RAG).

## Features

- Upload multiple PDF research papers.
- Extract text from PDF documents.
- Split documents into smaller text chunks.
- Generate embeddings using Hugging Face Sentence Transformers.
- Store document embeddings in a FAISS vector database.
- Retrieve relevant document chunks using similarity search.
- Generate context-aware answers using a Groq-hosted language model.
- Display retrieved text, source filenames, and page information.
- Measure answer generation time.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| LangChain | RAG pipeline and LLM orchestration |
| Hugging Face | Embedding generation |
| Sentence Transformers | Semantic text embeddings |
| FAISS | Vector similarity search |
| Groq API | Language model inference |
| PyPDF | PDF text extraction |
| python-dotenv | Environment variable management |

## Architecture

```text
PDF Upload
    |
    v
PDF Text Extraction
    |
    v
Text Splitting
    |
    v
Hugging Face Embeddings
    |
    v
FAISS Vector Store
    |
    v
User Question
    |
    v
Retrieve Relevant Chunks
    |
    v
Groq Language Model
    |
    v
Generated Answer
    |
    v
Display Answer and Retrieved Context
```

## How It Works

### 1. Document Loading

PDF documents are loaded using PyPDFLoader.

### 2. Text Splitting

RecursiveCharacterTextSplitter divides the extracted text into smaller chunks.

The current implementation uses:
- Chunk size: 1000 characters
- Chunk overlap: 200 characters

### 3. Embedding Generation

The application uses the following embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

### 4. Vector Storage

FAISS stores the document embeddings and supports similarity-based retrieval.

### 5. Retrieval

The retriever requests the three most relevant document chunks for a question.

### 6. Answer Generation

The retrieved context and user question are passed to the Groq-hosted language model to generate an answer.

## Installation

### 1. Install dependencies

From your Python environment, install the required packages.

```bash
pip install streamlit python-dotenv langchain-groq langchain-huggingface langchain-text-splitters langchain-classic langchain-community faiss-cpu sentence-transformers pypdf
```

### 2. Configure the API key

Create a `.env` file in the location expected by the application.

```env
GROQ_API_KEY=your_groq_api_key
```

Never upload your actual API key to GitHub.

### 3. Run the application

From the main repository directory:

```bash
streamlit run RAG-Document-Q&A/app.py
```

## Screenshots

Add your RAG application screenshot here.

The screenshot should show the document upload interface, generated answer, or retrieved document sections.

## Current Limitations

- The vector database is maintained in Streamlit session state rather than persisted as a permanent database.
- Retrieval quality depends on the document content and embedding similarity.
- Generated answers may contain errors.
- Scanned PDFs may require OCR when they do not contain extractable text.
- Automated retrieval and answer evaluation have not yet been demonstrated.

## Future Improvements

- Add persistent vector storage.
- Implement hybrid search and reranking.
- Add source citations to generated answers.
- Evaluate retrieval relevance and answer quality.
- Add automated tests.
- Build a FastAPI backend.
- Deploy the application using Docker and a cloud platform.

## Author

Venkata Siva Prasad