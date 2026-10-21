"""Create text embeddings with the Gemini API."""

from google import genai
from google.genai import errors, types

from config import load_config

MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
# The Gemini API accepts at most 100 texts per embedding request.
BATCH_SIZE = 100
# Gemini embeds stored passages and search questions slightly differently,
# which helps a short question match the passage that answers it.
DOCUMENT_TASK = "RETRIEVAL_DOCUMENT"
QUERY_TASK = "RETRIEVAL_QUERY"


class EmbeddingError(Exception):
    """Raised when the embeddings could not be created."""


def embed_texts(texts: list[str], task_type: str = DOCUMENT_TASK) -> list[list[float]]:
    """Return one embedding (a list of 768 floats) for each text."""
    if not texts:
        return []

    client = genai.Client(api_key=load_config().gemini_api_key)
    embeddings = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        try:
            response = client.models.embed_content(
                model=MODEL_NAME,
                contents=batch,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSIONS,
                    task_type=task_type,
                ),
            )
        except errors.APIError as error:
            raise EmbeddingError(
                f"Gemini API error ({error.code}): {error.message}. "
                f"Check that GEMINI_API_KEY is valid."
            ) from error
        except Exception as error:
            raise EmbeddingError(
                "Could not reach the Gemini API. Check your internet connection."
            ) from error

        embeddings.extend(embedding.values for embedding in response.embeddings)

    return embeddings
