# Stage 4 – `index_documents.py`

**Goal:** a command that reads a file, chunks it, embeds the chunks and stores them.

**What I'm going to do**
`argparse` reads `--file` and `--strategy`. Because of `choices`, an invalid strategy is rejected with a usage message automatically. Then the pipeline runs in order:

extract → chunk → embed → save

It prints a short progress line after each step. Every error class we have (`ExtractionError`, `ConfigError`, `EmbeddingError`, `DatabaseError`) is caught in one place and printed as a friendly one-line message with exit code 1, never a stack trace. Exit code 1 tells scripts the command failed. We embed *before* opening the database, so a Gemini failure never touches the database.

**Files:** create `index_documents.py`

**Tasks**
- [x] argparse: `--file` (required), `--strategy` (required, choices `fixed|sentence|paragraph`)
- [x] Pipeline: extract → chunk → embed → connect → set up table → insert
- [x] Progress output: characters extracted, number of chunks, rows saved
- [x] One `try/except` that turns our errors into friendly messages and exit code 1

**How to test**
```
python index_documents.py --file samples/example.pdf --strategy paragraph
python index_documents.py --file samples/example.docx --strategy fixed
python index_documents.py --file samples/example.pdf --strategy banana
```
Expected:
- the first two print something like `Extracted 12,345 characters` → `Created 18 chunks (paragraph)` → `Saved 18 chunks for example.pdf`
- the third prints argparse's "invalid choice" message

**Questions for you**
1. *Should `--strategy` be required or default to one?* My recommendation is required, exactly as the assignment's command shows. That way it is always clear which strategy produced the rows.

   **Answer:** required

2. *Should progress lines be plain `print` or the `logging` module?* My recommendation is plain `print`. It is a small CLI, and `logging` adds setup without a real benefit here.

   **Answer:** print
