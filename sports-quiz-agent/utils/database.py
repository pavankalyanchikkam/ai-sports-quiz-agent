import os
import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_vector_store():
    """
    Initializes and returns the ChromaDB vector store using Google GenAI embeddings.
    """
    # Initialize the embedding model using Gemini
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Directory to store the local database persistently
    persist_directory = "./chroma_db"
    
    # Create or load the vector store
    vector_store = Chroma(
        collection_name="sports_facts",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    return vector_store

def seed_database():
    """
    Seeds the database with some initial sports facts if it's empty.
    """
    vector_store = get_vector_store()
    
    # Fetch existing documents to check if the database is empty
    existing_docs = vector_store.get()
    
    if len(existing_docs['ids']) == 0:
        # Dummy facts for the agent to retrieve locally
        facts = [
            "The fastest goal in World Cup history was scored by Hakan Şükür in 10.8 seconds.",
            "Cricket legend Don Bradman retired with a Test batting average of 99.94.",
            "Michael Phelps holds the record for the most Olympic gold medals, with 23.",
            "Wimbledon is the oldest tennis tournament in the world, founded in 1877.",
            "The first official game of basketball was played in 1891 with peach baskets."
        ]
        
        # Add seed facts to the vector store
        vector_store.add_texts(
            texts=facts,
            metadatas=[{"source": "seed_data"} for _ in facts]
        )
        print("Local ChromaDB seeded successfully with initial facts.")