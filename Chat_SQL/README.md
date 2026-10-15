# 🦜 LangChain SQL Database Chatbot

An AI-powered SQL chatbot built using Python, Streamlit, LangChain, and Groq. This application allows users to interact with a SQL database using natural language instead of writing SQL queries manually.

The chatbot converts user questions into SQL queries, executes them against the selected database, and presents the results in a conversational interface.

## 🚀 Features

- **Natural Language to SQL:** Ask questions about your database in plain English.
- **SQLite Database:** Connect to the local `student.db` database.
- **MySQL Connectivity:** Connect to a MySQL database using connection details.
- **AI-Powered SQL Agent:** Uses LangChain's SQL agent and Groq LLM.
- **Interactive Chat Interface:** Built with Streamlit.
- **Database Table Inspection:** View available database tables.
- **Chat History:** View previous questions and answers during the session.
- **Clear Chat History:** Reset the conversation using the sidebar.

## 🛠️ Technologies Used

- Python
- Streamlit
- LangChain
- LangChain Community
- LangChain Groq
- Groq LLM
- SQLAlchemy
- SQLite
- MySQL
- MySQL Connector

## 📂 Project Structure

```text
Chat_SQL/
│
├── app.py
├── sqlite.py
├── student.db
├── image.png
├── README.md
└── requirements.txt