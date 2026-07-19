"""
src/database.py — ChromaDB interaction layer.
Handles initialisation, population, and vector-similarity querying.
"""

import os
import json
import chromadb
from chromadb.utils import embedding_functions


# ─────────────────────────────────────────────────────────────────────────────
# ChromaDB client
# ─────────────────────────────────────────────────────────────────────────────

def get_chroma_client():
    """Returns a persistent ChromaDB client that saves data to ./chroma_db/."""
    return chromadb.PersistentClient(path="./chroma_db")


# ─────────────────────────────────────────────────────────────────────────────
# Path helper
# ─────────────────────────────────────────────────────────────────────────────

def resolve_data_path():
    """
    Returns the absolute path to data/sports_facts.json regardless of
    whether the process is launched from the project root or the src/ folder.
    """
    # This file lives at src/database.py → go one level up → data/
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.abspath(os.path.join(base_dir, "..", "data", "sports_facts.json"))
    if os.path.exists(candidate):
        return candidate
    return "./data/sports_facts.json"


# ─────────────────────────────────────────────────────────────────────────────
# Setup / population
# ─────────────────────────────────────────────────────────────────────────────

def setup_and_populate_db():
    """
    Initialises the ChromaDB collection and populates it from sports_facts.json.

    Uses upsert() so re-running the app never creates duplicate entries.
    Safe to call on every startup — if data already exists it returns early.
    """
    client       = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="sports_production_knowledge_v5",
        embedding_function=embedding_fn,
    )

    # ── Early-exit if already populated ──────────────────────────────────────
    # FIX: use > 0 instead of >= 10 so any non-empty collection is respected
    if collection.count() > 0:
        print(f"[DB] Collection already contains {collection.count()} facts — skipping re-population.")
        return collection

    # ── Load source JSON ──────────────────────────────────────────────────────
    json_file_path = resolve_data_path()
    if not os.path.exists(json_file_path):
        print(f"[DB][ERROR] Source file not found: {json_file_path}")
        return collection

    try:
        with open(json_file_path, "r", encoding="utf-8") as fh:
            facts_list = json.load(fh)

        documents  = []
        metadatas  = []
        ids        = []

        for idx, item in enumerate(facts_list):
            documents.append(item["fact"])
            metadatas.append({"sport": item["sport"]})
            ids.append(f"{item['sport'].lower()}_fact_{idx}")

        # upsert is idempotent — safe to call multiple times
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"[DB] Successfully stored {len(documents)} facts into ChromaDB.")

    except Exception as exc:
        print(f"[DB][ERROR] Population failed: {exc}")

    return collection


# ─────────────────────────────────────────────────────────────────────────────
# Query
# ─────────────────────────────────────────────────────────────────────────────

def query_historic_facts(sport, query_text, n_results=2):
    """
    Queries ChromaDB for documents related to the given sport using
    vector similarity search filtered by sport metadata.

    Args:
        sport:       The target sport name (must match JSON 'sport' field exactly).
        query_text:  The search string converted to a vector for similarity matching.
        n_results:   Maximum number of documents to retrieve.

    Returns:
        A list of matching document strings, or a sensible fallback list.
    """
    client       = get_chroma_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="sports_production_knowledge_v5",
        embedding_function=embedding_fn,
    )

    # Lazy populate if the collection is somehow empty at query time
    if collection.count() == 0:
        print("[DB] Collection empty at query time — triggering lazy population.")
        setup_and_populate_db()

    try:
        # First check how many documents exist for this sport
        sport_docs    = collection.get(where={"sport": sport})
        available_ids = sport_docs.get("ids", [])

        if not available_ids:
            print(f"[DB] No facts found for sport '{sport}' — using fallback text.")
            return [
                f"Historical records confirm that {sport} has a rich and prestigious "
                f"international competitive legacy across major world tournaments."
            ]

        actual_n = min(n_results, len(available_ids))

        results = collection.query(
            query_texts=[query_text],
            n_results=actual_n,
            where={"sport": sport},
        )

        documents = results.get("documents", [[]])
        if documents and documents[0]:
            return documents[0]

        # Fallback: return raw docs for this sport if query returns nothing
        return sport_docs.get("documents", [])[:actual_n]

    except Exception as exc:
        print(f"[DB][ERROR] Query failed for '{sport}': {exc}")
        return [
            f"The sport of {sport} is celebrated globally for its thrilling tournaments "
            f"and iconic championship moments spanning decades of elite competition."
        ]
