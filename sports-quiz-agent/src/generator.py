from duckduckgo_search import DDGS

def get_live_news_context(sport_name):
    """
    Searches the live web for recent sport news, matches, or events.
    Includes strict fallbacks to bypass rate limits.
    """
    primary_query = f"{sport_name} latest tournament results championship news 2026"
    fallback_query = f"{sport_name} sports news updates"
    retrieved_texts = []

    print(f"Executing web search for: '{primary_query}'...")
    try:
        with DDGS() as ddgs:
            # Tier 1: Attempt highly specific query
            results = list(ddgs.text(primary_query, max_results=3))
            
            # Tier 2: Attempt broad query if specific query yields nothing
            if not results:
                print("Primary search returned empty. Trying fallback query...")
                results = list(ddgs.text(fallback_query, max_results=3))
            
            for index, r in enumerate(results, start=1):
                title = r.get("title", "No Title")
                snippet = r.get("body", "No Snippet Content Available")
                retrieved_texts.append(f"Web Source {index}: {title}\nSnippet: {snippet}")

    except Exception as e:
        print(f"Web Search fell back or failed: {e}")
        return "No live news retrieved due to temporary search engine rate limits. Generating based on historical facts only."

    # Tier 3: Handle completely empty returns safely
    if not retrieved_texts:
        return "No recent search updates found for the specified sport."
        
    return "\n\n".join(retrieved_texts)
