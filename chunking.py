"""Split clean text into chunks using one of three strategies."""

import re

STRATEGIES = ("fixed", "sentence", "paragraph")

# All sizes are in characters. Change them here to try other chunk sizes.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
# Paragraphs shorter than this are merged with the next one.
MIN_PARAGRAPH_SIZE = 100

# A sentence ends with ".", "!" or "?" followed by whitespace.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, strategy: str) -> list[str]:
    """Split text with the named strategy and return the non-empty chunks."""
    if strategy == "fixed":
        chunks = chunk_fixed(text)
    elif strategy == "sentence":
        chunks = chunk_sentences(text)
    elif strategy == "paragraph":
        chunks = chunk_paragraphs(text)
    else:
        raise ValueError(
            f"Unknown strategy: {strategy} (use {', '.join(STRATEGIES)})"
        )
    return [chunk for chunk in chunks if chunk.strip()]


def chunk_fixed(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Cut text every `size` characters, each chunk repeating the last `overlap` characters of the previous one."""
    if not 0 <= overlap < size:
        raise ValueError("Overlap must be at least 0 and smaller than the chunk size.")

    step = size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start:start + size].strip())
        if start + size >= len(text):
            break
    return chunks


def split_sentences(text: str) -> list[str]:
    """Split text into sentences at ".", "!" or "?" followed by whitespace."""
    return [sentence.strip() for sentence in SENTENCE_END.split(text) if sentence.strip()]


def chunk_sentences(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Group whole sentences into chunks of up to about `size` characters, never splitting a sentence."""
    chunks = []
    current = ""
    for sentence in split_sentences(text):
        if current and len(current) + 1 + len(sentence) > size:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    if current:
        chunks.append(current)
    return chunks


def chunk_paragraphs(text: str, size: int = CHUNK_SIZE, min_size: int = MIN_PARAGRAPH_SIZE) -> list[str]:
    """Make one chunk per paragraph, merging tiny paragraphs and splitting huge ones by sentences."""
    chunks = []
    pending = ""
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        pending = f"{pending}\n\n{paragraph}" if pending else paragraph
        if len(pending) < min_size:
            # Too short on its own (e.g. a heading), so keep it for the next paragraph.
            continue

        if len(pending) > size:
            chunks.extend(chunk_sentences(pending, size))
        else:
            chunks.append(pending)
        pending = ""

    if pending:
        # A short paragraph at the very end joins the last chunk.
        if chunks:
            chunks[-1] = f"{chunks[-1]}\n\n{pending}"
        else:
            chunks.append(pending)
    return chunks
