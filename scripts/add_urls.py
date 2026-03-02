# scripts/add_urls.py
import sys
from pathlib import Path
from urllib.parse import urlparse

SEED = Path("data/seed_urls.txt")

def is_valid_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def main():
    SEED.parent.mkdir(parents=True, exist_ok=True)
    existing = set()

    if SEED.exists():
        for line in SEED.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            existing.add(line)

    incoming = [a.strip() for a in sys.argv[1:] if a.strip()]
    if not incoming:
        print("Usage: python scripts/add_urls.py <url1> <url2> ...")
        sys.exit(1)

    added = 0
    with SEED.open("a", encoding="utf-8") as f:
        for u in incoming:
            if not is_valid_url(u):
                print(f"❌ Invalid URL: {u}")
                continue
            if u in existing:
                print(f"↩️ Already exists: {u}")
                continue
            f.write(u + "\n")
            existing.add(u)
            added += 1

    print(f"✅ Added {added} new URL(s). Total now: {len(existing)}")

if __name__ == "__main__":
    main()