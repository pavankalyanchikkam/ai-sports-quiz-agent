import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from utils.database import get_vector_store

def generate_sports_quiz(sport: str, difficulty: str) -> tuple:
    """
    Executes the RAG pipeline and returns BOTH the quiz text and the context used.
    """
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.7,
        google_api_key=api_key
    )
    
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    local_docs = retriever.invoke(sport)
    
    if local_docs:
        local_context = " ".join([doc.page_content for doc in local_docs])
    else:
        local_context = "No specific local facts found."
    
    search_tool = DuckDuckGoSearchRun()
    try:
        web_context = search_tool.run(f"Top {sport} historical facts and recent trivia")
    except Exception as e:
        web_context = "Web search currently unavailable."
        
    unified_context = f"=== HISTORICAL FACTS (ChromaDB) ===\n{local_context}\n\n=== LIVE NEWS (DuckDuckGo) ===\n{web_context}"
    

    prompt = f"""
    You are an expert sports quiz master. Your task is to generate a 4-question multiple-choice quiz about {sport} at a {difficulty} difficulty level.
    
    Use the following verified context to build your questions. Do not hallucinate outside of this information if possible.
    
    CONTEXT DETAILS:
    {unified_context}
    
    Format each question EXACTLY as follows with clear double line breaks between lines:
    
    ### Question [Number]
    [Question text here]
    
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    
    **Correct Answer:** [Single Letter, e.g., A]
    
    **Explanation:** [Detailed background reasoning quoting from the context details]
    
    ---
    """
    
    response = llm.invoke(prompt)
    
    if isinstance(response.content, list):
        clean_text = "".join([block.get("text", "") for block in response.content if isinstance(block, dict) and "text" in block])
        return clean_text, unified_context
        
    return response.content, unified_context
