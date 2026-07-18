# AI-Powered Sports Quiz Generation Agent

An interactive Streamlit application utilizing Retrieval-Augmented Generation (RAG) with ChromaDB and real-time web search to construct fact-checked multiple-choice quizzes.

## Architecture Highlights
- **Vector Space (ChromaDB)**: Extracts historical records using explicit sport-specific metadata indexing.
- **Freshness Layer (DuckDuckGo)**: Fetches real-time web context with a strict silent empty fallback to prevent hallucinated meta-questions.
- **Orchestration Brain (OpenAI)**: Generates exactly 4-5 structured multiple-choice questions cleanly grounded in verified context.

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Configure your OpenAI API key inside a root-level `.env` file.
3. Clean any existing local cache completely: `rm -rf chroma_db/`
4. Run the web dashboard application: `streamlit run app.py`
