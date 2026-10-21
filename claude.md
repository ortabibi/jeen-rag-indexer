# Project: Jeen AI – Part 2: Document Indexing & Retrieval

A Python CLI that indexes PDF/DOCX files into PostgreSQL (pgvector) using Gemini embeddings, and supports semantic search.

## Requirements (from the assignment)
- `index_documents.py --file <path> --strategy <fixed|sentence|paragraph>`
- `search.py --query "<text>"`
- Extract clean text from PDF/DOCX.
- Three chunking strategies: fixed-size with overlap, sentence-based, paragraph-based.
- Embeddings: `gemini-embedding-001` (google-genai SDK).
- Storage: PostgreSQL + pgvector. Table columns at least: id, chunk_text, embedding, filename, split_strategy, created_at.
- Search: vector similarity search.
- Error handling: missing file, unsupported file type, document with no text, embedding failure, database connection failure, empty search results.
- Deliverables: requirements.txt, README.md in English (installation, environment variables, run examples, sample output).

## Tech
- Python 3.13, virtual environment in `./venv`
- Packages: google-genai, psycopg[binary], pgvector, pypdf, python-docx, python-dotenv
- Database: Neon (hosted PostgreSQL with pgvector)

## Rules
- Secrets: `GEMINI_API_KEY` and `POSTGRES_URL` come only from `.env`. Never hardcode, print, log, or read back secrets or `.env`.
- No hardcoded file paths.
- Clean, modular code: separate modules for text extraction, chunking, embeddings, and database. Short docstrings on every function.
- Clear, friendly error messages. Never show a raw stack trace to the user.
- Work step by step: one small change at a time, then stop so I can test it.
- Before creating or changing files, briefly say what you're about to do.
- Explain new concepts simply. I'm a student learning this.
- Don't add features or files that weren't asked for.
- Always use the `./venv` environment for running and installing.
- After I confirm a stage works, give me the exact git commands to commit and push it, with a clear commit message (for example: "Stage 1: text extraction"). Never commit .env or secrets.
- Every time I give you a new task, start your reply with the word "Hopa!" so I know you've read these rules.