"""Index a PDF or DOCX file: extract text, chunk it, embed the chunks and save them."""

import argparse
import sys
from pathlib import Path

from chunking import STRATEGIES, chunk_text
from config import ConfigError
from db import DatabaseError, connect, insert_chunks, setup_database
from embeddings import EmbeddingError, embed_texts
from extraction import ExtractionError, extract_text


def parse_args() -> argparse.Namespace:
    """Read --file and --strategy from the command line."""
    parser = argparse.ArgumentParser(
        description="Index a PDF or DOCX file into the vector database."
    )
    parser.add_argument("--file", required=True, help="path to a .pdf or .docx file")
    parser.add_argument(
        "--strategy", required=True, choices=STRATEGIES, help="how to split the text"
    )
    return parser.parse_args()


def index_document(path: Path, strategy: str) -> None:
    """Run the pipeline extract → chunk → embed → save, printing progress."""
    text = extract_text(path)
    print(f"Extracted {len(text):,} characters")

    chunks = chunk_text(text, strategy)
    print(f"Created {len(chunks)} chunks ({strategy})")

    # Embed before opening the database, so a Gemini failure never touches it.
    embeddings = embed_texts(chunks)
    print(f"Created {len(embeddings)} embeddings")

    conn = connect()
    try:
        setup_database(conn)
        insert_chunks(conn, chunks, embeddings, path.name, strategy)
    finally:
        conn.close()
    print(f"Saved {len(chunks)} chunks for {path.name}")


def main() -> None:
    """Parse the arguments, index the file and turn our errors into friendly messages."""
    args = parse_args()
    try:
        index_document(Path(args.file), args.strategy)
    except (ExtractionError, ConfigError, EmbeddingError, DatabaseError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
