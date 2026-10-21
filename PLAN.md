# Part 2 – Plan

| # | Stage | Status |
|---|---|---|
| 0 | [Setup and connections](plans/00-setup.md) | Done |
| 1 | [Text extraction](plans/01-text-extraction.md) | Done |
| 2 | [Chunking strategies](plans/02-chunking.md) | Not started |
| 3 | [Saving and searching in the database](plans/03-database.md) | Not started |
| 4 | [`index_documents.py`](plans/04-index-documents.md) | Not started |
| 5 | [`search.py`](plans/05-search.md) | Not started |
| 6 | [Error handling check](plans/06-error-handling.md) | Not started |
| 7 | [README, sample runs, GitHub](plans/07-readme-github.md) | Not started |

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
