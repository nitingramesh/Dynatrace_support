# scripts/ingest_urls.py
import json
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SEED = Path("data/seed_urls.txt")
OUT = Path("data/raw/docs.jsonl")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SupportCopilot/1.0)"}

def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)

def load_seed_urls() -> list[str]:
    if not SEED.exists():
        raise FileNotFoundError(f"Missing {SEED}")
    raw = SEED.read_text(encoding="utf-8").splitlines()
    urls = []
    for line in raw:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        s = s.strip('"').strip("'").rstrip(",")
        urls.append(s)
    # unique preserve order
    return list(dict.fromkeys(urls))

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    urls = load_seed_urls()
    print(f"✅ Loaded {len(urls)} seed URLs")

    # overwrite each run (simple + clean demo)
    if OUT.exists():
        OUT.unlink()

    ok = 0
    fail = 0

    with OUT.open("a", encoding="utf-8") as f:
        for i, url in enumerate(urls, start=1):
            try:
                print(f"[{i}/{len(urls)}] Fetching: {url}")
                r = requests.get(url, headers=HEADERS, timeout=25)
                r.raise_for_status()
                text = clean_text(r.text)
                doc = {
                    "url": url,
                    "title": url,          # optional: you can parse <title> later
                    "topic": "unknown",    # optional: you can auto-tag later
                    "source_type": "seed_urls",
                    "text": text,
                }
                f.write(json.dumps(doc) + "\n")
                ok += 1
                time.sleep(0.5)  # polite crawling
            except Exception as e:
                print(f"❌ Failed: {url} -> {e}")
                fail += 1

    print(f"\n✅ Done. Success={ok}, Failed={fail}")
    print(f"📄 Output: {OUT}")

if __name__ == "__main__":
    main()