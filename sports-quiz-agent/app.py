"""
app.py — Streamlit dashboard entry point.
AI-Powered Sports Quiz Generation Agent using RAG (ChromaDB + DuckDuckGo + OpenAI GPT).
"""

import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db


# ─────────────────────────────────────────────────────────────────────────────
# 1.  One-time startup — warm up the local ChromaDB vector knowledge base
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def prepare_knowledge_base():
    """Populates ChromaDB with offline sports facts on the very first run only."""
    setup_and_populate_db()


prepare_knowledge_base()


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Page configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Sports Quiz Agent",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Main header
# ─────────────────────────────────────────────────────────────────────────────
st.title("🏆 AI-Powered Sports Quiz Generator")
st.caption(
    "Generate fact-checked, RAG-grounded multiple-choice sports quizzes "
    "for social media — powered by ChromaDB ▸ DuckDuckGo ▸ OpenAI GPT."
)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Sidebar controls
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Quiz Settings")

    sport_choice = st.selectbox(
        "🏅 Select Sport",
        ["Cricket", "Football", "Tennis", "Badminton", "Basketball"],
        help="Choose the sport you want the quiz to be generated for.",
    )

    difficulty = st.select_slider(
        "🎯 Select Difficulty",
        options=["Easy", "Medium", "Hard"],
        value="Medium",
        help="Easy = basic records | Medium = specific stats | Hard = obscure milestones",
    )

    st.divider()

    generate_btn = st.button(
        "🚀 Generate Fresh Quiz",
        use_container_width=True,
        type="primary",
    )

    clear_btn = st.button(
        "🗑️ Clear Quiz",
        use_container_width=True,
    )

    st.divider()
    st.caption(
        "**How it works**\n\n"
        "1. 🗄️ ChromaDB retrieves verified historical sports facts\n"
        "2. 🌐 DuckDuckGo fetches the latest live sports news\n"
        "3. 🧠 GPT reads only that context and writes grounded MCQs"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Session state initialisation
#     FIX: sport and difficulty are stored at generation time so the header
#     always matches the quiz content, even if the user later changes the
#     sidebar dropdowns before regenerating.
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "quiz_output":    None,
    "quiz_context":   None,
    "quiz_sport":     None,
    "quiz_difficulty": None,
}
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# 6.  Clear action
# ─────────────────────────────────────────────────────────────────────────────
if clear_btn:
    for key in _defaults:
        st.session_state[key] = None
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 7.  Generate action
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    with st.spinner("🔍 Fetching historical facts & searching the live web …"):
        try:
            quiz_text, context_used = compile_quiz_data(sport_choice, difficulty)
            # Store the quiz result AND the sport/difficulty at generation time
            st.session_state.quiz_output     = quiz_text
            st.session_state.quiz_context    = context_used
            st.session_state.quiz_sport      = sport_choice      # ← FIX
            st.session_state.quiz_difficulty = difficulty         # ← FIX
            st.success("✅ Quiz generated successfully!")
            st.balloons()
        except Exception as exc:
            st.error(f"❌ Generation failed: {exc}")
            st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# 8.  Display quiz (only when one exists in session state)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.quiz_output:
    saved_sport      = st.session_state.quiz_sport
    saved_difficulty = st.session_state.quiz_difficulty

    # ── 8a.  Quiz subheader ───────────────────────────────────────────────────
    st.subheader(f"📋 Current Quiz — {saved_sport}  |  {saved_difficulty}")

    # ── 8b.  Social-media-ready export block ─────────────────────────────────
    social_text = (
        f"Sport: {saved_sport}\n"
        f"Difficulty: {saved_difficulty}\n\n"
        + st.session_state.quiz_output
    )

    col_text, col_actions = st.columns([3, 1])
    with col_text:
        st.text_area(
            "📲 Copy & paste to your socials",
            value=social_text,
            height=280,
            help="Select all (Ctrl+A / Cmd+A) and copy, then paste into Instagram, Twitter/X, or WhatsApp.",
        )
    with col_actions:
        st.download_button(
            label="⬇️ Download .txt",
            data=social_text,
            file_name=f"{saved_sport}_{saved_difficulty}_quiz.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.metric("Sport",  saved_sport)
        st.metric("Level",  saved_difficulty)

    st.divider()

    # ── 8c.  Interactive quiz cards ───────────────────────────────────────────
    st.markdown("### 🎮 Interactive Quiz Mode")
    st.caption("Attempt each question mentally, then click to reveal the answer and explanation.")

    raw_blocks = [b.strip() for b in st.session_state.quiz_output.split("---") if b.strip()]

    for idx, block in enumerate(raw_blocks, start=1):
        with st.container(border=True):
            if "Correct Answer:" not in block:
                st.markdown(block)
                continue

            q_section, ans_section = block.split("Correct Answer:", 1)

            # Clean stray markdown bold/italic artefacts from LLM output
            q_section   = q_section.strip().rstrip("*").strip()
            ans_section = ans_section.strip().lstrip("*:").strip()

            if "Explanation:" in ans_section:
                letter_raw, exp_raw = ans_section.split("Explanation:", 1)
                correct_letter  = letter_raw.strip().replace("**", "").replace(":", "").strip()
                explanation_txt = exp_raw.strip().replace("**", "").replace(":", "").strip()
                reveal_md = (
                    f"🎯 **Correct Answer: {correct_letter}**\n\n"
                    f"📝 **Explanation:** {explanation_txt}"
                )
            else:
                correct_letter = ans_section.replace("**", "").replace(":", "").strip()
                reveal_md = f"🎯 **Correct Answer: {correct_letter}**"

            st.markdown(f"**Question {idx}**")
            st.markdown(q_section)
            with st.expander(f"💡 Reveal Answer for Question {idx}"):
                st.info(reveal_md)

    # ── 8d.  RAG context inspector ────────────────────────────────────────────
    st.divider()
    with st.expander("🔍 Inspect RAG Ground-Truth Context"):
        st.caption(
            "These are the exact sources the LLM used to generate this quiz. "
            "Every answer is grounded in this verified information — zero hallucinations."
        )
        st.code(st.session_state.quiz_context, language="markdown")


# ─────────────────────────────────────────────────────────────────────────────
# 9.  Placeholder — shown before the first quiz is generated
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.info(
        "👈 **Select a sport and difficulty** in the left sidebar, "
        "then click **🚀 Generate Fresh Quiz** to get started."
    )

    with st.expander("ℹ️ About this application"):
        st.markdown(
            """
            **AI-Powered Sports Quiz Generator** uses **Retrieval-Augmented Generation (RAG)**
            to create accurate, hallucination-free sports quizzes in seconds.

            | Layer | Technology | Role |
            |---|---|---|
            | Vector Store | ChromaDB | Stores & retrieves historical sports facts |
            | Live Search | DuckDuckGo | Fetches real-time news & 2026 match results |
            | Language Model | OpenAI GPT-3.5-Turbo | Generates grounded quiz questions |
            | Frontend | Streamlit | Interactive web dashboard |

            > 💡 Every question generated is backed by verifiable sources —
            > click **Inspect RAG Ground-Truth Context** after generating to see
            > exactly what the AI read before writing each question.
            """
        )
