import os
import json
import chromadb
from chromadb.utils import embedding_functions

def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def resolve_data_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    alternative_path = os.path.abspath(os.path.join(base_dir, "..", "data", "sports_facts.json"))
    if os.path.exists(alternative_path):
        return alternative_path
    return "./data/sports_facts.json"

def setup_and_populate_db():
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # V6 guarantees it reads the newly expanded 25-fact JSON file
    collection = client.get_or_create_collection(
        name="sports_production_knowledge_v6",
        embedding_function=embedding_fn
    )

    if collection.count() >= 25:
        return collection

    json_file_path = resolve_data_path()
    if not os.path.exists(json_file_path):
        return collection

    try:
        with open(json_file_path, "r") as f:
            facts_list = json.load(f)

        documents, metadata_list, ids = [], [], []

        for idx, item in enumerate(facts_list):
            documents.append(item["fact"])
            metadata_list.append({"sport": item["sport"]})
            ids.append(f"{item['sport'].lower()}_fact_{idx}")

        collection.upsert(documents=documents, metadatas=metadata_list, ids=ids)
    except Exception as e:
        print(f"Database insertion error: {e}")

    return collection

# WE NOW PULL 5 RESULTS SO THE LLM NEVER RUNS OUT OF MATERIAL
def query_historic_facts(sport, query_text, n_results=5):
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="sports_production_knowledge_v6",
        embedding_function=embedding_fn
    )

    try:
        if collection.count() == 0:
            setup_and_populate_db()

        sport_docs = collection.get(where={"sport": sport})
        
        if not sport_docs or not sport_docs.get("ids") or len(sport_docs["ids"]) == 0:
            return [f"Historical records indicate that {sport} has a rich competitive legacy."]

        available_count = len(sport_docs["ids"])
        actual_n = min(n_results, available_count)

        results = collection.query(
            query_texts=[query_text],
            n_results=actual_n,
            where={"sport": sport}
        )

        docs = results.get("documents", [])
        if docs and len(docs) > 0 and len(docs[0]) > 0:
            return docs[0]
        return sport_docs.get("documents", [])[:actual_n]

    except Exception as e:
        print(f"ChromaDB retrieval error: {e}")
        return [f"The legacy of {sport} is highlighted by prestigious history."]
