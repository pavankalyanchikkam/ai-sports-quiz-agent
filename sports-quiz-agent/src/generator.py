from openai import OpenAI
from src.config import OPENAI_API_KEY
from src.database import query_historic_facts
from src.search import get_live_news_context

def compile_quiz_data(sport, difficulty):
    db_query = f"{sport} history cup world championships records rules stats"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=5)
    db_context = "\n".join(db_matches)

    web_context = get_live_news_context(sport)
    
    unified_context = f"=== HISTORICAL FACTS ===\n{db_context}"
    if web_context:
        unified_context += f"\n\n=== LIVE INTERNET NEWS ===\n{web_context}"

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_instruction = (
        "You are an expert sports quiz creator. Your job is to write multiple-choice quizzes "
        "relying strictly on the provided Context. Avoid hallucinations. Do not use facts not "
        "found in the Context below. Keep all details completely accurate to the text context.\n\n"
        "CRITICAL DIFFICULTY INSTRUCTION:\n"
        "Adjust the complexity of the questions strictly based on the requested difficulty level. "
        "For Hard difficulty, questions must require specific knowledge such as exact years, scores, "
        "player statistics, record holders, or lesser-known historical facts. Avoid general knowledge "
        "that casual fans would know (e.g., 'which country is best at X').\n\n"
        "STRICT CONTEXT USAGE RULE:\n"
        "All 5 questions must test specific real-world sports facts: dates, scores, records, player names, or rules. "
        "Never create questions about what an article reports, what a website headline says, where to find scores, "
        "or what updates highlight. Do not formulate questions based on search metadata or website site descriptions."
    )

    user_prompt = (
        f"Generate exactly 5 unique multiple-choice questions for the sport: {sport}.\n"
        f"Difficulty target: {difficulty}.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}\n\n"
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
        temperature=0.3,
    )

    return response.choices[0].message.content, unified_context
