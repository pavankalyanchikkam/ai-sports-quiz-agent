import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db

# 1. Warm up vector base instances on initial startup execution
@st.cache_resource
def prepare_knowledge_base():
    setup_and_populate_db()

prepare_knowledge_base()

# 2. Page Configuration Layout Setup
st.set_page_config(page_title="AI Sports Quiz Agent", page_icon="🏆", layout="centered")

st.title("🏆 AI-Powered Sports Quiz Generator")
st.write("Generate fact-checked multiple-choice quizzes for social media using RAG (ChromaDB + Web Search).")

# 3. Structural Configurations Input Sliders
st.sidebar.header("Quiz Configurations")
sport_choice = st.sidebar.selectbox("Select Sport", ["Cricket", "Football", "Tennis", "Badminton", "Basketball"])
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

# 4. Global State Tracking Instantiations
if "quiz_output" not in st.session_state:
    st.session_state.quiz_output = None
    st.session_state.quiz_context = None

if st.sidebar.button("Generate Fresh Quiz", use_container_width=True):
    with st.spinner("Retrieving facts and compiling search streams..."):
        try:
            quiz_text, context_used = compile_quiz_data(sport_choice, difficulty)
            st.session_state.quiz_output = quiz_text
            st.session_state.quiz_context = context_used
            st.success("Quiz created successfully!")
        except Exception as e:
            st.error(f"Failed to compile quiz pipeline: {e}")

# 5. Core Interface Display Blocks
if st.session_state.quiz_output:
    st.subheader(f"Current Quiz: {sport_choice} ({difficulty})")

    # Construct explicit matching output signature prefix matching rubric constraints
    full_social_output = f"Sport: {sport_choice}\nDifficulty: {difficulty}\n\n" + st.session_state.quiz_output

    st.text_area("Generated Quiz Output (Ready for Social Media)",
                 value=full_social_output,
                 height=400)

    st.divider()
    st.markdown("### Interactive Quiz Mode")

    raw_questions = [q.strip() for q in st.session_state.quiz_output.split("---") if q.strip()]
    
    for idx, q_block in enumerate(raw_questions):
        if not q_block:
            continue
            
        if "Correct Answer:" in q_block:
            parts = q_block.split("Correct Answer:")
            question_and_options = parts[0].strip()
            raw_answer_segment = parts[1].strip()

            if "Explanation:" in raw_answer_segment:
                exp_parts = raw_answer_segment.split("Explanation:")
                correct_letter = exp_parts[0].strip()
                explanation_content = exp_parts[1].strip()
                final_dropdown_text = f"🎯 **Correct Answer:** {correct_letter}\n\n📝 **Explanation:** {explanation_content}"
            else:
                final_dropdown_text = f"🎯 **Correct Answer:** {raw_answer_segment}"

            with st.container(border=True):
                st.markdown(question_and_options)
                with st.expander(f"💡 Reveal Answer & Explanation for Question {idx + 1}"):
                    st.info(final_dropdown_text)
        else:
            with st.container(border=True):
                st.markdown(q_block)

    st.divider()
    with st.expander("🔍 Inspect Ground Truth (RAG Context Used)"):
        st.code(st.session_state.quiz_context, language="markdown")
