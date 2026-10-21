# Stage 3 – Saving and searching in the database

**Goal:** add functions to insert chunks with their embeddings and to find the most similar chunks.

**What I'm going to do**
- **Saving:** one insert that writes all of a document's chunks together, in a single *transaction*. A transaction means either all chunks are saved or none are, so a failure halfway never leaves half a document in the table.
- **Searching:** pgvector adds a distance operator. `<=>` is *cosine distance*, which compares the angle between two vectors: 0 means the same meaning, larger means less related. We sort by that distance and take the closest rows. Similarity is shown as `1 − distance`, so higher is better.

**Files:** change `db.py`

**Tasks**
- [x] `insert_chunks(conn, chunks, embeddings, filename, strategy)` in one transaction
- [x] `search_chunks(conn, query_embedding, top_k)` returns text, filename, strategy and similarity
- [x] Optional index for fast search (see question 3) – decided: no index for now, mention in README

**How to test**
Tested end to end in Stages 4 and 5. A quick check right after this stage:
```
python check_setup.py
```
Expected: `Setup OK` is still printed, so nothing broke.

**Questions for you**
1. *What happens if the same file is indexed twice with the same strategy?* My recommendation is to delete that file+strategy's old rows first, then insert. Otherwise duplicates fill your search results with copies. yes – delete old rows for the same filename + strategy, then insert. Do the delete and insert in one transaction, so if something fails the old rows are kept.
2: yes, just the filename
2. *Should the stored filename be just the name or the full path?* My recommendation is just the name, e.g. `report.pdf`. Full paths are machine-specific and can expose your folder structure. yes
3. *Should we add an HNSW vector index?* My recommendation is no. With a few hundred rows, an exact scan takes milliseconds, and an approximate index adds complexity for no gain. I'll mention it in the README as the next step at scale. no HNSW index for now, as you recommended – mention it in the README as the next step at scale.
