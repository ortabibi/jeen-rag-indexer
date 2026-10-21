"""Connect to PostgreSQL and set up the pgvector table."""

import psycopg
from pgvector.psycopg import register_vector

from config import load_config
from embeddings import EMBEDDING_DIMENSIONS

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT,
    embedding VECTOR({EMBEDDING_DIMENSIONS}),
    filename TEXT,
    split_strategy TEXT,
    created_at TIMESTAMP DEFAULT now()
)
"""


class DatabaseError(Exception):
    """Raised when a database operation fails."""


def connect() -> psycopg.Connection:
    """Open a connection to POSTGRES_URL with pgvector support enabled."""
    try:
        conn = psycopg.connect(load_config().postgres_url)
    except psycopg.Error as error:
        # The original error text can contain parts of the URL, so it is not shown.
        raise DatabaseError(
            "Could not connect to the database. "
            "Check POSTGRES_URL in your .env file and your internet connection."
        ) from error

    try:
        # register_vector needs the "vector" type to exist, so the extension
        # is enabled here, before registering.
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        register_vector(conn)
    except psycopg.Error as error:
        conn.close()
        raise DatabaseError(
            f"Could not enable the pgvector extension: {error.diag.message_primary}"
        ) from error

    return conn


def setup_database(conn: psycopg.Connection) -> None:
    """Create the document_chunks table if it doesn't exist yet."""
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    except psycopg.Error as error:
        conn.rollback()
        raise DatabaseError(
            f"Could not create the document_chunks table: {error.diag.message_primary}"
        ) from error
