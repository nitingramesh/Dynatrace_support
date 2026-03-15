import streamlit as st

from src.retrieval.search import Retriever
from run_copilot import keyword_fallback_context, dedupe_sources
from src.retrieval.command_retriever import extract_command_context
from src.retrieval.troubleshooting_retriever import extract_troubleshooting_context
from src.llm.structured_llm import generate_text_answer
from src.llm.final_llm import generate_command_answer


st.set_page_config(
    page_title="TraceSage",
    page_icon="🧠",
    layout="centered"
)

# Dynatrace logo
st.image("dynatrace_logo.png", width=200)

st.title("TraceSage – Dynatrace AI Assistant")
st.caption("AI-powered Dynatrace Documentation Support")


# -----------------------------
# UI INPUTS
# -----------------------------
topic_input = st.selectbox(
    "Topic",
    ["All", "kubernetes", "oneagent", "dem"]
)

question = st.text_area(
    "Question",
    placeholder="Ask a Dynatrace troubleshooting question...",
    height=120
)

run = st.button("Get Answer", type="primary")


# -----------------------------
# LOAD RETRIEVER
# -----------------------------
@st.cache_resource
def load_retriever():
    return Retriever(
        persist_dir="chroma_db",
        collection_name="dt_public_docs"
    )


retriever = load_retriever()


# -----------------------------
# HELPERS
# -----------------------------
def normalize_topic(t: str):
    if not t or t == "All":
        return None
    return t


def detect_intent(question: str) -> str:
    q = (question or "").lower()

    if any(x in q for x in ["what is", "explain", "how does", "role of", "difference between"]):
        return "concept"

    if any(x in q for x in ["command", "commands", "kubectl", "run", "execute", "cli"]):
        return "commands"

    if any(x in q for x in ["uninstall", "delete", "remove", "cleanup"]):
        return "uninstall"

    return "troubleshooting"


def question_needs_commands(question: str, intent: str) -> bool:
    q = (question or "").lower()

    if intent in {"commands", "uninstall"}:
        return True

    return any(x in q for x in ["command", "commands", "kubectl", "run", "execute", "cli"])


def format_retrieved_docs(docs, label: str) -> str:
    if not docs:
        return ""

    blocks = [f"=== {label} ==="]

    for i, d in enumerate(docs, start=1):
        title = d.get("title", "(no title)")
        url = d.get("url", "")
        text = d.get("text", "") or ""

        blocks.append(
            f"[{i}] {title}\n"
            f"URL: {url}\n"
            f"CONTENT:\n{text}\n"
        )

    return "\n\n".join(blocks)


# -----------------------------
# MAIN LOGIC
# -----------------------------
if run and question.strip():

    topic = normalize_topic(topic_input)

    # detect intent
    intent = detect_intent(question)
    needs_commands = question_needs_commands(question, intent)

    # -----------------------------
    # RETRIEVE CONTEXT
    # -----------------------------
    res = retriever.query(question, topic=topic, k=18)

    res_all = []
    if topic is not None:
        res_all = retriever.query(question, topic=None, k=15)

    combined_context = ""

    combined_context += format_retrieved_docs(
        res,
        "TOP SOURCES (topic-filtered)"
    )

    if res_all:
        combined_context += "\n\n" + format_retrieved_docs(
            res_all,
            "TOP SOURCES (all-topics fallback)"
        )

    # -----------------------------
    # KEYWORD FALLBACK
    # -----------------------------
    fallback_ctx = keyword_fallback_context(
        question,
        max_docs=4
    )

    if fallback_ctx:
        combined_context += (
            "\n\n=== FALLBACK EVIDENCE (keyword match) ===\n"
            + fallback_ctx + "\n"
        )

    combined_context = dedupe_sources(combined_context)

    # -----------------------------
    # EXTRACT CONTEXT TYPES
    # -----------------------------
    text_context = extract_troubleshooting_context(combined_context)

    command_context = extract_command_context(combined_context)

    if fallback_ctx:
        fallback_command_context = extract_command_context(fallback_ctx)

        if fallback_command_context:
            command_context += "\n" + fallback_command_context

    # -----------------------------
    # DEBUG PRINTS (optional)
    # -----------------------------
    print("===== TEXT CONTEXT =====")
    print(text_context[:3000])

    print("===== COMMAND CONTEXT =====")
    print(command_context[:3000])

    # -----------------------------
    # GENERATE ANSWERS
    # -----------------------------
    with st.spinner("TraceSage is analyzing Dynatrace documentation..."):

        text_answer = generate_text_answer(
            question,
            text_context
        )

        command_answer = generate_command_answer(
            question,
            command_context
        )

    # -----------------------------
    # DISPLAY RESULTS
    # -----------------------------
    if intent == "concept":
        st.subheader("Explanation")
    else:
        st.subheader("Answer")

    st.markdown(text_answer)

    if needs_commands and command_context.strip():
        st.markdown("### Commands")
        st.code(command_answer, language="bash")

else:
    st.info(
        "Select a topic (optional), enter a question, and click **Get Answer**."
    )