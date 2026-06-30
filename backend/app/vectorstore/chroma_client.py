import chromadb

from app.core.config import settings


def get_chroma_client():
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def get_or_create_collection(name: str):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)
