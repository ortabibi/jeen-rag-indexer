# Stage 1 – Text extraction

**Goal:** turn a PDF or DOCX file into one clean string of text.

**What I'm going to do**
A PDF stores text as positioned pieces on a page, not as sentences, so the extracted text often has broken lines, extra spaces and page headers. `pypdf` reads the text page by page. `python-docx` reads a Word file paragraph by paragraph. Then a small cleaning step:
- fixes odd whitespace
- joins lines that a PDF broke in the middle of a sentence
- keeps blank lines between paragraphs, because the paragraph strategy in Stage 2 needs them

This module also checks the inputs before anything else runs. It raises an error if:
- the file doesn't exist
- the file isn't `.pdf` or `.docx`
- no text comes out, for example a scanned PDF that is really just images

Catching these early means we never spend money on embeddings for a bad file.

**Files:** create `extraction.py`

**Tasks**
- [ ] `ExtractionError` exception class
- [ ] `extract_text(path)` picks PDF or DOCX by file extension
- [ ] PDF reader (pypdf), page by page
- [ ] DOCX reader (python-docx), paragraph by paragraph
- [ ] `clean_text(text)` handles whitespace, broken lines and paragraph breaks
- [ ] Errors: missing file, unsupported type, no text

**How to test**
```
python -c "from extraction import extract_text; t = extract_text('samples/example.pdf'); print(len(t)); print(t[:500])"
python -c "from extraction import extract_text; extract_text('nope.pdf')"
python -c "from extraction import extract_text; extract_text('requirements.txt')"
```
Expected:
- the first command prints the character count and readable text with paragraphs separated by blank lines
- the second and third raise `ExtractionError` with a clear message: "File not found: nope.pdf" and "Unsupported file type: .txt (use .pdf or .docx)"

**Questions for you**
1. *Test documents: do you have your own PDF/DOCX files, or should I make small samples in a `samples/` folder?* My recommendation is to use one real PDF and one real DOCX of yours. Real files show real problems like headers and broken lines, which made-up samples hide.
2. *Should DOCX tables be extracted too?* My recommendation is yes, each row as one line with cells separated by ` | `. Otherwise any text inside tables is silently lost.
3. *What about password-protected PDFs?* My recommendation is to treat them as an `ExtractionError` ("PDF is encrypted") and not try to decrypt them. That is rare and outside the assignment.
