# Handover Report: Social Welfare Law RAG System Debugging
**Date:** 2025-12-30
**Project:** Law Scraping & Search System

## 1. Project Overview
A RAG (Retrieval-Augmented Generation) system for searching Japanese Social Welfare Laws using Google Gemini Embeddings and ChromaDB. The goal is to provide accurate article retrieval for broad and specific welfare queries.

## 2. Current Status
- **Database**:
    - `SQLite`: Contains raw text of 14 key welfare laws (recently fixed: "Disability Abuse Prevention Law" is now present).
    - `ChromaDB`: Contains vector embeddings for all articles.
- **Search Logic (`app.py`)**:
    - **Hybrid Search Strategy**:
        1. **Static Dictionary Match**: Checks `LAW_ALIAS_MAP` for specific keywords (e.g., "虐待" -> Search 4 specific abuse laws).
        2. **AI Intent Recognition (New)**: If no static match, asks Gemini to map the query (e.g., "自立支援") to specific confirmed law names.
        3. **Fallback**: Standard Vector Similarity Search against the entire database.
    - **Ranking Logic**:
        - Fetches *all* articles for targeted laws (`collection.get`).
        - Calculates Cosine Similarity in Python (to avoid ChromaDB query instability).
        - **Guaranteed Diversity (Top-3)**: Ensures at least 3 articles from each targeted law are included in the pool before sorting.

## 3. The Core Issue: "Child Welfare Law Dominance"
Despite the above logic, queries like "自立支援" (Independence Support) or other general terms overwhelmingly return results from **"Child Welfare Law" (児童福祉法)**.
The user perception is that the system "has not left the mockup stage."

### Potential Causes to Investigate in Next Session:
1.  **AI Intent Misinterpretation**: The LLM might be explicitly including "Child Welfare Law" in its recommendation list for almost every query because the law is huge and covers many topics.
2.  **Fallback Triggering**: The AI Intent phase might be failing (exception or empty response), causing a fallback to raw vector search where "Child Welfare Law" (having the most articles) statistically significantly dominates the top results.
3.  **UI Feedback Missing**: We are not clearly showing *which* laws were selected by the AI, so we cannot tell if it's a selection error or a ranking error.


## 4. Recent Fixes (Verified)
- **Missing Data Fixed**: "Disability Abuse Prevention Law" was missing from DB... (See previous report).
- **Search Robustness**: Switched from `collection.query` to `collection.get`... (See previous report).
- **AI Intent Debug UI**: Added detailed law list display in `app.py` when AI selects laws.
- **Child Welfare Law Mitigation**: 
    - Updated System Prompt with negative constraints to avoid selecting Child Welfare Law for generic queries.
    - Implemented "Penalty Logic" in Fallback Search: If query does not contain child-related keywords (e.g. "子供", "保育"), penalize "Child Welfare Law" results by adding 0.15 to distance.
    - Verified (via `test_results.txt`) that "Child Welfare Law" does not dominate results for generic queries like "相談".

## 5. Action Plan for Next Session
1.  **Category Search**: Move away from pure Law Name matching. Implement broad category tags (Elderly, Disability, Child, Poverty) in metadata and filter by that first.
2.  **Verify AI Intent Key**: Investigation showed `gemini-1.5-flash` might be unavailable or API key has restricted scope. Reverted to `gemini-pro`. User should verify if AI Intent detection works in their environment.
3.  **UI Feedback**: Check if the new "Detailed Law List" in UI is helpful.


## 6. Crucial Files
- `src/interface/app.py`: Main search logic, Intent Recognition, and Reranking.
- `src/infrastructure/egov_api.py`: Data fetching logic.
- `src/core/models.py`: Pydantic models (Schema).
- `verify_logic.py`, `check_sqlite.py`: Debugging scripts.

## 7. Environment
- **OS**: Windows
- **API**: Google Gemini (Embeddings + Generative)
- **DB**: ChromaDB (Vector), SQLite (Raw)

## 8. Rust Migration (2025-12-30)
The backend has been completely rewritten in **Rust** for performance and stability.
- **Architecture**:
    - **Frontend**: Streamlit (Python) - Acts as a thin client.
    - **Backend**: Rust (Axum Web Framework) - Handles Search, Logic, and Embedding.
- **Search Logic**:
    - All logic (Intent Detection, Penalty/Boost, Vector Search) has been ported to Rust.
    - **In-Memory Index**: Data is exported from ChromaDB to `backend/data/index.json` and loaded into RAM for ultra-fast search.
- **Setup**:
    1. **Start System**: `python start_app.py` (Launches both Backend and Frontend automatically)
    2. **Features**:
        - **Law Search**: AI-powered vector search with intent recognition.
        - **Browse Mode**: Read full text of laws with sidebar navigation.

- **Deployment (Render.com)**:
    1. **Runtime**: Select **Docker**.
    2. **Environment Variables**: Add `GOOGLE_API_KEY`.
    3. **Plan**: Free Tier (Zero cost).
    4. **Status**: Verified & Deployed Success ✅

## 9. Security Improvements (2025-12-31)
The following security measures have been implemented to ensure safe operation:

1.  **Vulnerability Scanning (Sentinel Tool)**:
    - Created `Sentinel`, a custom security scanner in Rust.
    - Scans for project type (Rust/Python), runs standard audit tools (`cargo-audit`, `pip-audit`, `bandit`), and detects hardcoded secrets.
    - **Outcome**: Fixed "XML External Entity" vulnerability in Python scripts and added timeouts to all HTTP requests to prevent DoS.

2.  **Guardrails (Backend Protection)**:
    - Implemented `guardrails.rs` in the Rust backend.
    - **Active Checks**:
        - **Prompt Injection**: Blocks inputs like "Ignore previous instructions".
        - **XSS/Scripting**: Blocks HTML/JS injection attempts.
        - **Length Limit**: Rejects queries > 1000 chars to prevent memory exhaustion DoS.

3.  **Security Starter Kit**:
    - Packaged these tools for re-use in future projects.
    - Location: `C:\Users\user\.gemini\security-starter-kit`
    - Contains `sentinel.exe`, `start-scan.ps1`, `secure_requirements.txt`, and Guardrails templates.

## 10. Data Update (2025-12-31)
Added **Mental Health Social Worker Act (精神保健福祉士法)** to the database.

- **Objective**: Improve search relevance for queries related to mental health social workers.
- **Actions Taken**:
    1.  Updated `populate_db.py` to target "精神保健福祉士法" (ID: `409AC0000000131`).
    2.  Fetched latest XML data from e-Gov API and stored in SQLite.
    3.  Re-indexed the entire database (embeddings) using `indexer.py`.
    4.  Exported new vector data to `backend/data/index.json`.
- **Status**: Complete. The Rust backend will now search this law when restarted.
    - Total Articles for this law: 51



