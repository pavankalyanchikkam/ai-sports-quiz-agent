import os
import json
import chromadb
from chromadb.utils import embedding_functions

def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client saving to disk."""
    return chromadb.PersistentClient(path="./chroma_db")

def setup_and_populate_db(json_file_path="./data/sports_facts.json"):
    """Reads the offline JSON facts, creates a collection, and populates it."""
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # FORCED NEW COLLECTION NAME to bypass cache issues
    collection = client.get_or_create_collection(
        name="sports_knowledge_base_v1",
        embedding_function=embedding_fn
    )

    if collection.count() > 0:
        print(f"Database already populated with {collection.count()} facts.")
        return collection

    if not os.path.exists(json_file_path):
        print(f"Error: Raw fact data file not found at {json_file_path}")
        return collection

    with open(json_file_path, "r") as f:
        facts_list = json.load(f)

    documents = []
    metadata_list = []
    ids = []

    for idx, item in enumerate(facts_list):
        documents.append(item["fact"])
        metadata_list.append({"sport": item["sport"]})
        ids.append(f"fact_{idx}")

    collection.add(
        documents=documents,
        metadatas=metadata_list,
        ids=ids
    )
    print(f"Successfully vectorized and stored {len(documents)} facts.")
    return collection

def query_historic_facts(sport, query_text, n_results=2):
    """Queries ChromaDB for historic documents relating to a sport."""
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="sports_knowledge_base_v1",
        embedding_function=embedding_fn
    )

    try:
        sport_docs = collection.get(where={"sport": sport})
        available_count = len(sport_docs["ids"])

        if available_count == 0:
            print(f"No facts found in ChromaDB for sport: {sport}")
            return []

        actual_n = min(n_results, available_count)

        results = collection.query(
            query_texts=[query_text],
            n_results=actual_n,
            where={"sport": sport}
        )

        return results.get("documents", [[]])[0]

    except Exception as e:
        print(f"ChromaDB query error: {e}")
        return []
