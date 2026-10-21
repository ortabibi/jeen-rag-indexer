"""Search the indexed chunks for the ones most similar to a question."""

import argparse
import sys

from chunking import STRATEGIES
from config import ConfigError
from db import DatabaseError, connect, search_chunks, setup_database
from embeddings import QUERY_TASK, EmbeddingError, embed_texts

DEFAULT_TOP_K = 5
# Measured on the samples: relevant matches scored 0.61-0.73 and an
# unrelated query ("chocolate cake recipe") at most 0.53.
DEFAULT_MIN_SCORE = 0.6
# Long chunks are shortened so each result fits on a few lines.
PREVIEW_LENGTH = 300


def parse_args() -> argparse.Namespace:
    """Read --query, --top-k, --min-score and --strategy from the command line."""
    parser = argparse.ArgumentParser(
        description="Find the indexed chunks most similar to a question."
    )
    parser.add_argument("--query", required=True, help="the question to search for")
    parser.add_argument(
        "--top-k", type=int, default=DEFAULT_TOP_K,
        help=f"how many results to show (default {DEFAULT_TOP_K})",
    )
    parser.add_argument(
        "--min-score", type=float, default=DEFAULT_MIN_SCORE,
        help=f"hide results with a lower similarity (default {DEFAULT_MIN_SCORE})",
    )
    parser.add_argument(
        "--strategy", choices=STRATEGIES,
        help="only search chunks made with this strategy (default: all)",
    )
    args = parser.parse_args()

    if not args.query.strip():
        parser.exit(1, "Please enter a search query.\n")
    if args.top_k < 1:
        parser.exit(1, "--top-k must be at least 1.\n")
    return args


def shorten(text: str) -> str:
    """Put the text on one line and cut it to PREVIEW_LENGTH characters."""
    text = " ".join(text.split())
    if len(text) <= PREVIEW_LENGTH:
        return text
    return text[:PREVIEW_LENGTH].rstrip() + "..."


def search(query: str, top_k: int, min_score: float, strategy: str | None) -> list[dict]:
    """Embed the question and return the matching chunks from the database."""
    # Embed before opening the database, so a Gemini failure never touches it.
    query_embedding = embed_texts([query.strip()], task_type=QUERY_TASK)[0]

    conn = connect()
    try:
        setup_database(conn)
        return search_chunks(conn, query_embedding, top_k, min_score, strategy)
    finally:
        conn.close()


def print_results(results: list[dict], min_score: float) -> None:
    """Print each result with its rank, score, source and text."""
    if not results:
        print(
            f"No results found with similarity of at least {min_score}. "
            f"Try rephrasing the question or lowering --min-score."
        )
        return

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. score {result['similarity']:.3f} | "
            f"{result['filename']} | {result['strategy']}"
        )
        print(f"   {shorten(result['chunk_text'])}")
        print()


def main() -> None:
    """Parse the arguments, run the search and turn our errors into friendly messages."""
    args = parse_args()
    try:
        results = search(args.query, args.top_k, args.min_score, args.strategy)
    except (ConfigError, EmbeddingError, DatabaseError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    print_results(results, args.min_score)


if __name__ == "__main__":
    main()
