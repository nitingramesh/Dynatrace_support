import streamlit as st

from run_copilot import Retriever  # or wherever Retriever is imported from in run_copilot
from src.llm import generate_answer
from run_copilot import keyword_fallback_context, dedupe_sources  # adjust imports to your file structure

import streamlit as st

st.set_page_config(
    page_title="TraceSage",
    page_icon="🧠",
    layout="centered"
)

# Add Dynatrace logo
st.image("dynatrace_logo.png", width=200)

st.title("TraceSage – Dynatrace AI Assistant")
st.caption("AI-powered Dynatrace Documentation Support")


# --- Inputs
topic_input = st.selectbox("Topic", ["All", "kubernetes", "oneagent", "dem"])
question = st.text_area("Question", placeholder="Ask a Dynatrace troubleshooting question...", height=120)

run = st.button("Get Answer", type="primary")

@st.cache_resource
def load_retriever():
    return Retriever(persist_dir="chroma_db", collection_name="dt_public_docs")

retriever = load_retriever()

def normalize_topic(t: str):
    if not t or t == "All":
        return None
    return t

if run and question.strip():
    topic = normalize_topic(topic_input)

    # Retrieve context (same as your CLI)
    res = retriever.query(question, topic=topic, k=18)
    res_all = retriever.query(question, topic=None, k=15) if topic is not None else ""

    combined_context = ""
    combined_context += "=== TOP SOURCES (topic-filtered) ===\n" + str(res) + "\n"
    if res_all:
        combined_context += "\n=== TOP SOURCES (all-topics fallback) ===\n" + str(res_all) + "\n"

    fallback_ctx = keyword_fallback_context(question, max_docs=4)
    if fallback_ctx:
        combined_context += "\n=== FALLBACK EVIDENCE (keyword match) ===\n" + fallback_ctx + "\n"

    combined_context = dedupe_sources(combined_context)

    # ✅ Exec UI requirement: show ONLY grounded answer
    with st.spinner("Generating grounded answer..."):
        answer = generate_answer(question, combined_context)

    st.subheader("Answer")
    st.markdown(answer)

else:
    st.info("Select a topic (optional), enter a question, and click **Get Answer**.")