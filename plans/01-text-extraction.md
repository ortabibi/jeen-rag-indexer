# Stage 1 – Text extraction

**Goal:** turn a PDF or DOCX file into one clean string of text.

**What I'm going to do**
A PDF stores text as positioned pieces on a page, not as sentences, so the extracted text often has broken lines, extra spaces and page headers. `pypdf` reads the text page by page. `python-docx` reads a Word file paragraph by paragraph, plus any tables. Then a small cleaning step:
- fixes odd whitespace
- joins lines that a PDF broke in the middle of a sentence
- keeps blank lines between paragraphs, because the paragraph strategy in Stage 2 needs them

This module also checks the inputs before anything else runs. It raises an error if:
- the file doesn't exist
- the file isn't `.pdf` or `.docx`
- the PDF is password-protected
- no text comes out, for example a scanned PDF that is really just images

Catching these early means we never spend money on embeddings for a bad file.

**Sample documents**
Both are about the same made-up product, so a search like "login issue" returns real results later:
- `samples/support-faq.docx`: customer-support FAQ with sections on login issues, password reset, billing and account settings, plus one table (for example a billing plans table)
- `samples/user-guide.pdf`: user guide of several pages covering the same topics, with a page header/number on each page so the cleaning step has something real to remove

The DOCX is made with `python-docx`, which is already installed. Making a PDF needs a PDF *writer*, which we don't have (`pypdf` only reads). I'll install `fpdf2` temporarily, use it from a one-off script in my scratchpad (not in the project), then uninstall it. Only the two sample files go into the project, and `requirements.txt` stays unchanged.

**Files:** create `extraction.py`, `samples/support-faq.docx`, `samples/user-guide.pdf`

**Tasks**
- [x] Create `samples/support-faq.docx` (FAQ with one table)
- [x] Create `samples/user-guide.pdf` (multi-page user guide)
- [x] `ExtractionError` exception class
- [x] `extract_text(path)` picks PDF or DOCX by file extension
- [x] PDF reader (pypdf), page by page, in layout mode so blank lines between paragraphs are kept; removes repeated headers/footers and rejoins broken lines
- [x] DOCX reader (python-docx), paragraphs and tables in document order (each row on one line, cells separated by ` | `)
- [x] `clean_text(text)` handles whitespace and paragraph breaks (rejoining broken lines is PDF-only, so DOCX table rows stay on separate lines)
- [x] Errors: missing file, unsupported type, encrypted PDF, damaged file, no text

**How to test**
```
python -c "from extraction import extract_text; t = extract_text('samples/user-guide.pdf'); print(len(t)); print(t[:500])"
python -c "from extraction import extract_text; t = extract_text('samples/support-faq.docx'); print(len(t)); print(t)"
python -c "from extraction import extract_text; extract_text('nope.pdf')"
python -c "from extraction import extract_text; extract_text('requirements.txt')"
```
Expected:
- the first two print the character count and readable text with paragraphs separated by blank lines. The DOCX output includes the table rows as `cell | cell | cell`
- the last two raise `ExtractionError` with a clear message: "File not found: nope.pdf" and "Unsupported file type: .txt (use .pdf or .docx)"

**Decisions** (answered)
1. Test documents: generated samples in `samples/` (FAQ DOCX with a table, multi-page user guide PDF).
2. DOCX tables: extracted, one row per line, cells joined with ` | `.
3. Password-protected PDFs: rejected with `ExtractionError` ("PDF is encrypted"), no decryption attempted.
