from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
import time

COLLECTION_NAME = "demo_collection"
DIM = 768

client = MilvusClient(uri="http://milvus-standalone:19530")  # Cambia si no es Docker

model = SentenceTransformer("paraphrase-albert-small-v2")

if not client.has_collection(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=DIM,
        index_params={
            "field_name": "vector",
            "index_type": "FLAT",
            "metric_type": "COSINE",
            "params": {}
        }
    )

def insert_texts(texts: list[str]):
    vectors = model.encode(texts)
    data = [{"id": i, "vector": vectors[i], "text": texts[i]} for i in range(len(texts))]
    client.insert(collection_name=COLLECTION_NAME, data=data)
    client.load_collection(COLLECTION_NAME)

def search_text(query: str, limit: int = 3):
    client.load_collection(COLLECTION_NAME)
    query_vector = model.encode([query])
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=query_vector,
        anns_field="vector",
        output_fields=["text"],
        limit=limit,
        search_params={"params": {}}
    )
    return [hit["text"] for hit in results[0]]
