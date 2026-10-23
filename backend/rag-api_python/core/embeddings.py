"""
core/embeddings.py
------------------
Generates vector embeddings for text chunks.

Three backends are supported (switch via config.py):
  1. OpenAI text-embedding-3-small (USE_OPENAI_EMBEDDINGS=true)
  2. Gemini embedding-2 (USE_GEMINI_EMBEDDINGS=true)
  3. Multilingual SentenceTransformers model (default, local after download)

WHY THREE BACKENDS?
-------------------
SentenceTransformers runs offline but needs substantial memory to load.
OpenAI and Gemini embeddings call their respective hosted APIs.
The abstraction is a single function: embed_texts(texts) -> np.ndarray
so the rest of the codebase never cares which backend is active.
"""

from typing import List
import numpy as np
from config import (
    USE_OPENAI_EMBEDDINGS,
    USE_GEMINI_EMBEDDINGS,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    GEMINI_EMBEDDING_DIMENSIONS,
    SENTENCE_TRANSFORMER_MODEL,
)
from logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Lazy-load the embedding backend (avoids startup cost if not yet needed)
# ---------------------------------------------------------------------------
_st_model = None  # SentenceTransformer model instance (cached after first load)


def _get_sentence_transformer():
    """Load and cache the SentenceTransformer model."""
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading SentenceTransformer model: {SENTENCE_TRANSFORMER_MODEL}")
        _st_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        logger.info("SentenceTransformer model loaded successfully")
    return _st_model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text strings.

    This is the ONLY function the rest of the codebase calls.
    Dispatches to the correct backend transparently.

    Args:
        texts: List of text strings to embed.

    Returns:
        2-D NumPy array of shape (len(texts), embedding_dim).
        Each row is the embedding vector for the corresponding text.

    Raises:
        RuntimeError: If the selected embedding backend fails or is misconfigured.
    """
    if not texts:
        logger.warning("embed_texts called with empty list — returning empty array")
        return np.array([])

    if USE_OPENAI_EMBEDDINGS and USE_GEMINI_EMBEDDINGS:
        raise RuntimeError("Choose only one remote embedding provider: OpenAI or Gemini.")
    if USE_OPENAI_EMBEDDINGS:
        return _embed_with_openai(texts)
    if USE_GEMINI_EMBEDDINGS:
        return _embed_with_gemini(texts, is_query=False)
    return _embed_with_sentence_transformers(texts)


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string for similarity search.

    Returns:
        1-D NumPy array (embedding vector).
    """
    if USE_GEMINI_EMBEDDINGS:
        if USE_OPENAI_EMBEDDINGS:
            raise RuntimeError("Choose only one remote embedding provider: OpenAI or Gemini.")
        return _embed_with_gemini([query], is_query=True)[0]
    result = embed_texts([query])
    return result[0]


# ---------------------------------------------------------------------------
# Backend implementations (private — do not call directly)
# ---------------------------------------------------------------------------

def _embed_with_sentence_transformers(texts: List[str]) -> np.ndarray:
    """
    Use SentenceTransformers to embed a list of texts.
    Runs entirely locally — no API keys required.
    """
    logger.info(f"Generating embeddings for {len(texts)} chunks via SentenceTransformers")
    model = _get_sentence_transformer()

    # encode() returns a numpy array directly
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    logger.info(f"Embeddings generated — shape: {embeddings.shape}")
    return embeddings


def _embed_with_openai(texts: List[str]) -> np.ndarray:
    """
    Use OpenAI's embedding API to embed a list of texts.
    Requires OPENAI_API_KEY in the environment.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Add the key or choose Gemini/local embeddings."
        )

    import openai
    openai.api_key = OPENAI_API_KEY

    logger.info(f"Generating embeddings for {len(texts)} chunks via OpenAI ({OPENAI_EMBEDDING_MODEL})")

    response = openai.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )

    # Extract embedding vectors in the correct order
    embeddings = np.array([item.embedding for item in response.data])
    logger.info(f"Embeddings generated — shape: {embeddings.shape}")
    return embeddings


def _embed_with_gemini(texts: List[str], *, is_query: bool) -> np.ndarray:
    """Use Gemini's hosted embedding API without loading a local ML model."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the RAG service environment "
            "or choose another embedding provider."
        )

    import httpx

    if is_query:
        contents = [f"task: question answering | query: {text}" for text in texts]
    else:
        contents = [f"title: none | text: {text}" for text in texts]

    requests = [
        {
            "model": f"models/{GEMINI_EMBEDDING_MODEL}",
            "content": {"parts": [{"text": content}]},
            "output_dimensionality": GEMINI_EMBEDDING_DIMENSIONS,
        }
        for content in contents
    ]

    logger.info(
        f"Generating embeddings for {len(texts)} texts via Gemini "
        f"({GEMINI_EMBEDDING_MODEL}, {GEMINI_EMBEDDING_DIMENSIONS} dimensions)"
    )
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_EMBEDDING_MODEL}:batchEmbedContents"
    )
    vectors = []
    try:
        # Keep requests comfortably sized so large documents do not exceed
        # the embedding endpoint's per-request limits.
        for start in range(0, len(requests), 32):
            response = httpx.post(
                endpoint,
                headers={"x-goog-api-key": GEMINI_API_KEY},
                json={"requests": requests[start : start + 32]},
                timeout=60.0,
            )
            response.raise_for_status()
            payload = response.json()
            vectors.extend(item["values"] for item in payload["embeddings"])
        embeddings = np.asarray(vectors, dtype=np.float32)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise RuntimeError(
            f"Gemini embeddings request failed ({exc.response.status_code}): {detail}"
        ) from exc
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Gemini embeddings request failed: {exc}") from exc

    expected_shape = (len(texts), GEMINI_EMBEDDING_DIMENSIONS)
    if embeddings.shape != expected_shape:
        raise RuntimeError(
            "Gemini returned an unexpected embedding shape: "
            f"{embeddings.shape}; expected {expected_shape}."
        )
    logger.info(f"Gemini embeddings generated — shape: {embeddings.shape}")
    return embeddings
