import requests


def generate_text_answer(
    question: str,
    text_context: str,
    model: str = "llama3.1:8b",
) -> str:
    prompt = f"""
You are a Dynatrace technical support engineer.

STRICT RULES:
1. Use ONLY the information in the provided TEXT_CONTEXT.
2. Do NOT invent commands, URLs, or facts.
3. If the context is insufficient, say:
   "I could not find enough troubleshooting information in the Dynatrace documentation."
4. Focus on explanation and troubleshooting guidance only.
5. Do NOT output commands unless absolutely necessary.

OUTPUT FORMAT:
Issue Summary:
- Briefly explain the issue.

Troubleshooting Steps:
- Provide bullet points only if supported by the context.

TEXT_CONTEXT:
{text_context}

QUESTION:
{question}

ANSWER:
"""

    print("[LLM-TEXT] Generating troubleshooting answer...")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    print("[LLM-TEXT] Response received.")
    response.raise_for_status()
    return response.json().get("response", "").strip()