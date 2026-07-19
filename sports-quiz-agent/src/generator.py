"""
src/generator.py — RAG orchestration layer.
Pulls context from ChromaDB + DuckDuckGo, builds a grounded prompt,
and calls the OpenAI Chat Completions API to generate quiz questions.
"""

from openai import OpenAI

from src.config import OPENAI_API_KEY
from src.database import query_historic_facts
from src.search import get_live_news_context


# Difficulty-specific guidance injected into the user prompt
_DIFFICULTY_GUIDE = {
    "Easy":   "Focus on basic, well-known facts: famous records, popular winners, founding years.",
    "Medium": "Include specific statistics, exact years, tournament names, and player achievements.",
    "Hard":   "Target obscure records, exact scores, lesser-known milestones, and historical edge cases.",
}


def compile_quiz_data(sport, difficulty):
    """
    Full RAG pipeline:
        1. Retrieve historical facts from ChromaDB (offline vector store).
        2. Retrieve live news from DuckDuckGo (real-time web search).
        3. Merge both into a unified context string.
        4. Build a structured anti-hallucination prompt.
        5. Call OpenAI GPT and return the quiz + context.

    Args:
        sport:      Target sport (e.g., "Cricket").
        difficulty: Quiz difficulty — "Easy", "Medium", or "Hard".

    Returns:
        A tuple of (raw_quiz_string, unified_context_string).
    """
    # ── 1.  Historical context from ChromaDB ─────────────────────────────────
    db_query   = f"{sport} history cup world championships records achievements"
    db_matches = query_historic_facts(sport=sport, query_text=db_query, n_results=2)
    # FIX: explicit empty-list guard before joining
    db_context = "\n".join(db_matches) if db_matches else "No offline historical data available."

    # ── 2.  Live news context from DuckDuckGo ────────────────────────────────
    web_context = get_live_news_context(sport)

    # ── 3.  Merge both context streams ───────────────────────────────────────
    unified_context = (
        f"=== HISTORICAL FACTS ===\n{db_context}\n\n"
        f"=== LIVE INTERNET NEWS ===\n{web_context}"
    )

    # ── 4.  Build the grounded system prompt ─────────────────────────────────
    system_instruction = (
        "You are an expert sports quiz creator. Your ONLY job is to write "
        "multiple-choice quiz questions based strictly on the CONTEXT DETAILS provided below. "
        "You must NEVER hallucinate, invent, or introduce any fact not explicitly stated in the context. "
        "If the context is limited, generate fewer but fully accurate questions.\n\n"
        f"CONTEXT DETAILS:\n{unified_context}"
    )

    diff_guidance = _DIFFICULTY_GUIDE.get(difficulty, _DIFFICULTY_GUIDE["Medium"])

    user_prompt = (
        f"Generate exactly 4 to 5 unique multiple-choice questions for the sport: {sport}.\n"
        f"Difficulty: {difficulty}.\n"
        f"Difficulty guidance: {diff_guidance}\n\n"
        "IMPORTANT RULES:\n"
        "- Use ONLY facts explicitly stated in the CONTEXT DETAILS in the system prompt.\n"
        "- Each question must have exactly four answer options: A, B, C, D.\n"
        "- Only one option is correct per question.\n"
        "- The Explanation must quote or directly reference the context text.\n\n"
        "Format EACH question EXACTLY as shown below "
        "(including the --- separator at the end of each question):\n\n"
        "Question: [Your question text here]\n"
        "A) [Option A]\n"
        "B) [Option B]\n"
        "C) [Option C]\n"
        "D) [Option D]\n"
        "Correct Answer: [Single uppercase letter only, e.g., B]\n"
        "Explanation: [One to two sentences citing specific facts from the context above]\n"
        "---"
    )

    # ── 5.  Call OpenAI Chat Completions API ─────────────────────────────────
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.6,    # Lower = more deterministic and factually consistent
        max_tokens=1800,    # Sufficient for 4–5 questions with full explanations
    )

    return response.choices[0].message.content, unified_context
