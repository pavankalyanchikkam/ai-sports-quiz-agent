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

# --- STEP 2: SIDEBAR SETTINGS ---
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
                
                # --- STEP 3: FACTOR-PROOFED INTERACTIVE QUESTION CARD PARSING ---
                raw_questions = [q.strip() for q in quiz_output.split("---") if q.strip()]
                
                for idx, q_block in enumerate(raw_questions):
                    if "Correct Answer:" in q_block:
                        # Split by the main label text
                        parts = q_block.split("Correct Answer:")
                        
                        # Clean up the question text and strip any left-over markdown bold stars
                        question_and_options = parts[0].strip().rstrip("*").strip()
                        
                        # Isolate the remaining answer and explanation segment
                        raw_answer_segment = parts[1].strip().lstrip("*").strip().lstrip(":").strip()
                        
                        # Sub-split the explanation out to build a pristine layout inside the card
                        if "Explanation:" in raw_answer_segment:
                            exp_parts = raw_answer_segment.split("Explanation:")
                            correct_letter = exp_parts[0].strip().replace("**", "").replace(":", "").strip()
                            explanation_content = exp_parts[1].strip().replace("**", "").replace(":", "").strip()
                            
                            final_dropdown_text = f"🎯 **Correct Answer:** {correct_letter}\n\n📝 **Explanation:** {explanation_content}"
                        else:
                            clean_letter = raw_answer_segment.replace("**", "").replace(":", "").strip()
                            final_dropdown_text = f"🎯 **Correct Answer:** {clean_letter}"
                        
                        # Render cleanly into the interface container
                        with st.container(border=True):
                            st.markdown(question_and_options)
                            
                            with st.expander(f"💡 Reveal Answer & Explanation for Question {idx + 1}"):
                                st.markdown(final_dropdown_text)
                    else:
                        # Safe fallback layout block
                        with st.container(border=True):
                            st.markdown(q_block)
                
                st.divider()
                
                # --- STEP 4: GROUND TRUTH AUDIT EXPANDER ---
                with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
                    st.code(context_used, language="markdown")
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")
