from duckduckgo_search import DDGS

def get_live_news_context(sport_name):
    """
    Searches the live web for recent sport news.
    Failsafe: Returns a completely empty string if blocked or empty to prevent filler text questions.
    """
    primary_query = f"{sport_name} tournament championship match results news 2026"
    fallback_query = f"{sport_name} international competitive sports news updates"
    retrieved_texts = []

    print(f"Executing web search context capture for: '{primary_query}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(primary_query, max_results=3))
            
            if not results:
                print("Primary online query returned empty. Deploying secondary fallback parameters...")
                results = list(ddgs.text(fallback_query, max_results=3))
            
            for index, r in enumerate(results, start=1):
                title = r.get("title", "").strip()
                snippet = r.get("body", r.get("snippet", "")).strip()
                if title or snippet:
                    retrieved_texts.append(f"Web Source {index}: {title}\nSnippet: {snippet}")

    except Exception as e:
        print(f"Web search connection interrupted or rate-limited: {e}")
        return ""

    # CRITICAL FALLBACK: Return absolute empty string if no valid text retrieved.
    if not retrieved_texts:
        return ""

    return "\n\n".join(retrieved_texts)
