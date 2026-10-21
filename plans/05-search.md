# Stage 5 – `search.py`

**Goal:** a command that takes a question and shows the most similar chunks.

**What I'm going to do**
The query is embedded with the same model and the same 768 dimensions as the chunks. Vectors are only comparable if they come from the same "space". Then `search_chunks` finds the closest rows, and each result is printed with:
- its rank and similarity score
- the filename and strategy
- the chunk text, shortened if long

If the table is empty or nothing passes the threshold (question 2), it prints a friendly "No results found" message instead of an empty screen.

**Files:** create `search.py`; small change to `embeddings.py` (question 1)

**Tasks**
- [ ] argparse: `--query` (required), `--top-k` (default 5)
- [ ] Reject an empty or whitespace-only query
- [ ] Embed query → search → print ranked results
- [ ] Empty results message
- [ ] Same friendly error handling as Stage 4

**How to test**
```
python search.py --query "a question your test document answers"
python search.py --query "   "
```
Expected:
- the first prints up to 5 ranked results with scores, and the top result should clearly match the question
- the second prints "Please enter a search query"

**Questions for you**
1. *Should we use Gemini's task types?* `gemini-embedding-001` can embed documents as `RETRIEVAL_DOCUMENT` and questions as `RETRIEVAL_QUERY`, which improves search quality. My recommendation is yes. It is a one-line option in `embeddings.py`, recommended by Google for search. Chunks indexed before the change would need re-indexing.
2. *Should there be a minimum similarity threshold?* Vector search always returns the closest rows, even when none are relevant. My recommendation is a low default threshold (e.g. 0.5) plus a note in the output. That makes "empty search results" a real, testable case, not only "the table is empty".
3. *Should search have filters such as `--strategy` or `--file`?* My recommendation is no. They weren't asked for, and the result lines already show both. That makes it easy to compare strategies by eye.
