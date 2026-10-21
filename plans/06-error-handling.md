# Stage 6 – Error handling check

**Goal:** trigger each of the 6 required error cases on purpose and confirm the message is clear.

**What I'm going to do**
No new features. I'll give you a command for each case, run it, and fix any message that is unclear or shows a stack trace. For the two cases that need a broken `.env`, you edit `.env` yourself, because I never touch its contents, and then restore it.

**Files:** small fixes only, if needed

**Tasks**
- [x] Missing file: `python index_documents.py --file missing.pdf --strategy fixed`
- [x] Unsupported type: `python index_documents.py --file requirements.txt --strategy fixed`
- [x] No text: index a scanned or image-only PDF, or an empty DOCX
- [x] Embedding failure: you temporarily put a wrong `GEMINI_API_KEY` in `.env`, then index a file
- [x] Database failure: you temporarily change the password in `POSTGRES_URL`, then run a search
- [x] Empty results: search with an unrelated query, or search on an empty table
- [x] Every case prints one clear line, with no stack trace and no secret values

**How to test:** the commands in the task list. Each should print a single line starting with `Error:` (or the "No results" message) and exit with code 1, except empty results, which is not a failure.

**Questions for you**
1. *How should we get a "no text" test file?* My recommendation is an empty DOCX you save from Word. It is the easiest to make, and a scanned PDF goes through the same "no text" check.

   **Answer:** Create the test files yourself with a small script (python-docx can create an empty DOCX). Put them in samples/edge-cases/: empty.docx (no text) and notes.txt (unsupported type). Keep them in the repo so the README error examples can be reproduced.

2. *Should "no results" exit with code 0 or 1?* My recommendation is 0. The search worked and simply found nothing, which is different from a failure.

   **Answer:** 0, as recommended – but the message should still be clear to the user.
