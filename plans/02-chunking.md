# Stage 2 – Chunking strategies

**Goal:** split the clean text into chunks with one of three strategies.

**What I'm going to do**
An embedding stands for the meaning of one piece of text, and a whole document is too big and too mixed to be one piece. So we cut the text into chunks, and each chunk gets its own embedding. The three strategies differ in *where* they cut:
- **fixed**: every N characters, with each chunk overlapping the previous one by M characters. The overlap means a sentence that falls on a cut still appears whole in one of the two chunks. It is simple and predictable, but it can cut mid-word or mid-idea.
- **sentence**: split into sentences, then group a few sentences per chunk. It never cuts a sentence in half.
- **paragraph**: split on blank lines, so each paragraph is a chunk. Very short paragraphs are merged with the next one. Very long ones are split by sentences so no chunk gets too big.

All three are plain functions with no API or database calls, so they are easy to test.

**Files:** create `chunking.py`

**Tasks**
- [ ] `chunk_fixed(text, size, overlap)`
- [ ] `split_sentences(text)` using a regex on `.`, `!`, `?` followed by whitespace
- [ ] `chunk_sentences(text, ...)`
- [ ] `chunk_paragraphs(text, ...)`, merging tiny paragraphs and splitting huge ones
- [ ] `chunk_text(text, strategy)` dispatcher plus the list of valid strategy names
- [ ] Drop empty or whitespace-only chunks

**How to test**
```
python -c "from extraction import extract_text; from chunking import chunk_text; t = extract_text('samples/example.pdf'); [print(s, len(chunk_text(t, s))) for s in ('fixed','sentence','paragraph')]"
python -c "from chunking import chunk_text; [print(repr(c)) for c in chunk_text('One. Two! Three? Four.', 'sentence')]"
```
Expected: a chunk count for each strategy, with no empty chunks. Fixed chunks are all about the same length, and consecutive fixed chunks share their overlapping text.

**Questions for you**
1. *Should sizes be measured in characters or words?* My recommendation is characters, with fixed size 1000 and overlap 200. Characters are exact and easy to explain. 1000 characters is about 150–200 words, a good size for one idea.
2. *How should sentences be grouped?* My recommendation is to add sentences until about 1000 characters, never splitting one. A fixed count like "5 sentences" gives very uneven chunk sizes.
3. *Should sentence splitting use a library (nltk/spaCy) or a regex?* My recommendation is a regex. It is good enough here and adds no packages. Its weak spot is abbreviations like "e.g." or "Dr.", and I'll mention that in the README.
