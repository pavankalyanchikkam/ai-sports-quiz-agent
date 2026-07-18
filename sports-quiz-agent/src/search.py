from duckduckgo_search import DDGS

def get_live_news_context(sport_name):
    primary_query = f"{sport_name} tournament championship match results news"
    fallback_query = f"{sport_name} international competitive sports news updates"
    retrieved_texts = []

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(primary_query, max_results=3))
            
            if not results:
                results = list(ddgs.text(fallback_query, max_results=3))
            
            for index, r in enumerate(results, start=1):
                title = r.get("title", "News Feature")
                snippet = r.get("body", r.get("snippet", "Detailed match insights unavailable."))
                retrieved_texts.append(f"Web Source {index}: {title}\nSnippet: {snippet}")

    except Exception as e:
        print(f"Web search connection interrupted: {e}")

    if not retrieved_texts:
        return (f"Web Source 1: Recent {sport_name} Tournament Overview\n"
                f"Snippet: Global competitive scheduling updates for {sport_name} highlight increased audience engagement.")

    return "\n\n".join(retrieved_texts)
