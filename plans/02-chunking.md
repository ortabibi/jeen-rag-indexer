# Stage 2 – Chunking strategies

**Goal:** split the clean text into chunks with one of three strategies.

**What I'm going to do**
An embedding stands for the meaning of one piece of text, and a whole document is too big and too mixed to be one piece. So we cut the text into chunks, and each chunk gets its own embedding. The three strategies differ in *where* they cut:
- **fixed**: every 500 characters, with each chunk overlapping the previous one by 100 characters. The overlap keeps context across the cut: a short sentence (under 100 characters) that falls on a cut appears whole in one of the two chunks, and longer ones are at least partly repeated, so the meaning isn't lost completely. It is simple and predictable, but it can cut mid-word or mid-idea.
- **sentence**: split into sentences, then group a few sentences per chunk. It never cuts a sentence in half.
- **paragraph**: split on blank lines, so each paragraph is a chunk. Very short paragraphs are merged with the next one. Very long ones are split by sentences so no chunk gets too big.

All three are plain functions with no API or database calls, so they are easy to test.

**Files:** create `chunking.py`

**Tasks**
- [x] `chunk_fixed(text, size, overlap)`
- [x] `split_sentences(text)` using a regex on `.`, `!`, `?` followed by whitespace
- [x] `chunk_sentences(text, ...)`
- [x] `chunk_paragraphs(text, ...)`, merging tiny paragraphs and splitting huge ones
- [x] `chunk_text(text, strategy)` dispatcher plus the list of valid strategy names
- [x] Drop empty or whitespace-only chunks

**How to test**
```
python -c "from extraction import extract_text; from chunking import chunk_text; t = extract_text('samples/user-guide.pdf'); [print(s, len(chunk_text(t, s))) for s in ('fixed','sentence','paragraph')]"
python -c "from chunking import chunk_text; [print(repr(c)) for c in chunk_text('One. Two! Three? Four.', 'sentence')]"
```
Expected:
- the first prints a chunk count for each strategy (fixed 10, sentence 9, paragraph 19), with no empty chunks. Fixed chunks are all about the same length, and consecutive fixed chunks share their 100 overlapping characters
- the second prints one chunk, `'One. Two! Three? Four.'`, because all four sentences fit within 500 characters

**Decisions** (answered)
1. Sizes are in characters: `CHUNK_SIZE = 500`, `CHUNK_OVERLAP = 100`, constants at the top of `chunking.py` so they are easy to change. The sample documents are only ~4,000 characters, so smaller chunks give more precise search results.
2. Sentence grouping: whole sentences are added until the chunk would pass ~500 characters. A sentence is never split, so one longer than 500 becomes its own chunk.
3. Sentence splitting uses a regex, with no extra packages. Known weak spot: abbreviations like "e.g." or "Dr." are treated as sentence ends.
4. Paragraphs shorter than `MIN_PARAGRAPH_SIZE = 100` (e.g. headings) are merged into the next paragraph. Paragraphs longer than 500 are split by sentences. A short paragraph at the very end joins the last chunk.
