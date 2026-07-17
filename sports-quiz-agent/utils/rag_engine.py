import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from utils.database import get_vector_store

def generate_sports_quiz(sport: str, difficulty: str) -> str:
    """
    Executes the RAG pipeline: retrieves local facts, searches the web, and generates a quiz.
    """
    # 1. Safely pull the API key
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = os.getenv("GOOGLE_API_KEY")

    # 2. Initialize the LLM explicitly passing the key
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.7,
        google_api_key=api_key
    )
    
    # 3. Retrieve Local Context (from ChromaDB)
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    local_docs = retriever.invoke(sport)
    
    if local_docs:
        local_context = " ".join([doc.page_content for doc in local_docs])
    else:
        local_context = "No specific local facts found."
    
    # 4. Retrieve Live Internet Context (from DuckDuckGo)
    search_tool = DuckDuckGoSearchRun()
    try:
        web_context = search_tool.run(f"Top {sport} historical facts and recent trivia")
    except Exception as e:
        web_context = "Web search currently unavailable."
    
    # 5. Construct the Augmented Prompt (Updated to strictly demand 4 questions)
    prompt = f"""
    You are an expert sports quiz master. Your task is to generate a 4-question multiple-choice quiz about {sport} at a {difficulty} difficulty level.
    
    Use the following verified context to build your questions. Do not hallucinate outside of this information if possible.
    
    [Local Database Facts]
    {local_context}
    
    [Live Web Facts]
    {web_context}
    
    Format the output elegantly using Markdown. For each question, strictly provide:
    1. The Question.
    2. 4 Options labeled A, B, C, and D.
    3. The Correct Answer explicitly stated on a new line below the options.
    """
    
    # 6. Generate the LLM response
    response = llm.invoke(prompt)
    
    # 7. Clean the output to remove raw dictionary/signature structures
    if isinstance(response.content, list):
        # Extracts only the clean text portion if the model returns a multi-modal block
        clean_text = "".join([block.get("text", "") for block in response.content if isinstance(block, dict) and "text" in block])
        return clean_text
        
    return response.content
