import os
import json
import chromadb
from chromadb.utils import embedding_functions

def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client saving to disk."""
    return chromadb.PersistentClient(path="./chroma_db")

def resolve_data_path():
    """Determines the absolute system path to the static JSON dataset."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    alternative_path = os.path.abspath(os.path.join(base_dir, "..", "data", "sports_facts.json"))
    if os.path.exists(alternative_path):
        return alternative_path
    return "./data/sports_facts.json"

def setup_and_populate_db():
    """Reads the static JSON file and upserts elements to a fresh vector collection."""
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # V10 identifier isolates this version completely from old corrupted caches
    collection = client.get_or_create_collection(
        name="sports_evaluation_collection_v10",
        embedding_function=embedding_fn
    )

    if collection.count() >= 25:
        return collection

    json_file_path = resolve_data_path()
    if not os.path.exists(json_file_path):
        print(f"Error: Raw fact data file not found at {json_file_path}")
        return collection

    try:
        with open(json_file_path, "r") as f:
            facts_list = json.load(f)

        documents, metadata_list, ids = [], [], []

        for idx, item in enumerate(facts_list):
            documents.append(item["fact"])
            metadata_list.append({"sport": item["sport"]})
            ids.append(f"{item['sport'].lower()}_fact_{idx}")

        collection.upsert(
            documents=documents,
            metadatas=metadata_list,
            ids=ids
        )
        print(f"Successfully vectorized and stored {len(documents)} facts.")
    except Exception as e:
        print(f"Error handling database insertion routine: {e}")

    return collection

def query_historic_facts(sport, query_text, n_results=5):
    """Queries ChromaDB using explicit metadata structural filters."""
    client = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="sports_evaluation_collection_v10",
        embedding_function=embedding_fn
    )

    try:
        if collection.count() == 0:
            setup_and_populate_db()

        # Isolate exactly how many facts exist for this specific sport
        sport_docs = collection.get(where={"sport": sport})
        
        if not sport_docs or not sport_docs.get("ids") or len(sport_docs["ids"]) == 0:
            return [f"Historical records indicate that {sport} possesses a deep competitive legacy."]

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
        print(f"ChromaDB retrieval layer error encountered: {e}")
        return [f"The legacy of {sport} is highlighted by prestigious historical milestones."]
