import requests

def generate_answer(question: str, context: str, model: str = "llama3.1:8b") -> str:
    prompt = f"""
You are a senior SRE and Kubernetes support engineer.

STRICT RULES (must follow):
1) Use ONLY the information in the provided CONTEXT.
2) Cite ONLY using the source IDs that appear in the SOURCES list below, like [1], [2].
3) Never invent citations. If you cannot support a claim with SOURCES, say:
   "I don't have enough information in the documentation."
4) If you cite something, it must match the SOURCES list exactly (no [7] if only [1]-[5] exist).

Output format:
Clear Explanation:
<short paragraph>

Steps:
- step 1 ...
- step 2 ...

Citations:
- [1] <one-line why used>
- [2] <one-line why used>

CONTEXT (includes SOURCES + SNIPPETS):
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()