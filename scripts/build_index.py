# scripts/build_index.py
import subprocess
import sys

def main():
    # Run your package module so relative imports work
    cmd = [sys.executable, "-m", "src.ingest.indexer"]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()