import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db

# 1. Warm-up and initialize the vector DB with our offline facts on startup
@st.cache_resource
def prepare_knowledge_base():
    setup_and_populate_db()

prepare_knowledge_base()

# 2. Set Page configurations
st.set_page_config(page_title="Sports Quiz Agent", page_icon="🏆", layout="centered")

st.title("🏆 AI-Powered Sports Quiz Generator")
st.write("Challenge yourself or generate engaging social media content! Powered by RAG (ChromaDB + Web Search).")

# 3. Sidebar inputs
st.sidebar.header("Quiz Settings")
sport_choice = st.sidebar.selectbox("Select Sport", ["Cricket", "Football", "Badminton", "Tennis", "Basketball"])
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

# 4. Initialize session state to remember quizzes across page interactions
if "quiz_output" not in st.session_state:
    st.session_state.quiz_output = None
    st.session_state.quiz_context = None

# Button to trigger compilation pipeline
if st.sidebar.button("Generate Fresh Quiz", use_container_width=True):
    with st.spinner("Fetching historical facts & scouring the live web..."):
        try:
            quiz_text, context_used = compile_quiz_data(sport_choice, difficulty)
            st.session_state.quiz_output = quiz_text
            st.session_state.quiz_context = context_used
            st.success("Quiz created successfully!")
        except Exception as e:
            st.error(f"Failed to generate quiz: {e}")

# 5. Display the generated quiz
if st.session_state.quiz_output:
    st.subheader(f"Current Quiz: {sport_choice} ({difficulty})")

    st.text_area("Generated Quiz Output (Copy paste to your socials)",
                 value=st.session_state.quiz_output,
                 height=350)

    st.divider()
    st.markdown("### Interactive Quiz Mode")

    raw_questions = [q.strip() for q in st.session_state.quiz_output.split("---") if q.strip()]
    for idx, q_block in enumerate(raw_questions):
        if "Correct Answer:" in q_block:
            parts = q_block.split("Correct Answer:")
            question_and_options = parts[0].strip().rstrip("*").strip()
            raw_answer_segment = parts[1].strip().lstrip("*").strip().lstrip(":").strip()

            if "Explanation:" in raw_answer_segment:
                exp_parts = raw_answer_segment.split("Explanation:")
                correct_letter = exp_parts[0].strip().replace("**", "").replace(":", "").strip()
                explanation_content = exp_parts[1].strip().replace("**", "").replace(":", "").strip()
                final_dropdown_text = f"🎯 **Correct Answer:** {correct_letter}\n\n📝 **Explanation:** {explanation_content}"
            else:
                clean_letter = raw_answer_segment.replace("**", "").replace(":", "").strip()
                final_dropdown_text = f"🎯 **Correct Answer:** {clean_letter}"

            with st.container(border=True):
                st.markdown(question_and_options)
                with st.expander(f"💡 Reveal Answer & Explanation for Question {idx + 1}"):
                    st.info(final_dropdown_text)
        else:
            with st.container(border=True):
                st.markdown(q_block)

    st.divider()
    # Expandable window showcasing the "ground truth context" for audit purposes
    with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
        st.code(st.session_state.quiz_context, language="markdown")
