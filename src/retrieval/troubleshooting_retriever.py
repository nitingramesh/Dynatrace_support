TROUBLE_KEYWORDS = [
    "troubleshoot",
    "troubleshooting",
    "issue",
    "issues",
    "error",
    "errors",
    "failure",
    "failed",
    "verify",
    "check",
    "diagnose",
    "restart",
    "crashloopbackoff",
    "not reporting",
    "not working",
    "timeout",
    "uninstall",
    "delete",
    "cleanup",
    "remove",
    "stuck",
]


def extract_troubleshooting_context(context: str) -> str:
    matched = []

    for line in context.splitlines():
        lower = line.lower().strip()
        if not lower:
            continue

        if any(keyword in lower for keyword in TROUBLE_KEYWORDS):
            matched.append(line.strip())

    unique_lines = list(dict.fromkeys(matched))

    if not unique_lines:
        return ""

    return "\n".join(unique_lines[:50])