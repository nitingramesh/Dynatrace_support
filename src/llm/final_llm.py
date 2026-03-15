import requests


def generate_command_answer(
    question: str,
    command_context: str,
    model: str = "llama3.1:8b",
) -> str:
    prompt = f"""
You are a Dynatrace command extraction assistant.

STRICT RULES:
1. Use ONLY the information in the provided COMMAND_CONTEXT.
2. Return ONLY the exact commands relevant to the user's question.
3. Do NOT explain the commands.
4. Do NOT summarize.
5. Do NOT invent commands.
6. Preserve commands exactly as written in the context.
7. If no commands are found, return exactly:
   No relevant commands found in the provided documentation.

COMMAND_CONTEXT:
{command_context}

QUESTION:
{question}

COMMANDS:
"""

    print("[LLM-COMMAND] Generating command answer...")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    print("[LLM-COMMAND] Response received.")
    response.raise_for_status()
    return response.json().get("response", "").strip()