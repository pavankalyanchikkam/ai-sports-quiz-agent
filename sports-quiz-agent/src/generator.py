from openai import OpenAI
from src.config import OPENAI_API_KEY
from src.database import query_historic_facts
from src.search import get_live_news_context

def compile_quiz_data(sport, difficulty):
    db_query = f"{sport} history cup world championships records"
    # Pulling 5 results from Chroma to match the 5 questions asked
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=5)
    db_context = "\n".join(db_matches)

    web_context = get_live_news_context(sport)
    unified_context = f"=== HISTORICAL FACTS ===\n{db_context}\n\n=== LIVE INTERNET NEWS ===\n{web_context}"

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_instruction = (
        "You are an expert sports quiz creator. Your job is to write multiple-choice quizzes "
        "relying strictly on the provided Context. Avoid hallucinations.\n\n"
        "CRITICAL DIFFICULTY INSTRUCTION:\n"
        "For Hard difficulty, questions must require specific knowledge such as exact years, scores, "
        "player statistics, record holders, or lesser-known historical facts. Avoid general knowledge.\n\n"
        "STRICT CONTEXT USAGE RULE:\n"
        "Use web search results ONLY as background context to ensure freshness. Never create a "
        "question that asks what an article reports, what updates highlight, or what a website says. "
        "All 5 questions must test specific sports facts: dates, scores, records, player names, or rules.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}"
    )

    user_prompt = (
        f"Generate exactly 5 unique multiple-choice questions for the sport: {sport}.\n"
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content, unified_context
