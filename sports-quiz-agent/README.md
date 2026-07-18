# AI-Powered Sports Quiz Generation Agent

An interactive Streamlit dashboard designed to automatically create fact-checked multiple-choice sports quizzes for social media engagement using Retrieval-Augmented Generation (RAG).

## Core Architecture
- **Vector Core (ChromaDB)**: Extracts historical records using strict sport-specific metadata indexing.
- **Web Intelligence (DuckDuckGo)**: Scours live online updates with dynamic fallback routines to bypass query limits.
- **Orchestration Brain (OpenAI GPT)**: Generates 4-5 structured multiple-choice questions cleanly grounded in the unified context payload.

## Installation & Deployment
1. Set up dependencies: `pip install -r requirements.txt`
2. Add your credentials to a root-level `.env` file.
3. Boot up the user interface: `streamlit run app.py`
