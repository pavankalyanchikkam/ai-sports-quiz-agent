from google import genai
from google.genai import types
from src.config import GOOGLE_API_KEY
from src.database import query_historic_facts
from src.search import get_live_news_context

def compile_quiz_data(sport, difficulty):
    """
    1. Gathers context from ChromaDB (Historical).
    2. Gathers context from DuckDuckGo (Live news).
    3. Blends them inside a grounded prompt.
    4. Connects to Gemini and generates the structured quiz.
    """
    # Create query to run against ChromaDB
    db_query = f"{sport} history cup championships rules records"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=2)
    db_context = "\n".join(db_matches) if db_matches else "No offline historic data recorded."

    # Search the live web
    web_context = get_live_news_context(sport)

    # Combine historical and web contexts
    unified_context = f"=== HISTORICAL FACTS ===\n{db_context}\n\n=== LIVE INTERNET NEWS ===\n{web_context}"

    # Instantiate the Gemini API client
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Constructing a structured system prompt
    system_instruction = (
        "You are an expert sports quiz creator. Your job is to write multiple-choice quizzes "
        "relying strictly on the provided Context. Avoid hallucinations. Do not use facts not "
        "found in the Context below. If facts are scarce, make do with what you have, "
        "but keep details completely accurate to the text context.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}"
    )

    user_prompt = (
        f"Generate exactly 3 unique multiple-choice questions for the sport: {sport}.\n"
        f"Difficulty target: {difficulty}.\n\n"
        "Format each question exactly as follows so my program can parse it:\n"
        "Question: [Question text here]\n"
        "A) [Option A]\n"
        "B) [Option B]\n"
        "C) [Option C]\n"
        "D) [Option D]\n"
        "Correct Answer: [Single Letter, e.g., A]\n"
        "Explanation: [Detailed background reasoning quoting from the context details]\n"
        "---"
    )

    # Make API call - utilizing 1.5-flash to completely bypass the limit: 0 error
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        ),
        contents=user_prompt
    )

    return response.text, unified_context
