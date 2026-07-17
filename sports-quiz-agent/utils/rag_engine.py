import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from utils.database import get_vector_store

def generate_sports_quiz(sport: str, difficulty: str) -> str:
    """
    Executes the RAG pipeline: retrieves local facts, searches the web, and generates a quiz.
    """
    # 1. Initialize the LLM (Gemini 1.5 Flash is excellent for speed and reasoning)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7 # Adds slight creativity for varied question formats
    )
    
    # 2. Retrieve Local Context (from ChromaDB)
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    local_docs = retriever.invoke(sport)
    
    if local_docs:
        local_context = " ".join([doc.page_content for doc in local_docs])
    else:
        local_context = "No specific local facts found."
    
    # 3. Retrieve Live Internet Context (from DuckDuckGo)
    search_tool = DuckDuckGoSearchRun()
    try:
        # Search the web for recent/historical facts about the sport
        web_context = search_tool.run(f"Top {sport} historical facts and recent trivia")
    except Exception as e:
        web_context = "Web search currently unavailable."
    
    # 4. Construct the Augmented Prompt
    prompt = f"""
    You are an expert sports quiz master. Your task is to generate a 3-question multiple-choice quiz about {sport} at a {difficulty} difficulty level.
    
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
    
    # 5. Generate and return the LLM response
    response = llm.invoke(prompt)
    return response.content