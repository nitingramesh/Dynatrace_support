TraceSage = Meaning

TraceSage = A wise AI that understands system traces and helps diagnose problems.


TraceSage is a local, documentation-driven AI assistant designed to help support engineers quickly surface relevant troubleshooting paths, identify likely causes, and reference official documentation with citations.



Unlike generic AI chatbots, TraceSage only answers using curated documentation and community sources defined in `data/seed_urls.txt`.



This ensures:

- Grounded answers

- Source transparency

- No hallucinated troubleshooting steps

- Controlled knowledge boundaries



---



## 🎯 Purpose



Support engineers spend significant time:

- Searching Dynatrace documentation

- Scanning community posts

- Reviewing troubleshooting guides

- Cross-referencing multiple sources



TraceSage accelerates this process by:



1. Ingesting curated documentation sources

2. Converting them into a searchable knowledge base

3. Retrieving relevant evidence snippets

4. Generating grounded answers with citations

5. Caching responses for repeated queries

---

## Architecture

- **Retriever**: ChromaDB + sentence-transformers
- **Text LLM**: Generates grounded explanations and troubleshooting steps
- **Command LLM**: Extracts exact commands from retrieved documentation
- **UI**: Streamlit

## Current Features

- Topic-based retrieval
- All-topics fallback retrieval
- Keyword fallback over indexed/raw documentation
- Separate explanation and command generation
- Intent-aware UI:
  - Concept questions show explanation only
  - Command/uninstall questions show commands separately

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py