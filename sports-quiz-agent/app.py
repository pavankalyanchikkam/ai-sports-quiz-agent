import streamlit as st
import os
from dotenv import load_dotenv
from utils.database import seed_database
from utils.rag_engine import generate_sports_quiz

# 1. Load environment variables (pulls API keys from .env file)
load_dotenv()

# 2. Ensure the local database is seeded on startup
@st.cache_resource
def initialize_app():
    seed_database()
    return True

initialize_app()

# 3. Streamlit UI Configurations
st.set_page_config(page_title="AI Sports Quiz Agent", page_icon="🏆")

st.title("🏆 AI-Powered Sports Quiz Agent")
st.markdown("""
Welcome! This agent uses **RAG (Retrieval-Augmented Generation)** to create fact-checked sports quizzes. 
It pulls context from a local **ChromaDB** and live **web searches** before generating questions via Gemini.
""")

st.divider()

# 4. User Inputs
col1, col2 = st.columns(2)
with col1:
    sport_input = st.text_input("Enter a Sport:", placeholder="e.g., Cricket, Football, Tennis")
with col2:
    difficulty_level = st.selectbox("Select Difficulty:", ["Easy", "Medium", "Hard"])

# 5. Generation Logic
if st.button("Generate Quiz 🚀", use_container_width=True):
    
    # Validation checks
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("API Key not found! Please check your `.env` file.")
    elif sport_input.strip() == "":
        st.warning("Please enter a sport to generate the quiz.")
    else:
        # Trigger the RAG pipeline with a loading spinner
        with st.spinner(f"Agent is scanning databases and the web for {sport_input} facts..."):
            try:
                quiz_output = generate_sports_quiz(sport_input, difficulty_level)
                
                # Display output
                st.success("Quiz Generated Successfully!")
                st.markdown("### Your Custom Quiz")
                st.info(quiz_output)
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")

st.divider()
