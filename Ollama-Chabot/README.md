# Ollama Chatbot 🤖

## Overview

An interactive chatbot application built using Python, Streamlit, LangChain, and Ollama. It allows users to interact with locally hosted language models through a simple web interface.

## Features

- Integration with Ollama language models.
- Model selection through the Streamlit sidebar.
- Adjustable temperature and token settings in the interface.
- Prompt templates using LangChain.
- Text output processing using StrOutputParser.

## Technologies

- Python
- Streamlit
- LangChain
- Ollama

## Architecture

User Question → Prompt Template → Ollama LLM → Output Parser → Response

## Installation

### 1. Install Ollama

Install Ollama and ensure the required model is available locally.

### 2. Install dependencies

From your project environment, install the required packages.

```bash
pip install streamlit langchain-core langchain-ollama python-dotenv
```

### 3. Run the application

From the main repository directory:

```bash
streamlit run Ollama-Chatbot/app.py
```

## Screenshots

Add screenshots of your chatbot interface and LangSmith tracking here if they correspond to this application.

## Future Improvements

- Add conversation history.
- Support additional local models.
- Improve error handling.
- Add automated tests.

## Author

Venkata Siva Prasad