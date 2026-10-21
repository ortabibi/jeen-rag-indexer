# Document Indexing & Semantic Search

A Python command-line tool that indexes PDF and DOCX files into PostgreSQL with
[pgvector](https://github.com/pgvector/pgvector), using Google's
`gemini-embedding-001` embeddings, and finds the passages most similar to a question.

- `index_documents.py` extracts the text, splits it into chunks with one of three strategies, embeds each chunk and saves it.
- `search.py` embeds a question and returns the most similar chunks by cosine similarity.

## Project structure

| File | What it does |
|---|---|
| `index_documents.py` | CLI: extract → chunk → embed → save |
| `search.py` | CLI: embed the query → vector search → print ranked results |
| `extraction.py` | Clean text extraction from PDF (pypdf) and DOCX (python-docx) |
| `chunking.py` | The three chunking strategies |
| `embeddings.py` | Gemini embeddings (google-genai SDK) |
| `db.py` | PostgreSQL connection, table setup, insert and search |
| `config.py` | Reads `GEMINI_API_KEY` and `POSTGRES_URL` from `.env` |
| `check_setup.py` | Quick test that the database and the Gemini API both work |
| `samples/` | Two sample documents, plus `edge-cases/` files for the error examples |

## Installation

Requires Python 3.13 (other recent 3.x versions should work) and a PostgreSQL
database with the pgvector extension available. This project was tested on
[Neon](https://neon.tech), which includes pgvector.

```bash
git clone https://github.com/ortabibi/jeen-rag-indexer.git
cd jeen-rag-indexer

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and fill in your own values. `.env` is ignored by
git, so your secrets are never committed.

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `POSTGRES_URL` | Connection string, e.g. `postgresql://user:password@host/dbname?sslmode=require` |

Check that both work:

```
$ python check_setup.py
Database: connected, table document_chunks is ready
Embedding dimensions: 768
Setup OK
```

The table `document_chunks` (and the `vector` extension) is created automatically on first use:

| Column | Type |
|---|---|
| `id` | `SERIAL PRIMARY KEY` |
| `chunk_text` | `TEXT` |
| `embedding` | `VECTOR(768)` |
| `filename` | `TEXT` |
| `split_strategy` | `TEXT` |
| `created_at` | `TIMESTAMP DEFAULT now()` |

## Usage

### Indexing

```
python index_documents.py --file <path> --strategy <fixed|sentence|paragraph>
```

```
$ python index_documents.py --file samples/user-guide.pdf --strategy paragraph
Extracted 3,970 characters
Created 19 chunks (paragraph)
Created 19 embeddings
Saved 19 chunks for user-guide.pdf
```

```
$ python index_documents.py --file samples/support-faq.docx --strategy fixed
Extracted 3,118 characters
Created 8 chunks (fixed)
Created 8 embeddings
Saved 8 chunks for support-faq.docx
```

Indexing the same file again with the same strategy replaces its old rows, so
there are no duplicates.

### Searching

```
python search.py --query "<text>" [--top-k 5] [--min-score 0.6] [--strategy fixed|sentence|paragraph]
```

| Option | Default | Meaning |
|---|---|---|
| `--query` | (required) | The question to search for |
| `--top-k` | 5 | Maximum number of results |
| `--min-score` | 0.6 | Hide results with a lower similarity |
| `--strategy` | all | Only search chunks made with this strategy |

Results are ranked by similarity (`1 − cosine distance`, higher is better). Long chunks are shortened in the output.

```
$ python search.py --query "login issue"
1. score 0.730 | user-guide.pdf | paragraph
   Troubleshooting login issues: if you see the message "Incorrect email or password", check for typing mistakes and make sure Caps Lock is off. If the page keeps returning to the login screen after you log in, your browser is probably blocking cookies. Allow cookies for nimbus.example.com and try agai...

2. score 0.728 | support-faq.docx | paragraph
   Login issues I can't log in to my account. What should I do? First, check that you are using the email address you registered with and that Caps Lock is off. If you still cannot log in, clear your browser cache and cookies, or try a private window. If the login page keeps reloading, make sure third-...

3. score 0.708 | support-faq.docx | fixed
   n, clear your browser cache and cookies, or try a private window. If the login page keeps reloading, make sure third-party cookies are allowed for nimbus.example.com. Why is my account locked after several login attempts? For your security, the account is locked for 15 minutes after five failed logi...

4. score 0.707 | user-guide.pdf | fixed
   eturning to the login screen after you log in, your browser is probably blocking cookies. Allow cookies for nimbus.example.com and try again. After five failed login attempts the account is locked for 15 minutes. This protects you from people trying to guess your password. You can wait, or unlock th...

5. score 0.704 | user-guide.pdf | fixed
   ld click "Log in with SSO" instead of entering a password. If SSO fails, ask your company administrator to check that your account is assigned to the app. 3. Resetting your password If you forgot your password, click "Forgot password?" on the login page and enter your email address. A password reset...
```

Filtering by strategy:

```
$ python search.py --query "login issue" --strategy sentence --top-k 2
1. score 0.694 | support-faq.docx | sentence
   Nimbus Workspace - Customer Support FAQ This FAQ answers the most common questions our support team receives about Nimbus Workspace. If your question is not covered here, contact us at support@nimbus.example.com. Login issues I can't log in to my account. What should I do? First, check that you are...

2. score 0.693 | support-faq.docx | sentence
   If the login page keeps reloading, make sure third-party cookies are allowed for nimbus.example.com. Why is my account locked after several login attempts? For your security, the account is locked for 15 minutes after five failed login attempts in a row. Wait 15 minutes and try again, or reset your...
```

An unrelated question returns no results instead of irrelevant ones:

```
$ python search.py --query "chocolate cake recipe"
No results found with similarity of at least 0.6. Try rephrasing the question or lowering --min-score.
```

## Chunking strategies

All sizes are in characters and are constants at the top of `chunking.py`.

| Strategy | How it works | Chunks (PDF / DOCX) |
|---|---|---|
| `fixed` | Windows of 500 characters, each overlapping the previous one by 100 | 10 / 8 |
| `sentence` | Whole sentences are grouped until a chunk would pass ~500 characters. A sentence is never split. | 9 / 7 |
| `paragraph` | One chunk per paragraph. Paragraphs under 100 characters (e.g. headings) are merged into the next one; paragraphs over 500 are split by sentences. | 19 / 14 |

**Comparison on the real search above.** Both strategies found the same passage
about the login page returning to the login screen, but:

- the **fixed** chunk starts mid-word, `"eturning to the login screen..."`, because it was cut at an exact character position. The 100-character overlap keeps the context in the neighbouring chunk, but the chunk itself is harder to read.
- the **paragraph** chunk starts cleanly, `"Troubleshooting login issues: ..."`, and holds one complete topic, and it scored highest (0.730).
- the **sentence** chunks always start and end on sentence boundaries, but can combine unrelated sentences (the first one above mixes the FAQ's introduction with the login section).

## Error handling

Every error prints one clear line starting with `Error:` and exits with code 1. No stack
traces and no secret values are shown. All six required cases, with their real output:

**1. Missing file**
```
$ python index_documents.py --file missing.pdf --strategy fixed
Error: File not found: missing.pdf
```

**2. Unsupported file type**
```
$ python index_documents.py --file samples/edge-cases/notes.txt --strategy fixed
Error: Unsupported file type: .txt (use .pdf or .docx)
```

**3. Document with no text**
```
$ python index_documents.py --file samples/edge-cases/empty.docx --strategy fixed
Error: No text found in empty.docx.
```

**4. Embedding failure** (an invalid `GEMINI_API_KEY`)
```
$ python index_documents.py --file samples/user-guide.pdf --strategy fixed
Extracted 3,970 characters
Created 10 chunks (fixed)
Error: Gemini API error (400): API key not valid. Please pass a valid API key. Check that GEMINI_API_KEY is valid.
```
Embedding runs before the database is opened, so a Gemini failure never changes stored data.

**5. Database connection failure** (a wrong `POSTGRES_URL`)
```
$ python search.py --query "login issue"
Error: Could not connect to the database. Check POSTGRES_URL in your .env file and your internet connection.
```

**6. Empty search results** (exit code 0, since the search itself worked)
```
$ python search.py --query "chocolate cake recipe"
No results found with similarity of at least 0.6. Try rephrasing the question or lowering --min-score.
```

## Design decisions

**Text extraction**
- **DOCX tables:** table text is extracted with one row per line and cells separated by ` | `, so it isn't lost.
- **PDF layout mode:** pypdf's normal mode returns no blank lines between paragraphs, so layout mode is used to keep them for the paragraph strategy.
- **Headers and footers:** lines that repeat in the first/last 3 lines of at least half the pages are removed (digits ignored, so "Page 1" and "Page 2" match). A document title that matches the running header is removed too.
- **Encrypted PDFs** are rejected with a clear error. Decrypting them is out of scope.

**Chunking**
- **Chunk size:** 500 characters, with 100 overlap for `fixed`. The sample documents are only ~3,000–4,000 characters, so smaller chunks give more precise results.
- **Sentence splitting:** a regex on `.`, `!` or `?` followed by whitespace, with no extra packages.

**Embeddings and storage**
- **768 dimensions:** `gemini-embedding-001` returns 3,072 numbers by default; we request 768 (`output_dimensionality`). It is one of Google's recommended sizes and makes each row 4× smaller. pgvector's HNSW index supports at most 2,000 dimensions, so 3,072 would block adding an index later.
- **Task types:** chunks are embedded as `RETRIEVAL_DOCUMENT` and queries as `RETRIEVAL_QUERY`, as Google recommends for search.
- **Re-indexing:** the old rows for the same filename + strategy are deleted, then the new ones inserted, in one transaction. If anything fails, the old rows are kept.
- **Stored filename:** only the file name (e.g. `user-guide.pdf`), not the full path, which is machine-specific and exposes folder structure.
- **Embed before saving:** the pipeline is extract → chunk → embed → save, so a Gemini failure never touches the database.

**Search**
- **Minimum score 0.6:** vector search always returns the closest rows, even when none are relevant. On the samples, "login issue" scored 0.70–0.73, a differently worded relevant question ("how do I get my money back") scored 0.61–0.65, and the unrelated "chocolate cake recipe" scored at most 0.53, so the default 0.6 sits between them. It can be changed with `--min-score`.
- **No vector index yet:** search does an exact scan with cosine distance (`<=>`). With a few dozen rows this takes milliseconds. An HNSW index is the next step at scale.

## Limitations

- Sentence splitting treats abbreviations like "e.g." or "Dr." as sentence ends.
- If a PDF heading sits very close to the next paragraph, it stays joined to that paragraph.
- Scanned (image-only) PDFs have no text layer, so they are reported as "No text found". There is no OCR.
- Encrypted PDFs are not supported.

---

Built with the help of Claude Code.
