# AI-Powered Sports Quiz Agent

An interactive web application built with Streamlit that generates fact-checked sports quizzes using Retrieval-Augmented Generation (RAG).

## Features
- Retrieves historical facts from a local ChromaDB vector database.
- Pulls live, up-to-date context from the web using DuckDuckGo Search.
- Generates 4 strictly grounded multiple-choice questions via OpenAI (GPT-3.5-Turbo).
- Supports Cricket, Football, Badminton, Tennis, and Basketball.
- Interactive, state-managed UI with color-coded answer reveals.

## Project Structure
```
sports-quiz-agent/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── app.py
├── data/
│   └── sports_facts.json
└── src/
    ├── __init__.py
    ├── config.py
    ├── database.py
    ├── search.py
    └── generator.py
```

## Setup Instructions
1. Clone the repository and navigate into the project folder.
2. Create a virtual environment: `python -m venv venv` then `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux).
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file and add your OpenAI API key: `OPENAI_API_KEY=sk-your_key_here`
5. Run the application: `streamlit run app.py`

## How to Get an OpenAI API Key
Visit https://platform.openai.com/api-keys, sign in, and click "Create new secret key".

## How It Works
1. User selects a sport and difficulty level from the sidebar.
2. The app queries ChromaDB for relevant historical facts about the sport.
3. The app searches DuckDuckGo for recent live news about the sport.
4. Both contexts are combined and sent to OpenAI GPT-3.5-Turbo.
5. The LLM generates 4 grounded multiple-choice questions displayed interactively.
