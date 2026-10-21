"""Check that the database and the Gemini API are both working."""

import sys

from config import ConfigError
from db import DatabaseError, connect, setup_database
from embeddings import EmbeddingError, embed_texts


def main() -> None:
    """Run the setup checks and print the result."""
    try:
        with connect() as conn:
            setup_database(conn)
        print("Database: connected, table document_chunks is ready")

        embedding = embed_texts(["hello world"])[0]
        print(f"Embedding dimensions: {len(embedding)}")
    except (ConfigError, DatabaseError, EmbeddingError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    print("Setup OK")


if __name__ == "__main__":
    main()
