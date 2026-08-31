from openai import OpenAI

from Service.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL


def get_openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing from .env")
    return OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    client = get_openai_client()
    vectors: list[list[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=batch,
        )
        vectors.extend([item.embedding for item in response.data])

    return vectors


def embed_query(text: str) -> list[float]:
    return embed_texts([text], batch_size=1)[0]


def dot_product(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))

