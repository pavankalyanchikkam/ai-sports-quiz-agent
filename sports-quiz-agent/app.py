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

# --- STEP 1: FORCE WIDE LAYOUT TO INCREASE WIDTH & REDUCE SCROLLING ---
st.set_page_config(page_title="AI Sports Quiz Agent", page_icon="🏆", layout="wide")

st.title("🏆 AI-Powered Sports Quiz Agent")
st.markdown("""
Welcome! This agent uses **RAG (Retrieval-Augmented Generation)** to create fact-checked sports quizzes. 
It pulls context from a local **ChromaDB** and live **web searches** before generating questions via Gemini.
""")

st.divider()

# Sidebar Settings
st.sidebar.header("Quiz Settings")
sport_input = st.sidebar.text_input("Enter a Sport:", placeholder="e.g., Cricket")
difficulty_level = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

if st.sidebar.button("Generate Quiz 🚀", use_container_width=True):
    
    if not sport_input.strip():
        st.sidebar.warning("Please enter a sport to generate the quiz.")
    else:
        with st.spinner(f"Agent is scanning databases and the web for {sport_input} facts..."):
            try:
                quiz_output, context_used = generate_sports_quiz(sport_input, difficulty_level)
                
                st.success("Quiz Generated Successfully!")
                st.markdown("### Your Custom Quiz")
                
                # --- STEP 2: DYNAMICALLY PARSE QUESTIONS INTO INTERACTIVE CARDS ---
                # Split the raw output text into individual questions using the '---' delimiter
                raw_questions = [q.strip() for q in quiz_output.split("---") if q.strip()]
                
                for idx, q_block in enumerate(raw_questions):
                    # Check if the block contains answer information
                    if "Correct Answer:" in q_block:
                        # Separate the question/options from the answer/explanation
                        parts = q_block.split("Correct Answer:")
                        question_and_options = parts[0].strip()
                        answer_and_explanation = "**Correct Answer:** " + parts[1].strip()
                        
                        # Render the question block inside a clean UI container
                        with st.container(border=True):
                            st.markdown(question_and_options)
                            
                            # Interactive dropdown: Hides the answer until the user clicks it!
                            with st.expander(f"💡 Reveal Answer & Explanation for Question {idx + 1}"):
                                st.markdown(answer_and_explanation)
                    else:
                        # Fallback case if formatting varies slightly
                        with st.container(border=True):
                            st.markdown(q_block)
                
                st.divider()
                
                # Ground Truth Expander at the very bottom
                with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
                    st.code(context_used, language="markdown")
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")
