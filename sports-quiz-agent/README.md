# AI-Powered Sports Quiz Agent

An interactive web application built with Streamlit that generates fact-checked sports quizzes using Retrieval-Augmented Generation (RAG).

## Features
- Retrieves historical facts from a local ChromaDB vector database.
- Pulls live, up-to-date context from the web using DuckDuckGo Search.
- Generates 3 strictly grounded multiple-choice questions via OpenAI.
- Interactive, state-managed UI with color-coded answer reveals.

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file and add your API key: `OPENAI_API_KEY=your_key_here`
3. Run the application: `streamlit run app.py`
