from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from feature_extractor import FeatureExtractor
import os

COLLECTION_NAME = "demo_collection"
DIMENSION = 768

# Inicializar cliente y modelo
client = MilvusClient(uri="http://localhost:19530")
model = SentenceTransformer("paraphrase-albert-small-v2")

# Crear colección limpia
def setup_collection():
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=DIMENSION,
        auto_id=True,
        enable_dynamic_field=True
    )
    if client.has_collection(collection_name="images"):
        client.drop_collection(collection_name="images")
    client.create_collection(
        collection_name="images",
        vector_field_name="vector",
        dimension=512,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE",
    )

# Insertar documentos
def insert_documents(items, metadata=None):
    vectors = model.encode([item.text for item in items])
    data = [
        {
           
            "vector": vectors[i],
            "text": items[i].text,
            "subject": items[i].subject,
            "filename": metadata.get("filename") if metadata else None
        }
        for i in range(len(items))
    ]
    client.insert(collection_name=COLLECTION_NAME, data=data)
    return len(data)

# Buscar documentos
def search_documents(query: str, top_k: int):
    client.load_collection(COLLECTION_NAME)
    query_vector = model.encode([query])
    res = client.search(
        collection_name=COLLECTION_NAME,
        data=query_vector,
        limit=top_k,
        output_fields=["text", "subject"]
    )

    return [
        {
            "id": hit["id"],
            "text": hit["entity"]["text"],
            "subject": hit["entity"]["subject"],
            "similarity": round(1 - hit["distance"], 4)
        }
        for hit in res[0]
    ]

# Insertar imagenes
def insert_images(images, metadata=None):
    extractor = FeatureExtractor("resnet34")
    embeddings = []
    for image in images:
        image_embedding = extractor(image)
        embeddings.append(image_embedding)
    data = [
        {
           
            "vector": embeddings[i],
            "filename": metadata.get("filename") if metadata else None
        }
        for i in range(len(embeddings))
    ]
    client.insert(collection_name="images", data=data)
    return len(data)
 
def search_similar_images(image_path, top_k: int):
    extractor = FeatureExtractor("resnet34")
    vectors = [extractor(image_path)]

    results = client.search(
        "images",
        data=vectors,
        output_fields=["filename"],
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )

    print(results)

    # URL base de tu servidor
    base_url = "http://localhost:8000/images"

    return [
        {
            "filename": hit["entity"]["filename"],
            "score": round(1 - hit["distance"], 4),
            "url": f"{base_url}/{hit['entity']['filename']}"
        }
        for hit in results[0]
    ]

# Obtener todos los vectores y metadatos de una colección específica
def get_all_vectors_from_collection(collection_name, limit=100):
    client.load_collection(collection_name)
    results = client.query(
        collection_name=collection_name,
        filter=None,
        output_fields=["id", "vector", "text", "subject", "filename"],
        limit=limit
    )
    return results

# Obtener todos los vectores y metadatos de la colección principal
def get_all_vectors(limit=100):
    return get_all_vectors_from_collection(COLLECTION_NAME, limit)

# Obtener vectores de ambas colecciones
def get_all_vectors_combined(limit=100):
    texts = get_all_vectors_from_collection(COLLECTION_NAME, limit)
    images = get_all_vectors_from_collection("images", limit)
    
    # Agregar tipo de dato a cada elemento
    for item in texts:
        item["type"] = "text"
    for item in images:
        item["type"] = "image"
    
    return texts + images
