# scripts/validate_urls.py
from pathlib import Path

SEED = Path("data/seed_urls.txt")

def main():
    if not SEED.exists():
        print(f"❌ Missing: {SEED}")
        return

    raw = SEED.read_text(encoding="utf-8").splitlines()
    urls = []
    for line in raw:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # clean common paste formats: quotes and trailing commas
        s = s.strip('"').strip("'").rstrip(",")
        urls.append(s)

    unique = list(dict.fromkeys(urls))  # keep order, remove duplicates
    print(f"Lines in file: {len(raw)}")
    print(f"Valid URL lines (after cleaning): {len(urls)}")
    print(f"Unique URLs: {len(unique)}")
    print("\nFirst 10:")
    for u in unique[:10]:
        print(" -", u)

if __name__ == "__main__":
    main()