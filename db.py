"""Connect to PostgreSQL and set up the pgvector table."""

import psycopg
from pgvector import Vector
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


def insert_chunks(
    conn: psycopg.Connection,
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
    strategy: str,
) -> None:
    """Replace this file+strategy's rows with the new chunks, in one transaction."""
    rows = [
        (chunk, Vector(embedding), filename, strategy)
        for chunk, embedding in zip(chunks, embeddings)
    ]
    try:
        # Delete and insert are committed together, so if anything fails
        # the old rows are kept and no half-indexed document is left behind.
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM document_chunks WHERE filename = %s AND split_strategy = %s",
                (filename, strategy),
            )
            cur.executemany(
                "INSERT INTO document_chunks (chunk_text, embedding, filename, split_strategy) "
                "VALUES (%s, %s, %s, %s)",
                rows,
            )
        conn.commit()
    except psycopg.Error as error:
        conn.rollback()
        raise DatabaseError(
            f"Could not save the chunks: {error.diag.message_primary}"
        ) from error


def search_chunks(
    conn: psycopg.Connection,
    query_embedding: list[float],
    top_k: int,
    min_score: float = 0.0,
    strategy: str | None = None,
) -> list[dict]:
    """Return up to top_k chunks scoring at least min_score, most similar first."""
    query_vector = Vector(query_embedding)
    # <=> is cosine distance (0 = same meaning), so similarity = 1 - distance.
    conditions = ["1 - (embedding <=> %s) >= %s"]
    params = [query_vector, query_vector, min_score]
    if strategy is not None:
        conditions.append("split_strategy = %s")
        params.append(strategy)
    params.extend([query_vector, top_k])

    try:
        rows = conn.execute(
            "SELECT chunk_text, filename, split_strategy, 1 - (embedding <=> %s) "
            f"FROM document_chunks WHERE {' AND '.join(conditions)} "
            "ORDER BY embedding <=> %s LIMIT %s",
            params,
        ).fetchall()
    except psycopg.Error as error:
        conn.rollback()
        raise DatabaseError(
            f"Could not search the chunks: {error.diag.message_primary}"
        ) from error

    return [
        {"chunk_text": text, "filename": name, "strategy": strategy, "similarity": similarity}
        for text, name, strategy, similarity in rows
    ]
