# Part 2 – Plan

| # | Stage | Status |
|---|---|---|
| 0 | [Setup and connections](plans/00-setup.md) | Done |
| 1 | [Text extraction](plans/01-text-extraction.md) | Done |
| 2 | [Chunking strategies](plans/02-chunking.md) | Done |
| 3 | [Saving and searching in the database](plans/03-database.md) | Done |
| 4 | [`index_documents.py`](plans/04-index-documents.md) | Done |
| 5 | [`search.py`](plans/05-search.md) | Done |
| 6 | [Error handling check](plans/06-error-handling.md) | Done |
| 7 | [README, sample runs, GitHub](plans/07-readme-github.md) | In progress |

Workflow: before each stage, I show that stage's questions and wait for your answers. After each stage, I tick its boxes in its file, update the status here, tell you how to test it, and stop. The next stage starts only when you say so.

All commands run from the `part2` folder using `./venv/Scripts/python.exe` (shown in the stage files as `python`).

## Design decisions

A running list of choices made along the way, to be copied into the README in Stage 7.

- **Sample documents (Stage 1):** `samples/` holds a generated customer-support FAQ (DOCX, with a table) and a multi-page user guide (PDF), both on login, password reset, billing and account settings.
- **DOCX tables (Stage 1):** table text is extracted, with one row per line and cells separated by ` | `, so it isn't lost.
- **Encrypted PDFs (Stage 1):** rejected with a clear error. Decrypting them is out of scope.
- **PDF layout mode (Stage 1):** pypdf's normal mode returns no blank lines between paragraphs, so layout mode is used to keep them for the paragraph strategy.
- **Headers and footers (Stage 1):** lines that repeat in the first/last 3 lines of at least half the pages are removed (digits ignored, so "Page 1", "Page 2" match). A document title that matches the running header is removed too.
- **Known limitation (Stage 1):** if a PDF heading sits very close to the next paragraph, it stays joined to that paragraph. Detecting headings by guesswork would break real wrapped lines.
- **Chunk sizes (Stage 2):** measured in characters: 500 per chunk, 100 overlap for the fixed strategy. The sample documents are only ~4,000 characters, so smaller chunks give more precise search results. Sizes are constants at the top of `chunking.py`.
- **Sentence grouping (Stage 2):** whole sentences are added until a chunk would pass ~500 characters. A sentence is never split, so a longer one becomes its own chunk.
- **Sentence splitting (Stage 2):** a regex on `.`, `!`, `?` followed by whitespace, with no extra packages. Known limitation: abbreviations like "e.g." or "Dr." are treated as sentence ends.
- **Paragraph chunks (Stage 2):** paragraphs under 100 characters (e.g. headings) are merged into the next one. Paragraphs over 500 are split by sentences.
- **Embedding size (Stage 3):** `gemini-embedding-001` returns 3,072 numbers by default; we ask for 768 (`output_dimensionality`). It is one of Google's recommended sizes and keeps each row 4× smaller. pgvector's HNSW index supports at most 2,000 dimensions, so 3,072 would block adding an index later. The table's `vector(768)` column must match.
- **Re-indexing (Stage 3):** indexing a file again with the same strategy deletes that filename + strategy's old rows, then inserts the new ones. Delete and insert run in one transaction, so if something fails the old rows are kept.
- **Stored filename (Stage 3):** only the file name (e.g. `user-guide.pdf`), not the full path. Full paths are machine-specific and expose your folder structure.
- **No vector index (Stage 3):** search does an exact scan with cosine distance (`<=>`). With a few hundred rows this takes milliseconds. An HNSW index is the next step at scale.
- **Required `--strategy` (Stage 4):** no default, exactly as the assignment's command shows, so it is always clear which strategy produced the rows.
- **Embed before saving (Stage 4):** the pipeline is extract → chunk → embed → save, so a Gemini failure never touches the database.
- **Progress output (Stage 4):** plain `print`, not `logging`. It is a small CLI.
- **Task types (Stage 5):** chunks are embedded as `RETRIEVAL_DOCUMENT` and queries as `RETRIEVAL_QUERY`, as Google recommends for search.
- **Minimum score (Stage 5):** `--min-score`, default 0.6. Measured on the samples: relevant matches for "login issue" scored 0.61–0.73, and the unrelated "chocolate cake recipe" scored at most 0.53, so 0.6 sits between them. Vector search always returns the closest rows, so without a threshold "no results" could never happen.
- **Search options (Stage 5):** `--top-k` (default 5) and an optional `--strategy` filter. Without the filter, all strategies are searched.

## Requirements coverage

| Requirement | Stage |
|---|---|
| Extract clean text from PDF / DOCX | 1 |
| Chunking: fixed-size with overlap, sentence, paragraph | 2 |
| Store chunks + embeddings in pgvector | 3 |
| `index_documents.py --file --strategy` | 4 |
| `search.py --query` (vector similarity) | 5 |
| Error: missing file | 1 (raised), 4 (shown to user) |
| Error: unsupported file type | 1, 4 |
| Error: document with no text | 1, 4 |
| Error: embedding failure | 0 (raised), 4, 5 |
| Error: database connection failure | 0 (raised), 4, 5 |
| Error: empty search results | 5 |
| Check all 6 error cases end to end | 6 |
| README.md, sample output, GitHub | 7 |
