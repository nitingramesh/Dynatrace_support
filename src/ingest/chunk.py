import re
from typing import List

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    if not text:
        return []

    # split into sentences (simple + good enough for POC)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks: List[str] = []
    current = ""

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        if len(current) + 1 + len(s) <= chunk_size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            current = s

    if current:
        chunks.append(current)

    # add overlap by prefixing last N chars of previous chunk
    if overlap > 0 and len(chunks) > 1:
        final_chunks: List[str] = []
        prev_tail = ""
        for c in chunks:
            if prev_tail:
                c = (prev_tail + " " + c).strip()
            final_chunks.append(c)
            prev_tail = c[-overlap:]
        return final_chunks

    return chunks