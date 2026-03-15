import re

COMMAND_PATTERNS = [
    r"^\s*kubectl\s+.*",
    r"^\s*helm\s+.*",
    r"^\s*oc\s+.*",
    r"^\s*oneagentctl.*",
    r"^\s*dtctl.*",
    r"^\s*dynatrace-operator.*",
]

def extract_command_context(context: str) -> str:
    lines = context.splitlines()
    command_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in COMMAND_PATTERNS):
            command_lines.append(stripped)
            continue

        if (
            any(cmd in stripped.lower() for cmd in ["kubectl", "helm", "oc", "oneagentctl", "dtctl"])
            and any(flag in stripped for flag in ["--", "-n ", "-f ", "-l "])
        ):
            command_lines.append(stripped)

    unique_commands = list(dict.fromkeys(command_lines))
    return "\n".join(unique_commands[:50])