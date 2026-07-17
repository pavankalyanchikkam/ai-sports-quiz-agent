import streamlit as st
import os
from dotenv import load_dotenv
from utils.database import seed_database
from utils.rag_engine import generate_sports_quiz

load_dotenv()

@st.cache_resource
def initialize_app():
    seed_database()
    return True

initialize_app()

st.set_page_config(page_title="AI Sports Quiz Agent", page_icon="🏆")

st.title("🏆 AI-Powered Sports Quiz Agent")
st.markdown("""
Welcome! This agent uses **RAG (Retrieval-Augmented Generation)** to create fact-checked sports quizzes. 
It pulls context from a local **ChromaDB** and live **web searches** before generating questions via Gemini.
""")

st.divider()

# --- MOVED TO SIDEBAR AS PER INSTRUCTIONS ---
st.sidebar.header("Quiz Settings")
sport_input = st.sidebar.text_input("Enter a Sport:", placeholder="e.g., Cricket")
difficulty_level = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

if st.sidebar.button("Generate Quiz 🚀", use_container_width=True):
    
    if not sport_input.strip():
        st.sidebar.warning("Please enter a sport to generate the quiz.")
    else:
        with st.spinner(f"Agent is scanning databases and the web for {sport_input} facts..."):
            try:
                # Now unpacks BOTH the quiz output and the context used
                quiz_output, context_used = generate_sports_quiz(sport_input, difficulty_level)
                
                st.success("Quiz Generated Successfully!")
                st.markdown("### Your Custom Quiz")
                st.info(quiz_output)
                
                # --- ADDED AUDIT EXPANDER AS PER INSTRUCTIONS ---
                with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
                    st.code(context_used, language="markdown")
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")
