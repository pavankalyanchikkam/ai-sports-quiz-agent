from openai import OpenAI
from src.config import OPENAI_API_KEY
from src.database import query_historic_facts
from src.search import get_live_news_context

def compile_quiz_data(sport, difficulty):
    """Assembles all RAG vectors and text streams to generate the grounded quiz."""
    db_query = f"{sport} history cup world championships records"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=2)
    db_context = "\n".join(db_matches)

    web_context = get_live_news_context(sport)
    unified_context = f"=== HISTORICAL FACTS ===\n{db_context}\n\n=== LIVE INTERNET NEWS ===\n{web_context}"

    client = OpenAI(api_key=OPENAI_API_KEY)

    # FIX 1: Strict constraints forbidding questions about web sources or search engines
    system_instruction = (
        "You are an expert sports quiz creator. Your job is to write multiple-choice quizzes "
        "relying strictly on the provided Context. Avoid hallucinations. Do not use facts not "
        "found in the Context below. Keep all details completely accurate to the text context.\n\n"
        "CRITICAL CONSTRAINTS:\n"
        "1. Only generate questions about real-world sports facts, tournament records, history, rules, or athletes.\n"
        "2. NEVER generate a question about where to find scores, which website covers a sport, or mention the text source itself (e.g., do NOT ask questions about 'Web Source 1' or 'ESPN'). The quiz must feel like a genuine sports trivia contest, not an assessment of the provided text snippets.\n"
        "3. Ensure the explanation validates the sports fact itself without mentioning phrases like 'According to Web Source 1'.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}"
    )

    # FIX 2: Explicit difficulty enforcement guidelines for the LLM
    difficulty_guidelines = (
        "- Easy: basic rules, player counts, well-known grand champions.\n"
        "- Medium: famous tournaments, milestone records, key years.\n"
        "- Hard: highly specific statistics, lesser-known historical deep-dives, exact dates, and match scores."
    )

    user_prompt = (
        f"Generate exactly 4 unique multiple-choice questions for the sport: {sport}.\n"
        f"Difficulty target: {difficulty}.\n\n"
        f"Adhere strictly to these difficulty guidelines:\n{difficulty_guidelines}\n\n"
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
    )

    return response.choices[0].message.content, unified_context
