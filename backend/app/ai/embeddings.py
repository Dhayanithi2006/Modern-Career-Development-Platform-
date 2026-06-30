from hashlib import sha256


def deterministic_embedding(text: str, dimensions: int = 384) -> list[float]:
    """Development fallback embedding. Replace with Gemini embeddings in production."""
    digest = sha256(text.encode("utf-8")).digest()
    values = []
    for index in range(dimensions):
        values.append(digest[index % len(digest)] / 255)
    return values
