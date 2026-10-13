# OpenAI Chatbot 💬

## Overview

An interactive chatbot developed using Python, Streamlit, LangChain, and the OpenAI API. The application allows users to select a supported model and submit questions through a web interface.

## Features

- Integration with OpenAI chat models.
- Interactive Streamlit interface.
- Model selection.
- Configurable temperature and token settings in the interface.
- LangChain prompt templates.
- String output parsing.
- LangSmith tracking configuration.

## Technologies

- Python
- Streamlit
- LangChain
- OpenAI API
- LangSmith
- python-dotenv

## Architecture

User Question → Prompt Template → OpenAI Model → Output Parser → Response

## Installation

### 1. Install dependencies

```bash
pip install streamlit langchain-openai langchain-core python-dotenv openai
```

### 2. Configure your API key

Create a `.env` file in the location expected by your application.

```env
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

Replace the placeholders with your actual credentials.

Never upload your `.env` file or API keys to GitHub.

### 3. Run the application

From the main repository directory:

```bash
streamlit run OpenAI-Chatbot/app.py
```

## Screenshots

Add your OpenAI chatbot output and relevant LangSmith tracking screenshots here.

## Future Improvements

- Add conversational memory.
- Improve error handling.
- Add automated testing.
- Evaluate response quality.

## Author

Venkata Siva Prasad