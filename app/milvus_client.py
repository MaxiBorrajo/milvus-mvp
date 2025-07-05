from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from feature_extractor import FeatureExtractor
import os
import numpy as np

COLLECTION_NAME = "demo_collection"
PERSON_COLLECTION = 'person'
DIMENSION = 768

# Inicializar cliente y modelo
client = MilvusClient(uri="http://localhost:19530")
model = SentenceTransformer("paraphrase-albert-small-v2")
PERSON_VECTOR_DIM = model.get_sentence_embedding_dimension()

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
        dimension=384,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE",
    )

    if client.has_collection(collection_name=PERSON_COLLECTION):
        client.drop_collection(collection_name=PERSON_COLLECTION)
    client.create_collection(
        collection_name=PERSON_COLLECTION,
        dimension=DIMENSION,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type='COSINE'  # Volver a COSINE para vectores crudos
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

def insert_persons(persons_list, metadata=None):
    """
    Inserts a list of persons into the Milvus collection with their vector embeddings.
    
    Args:
        persons_list: List of Person objects (with .description, .name, .skills attributes)
        metadata: Optional dictionary of additional metadata (e.g., source_file)
    
    Returns:
        int: Number of persons inserted
    """
    try:
        # Encode person descriptions using model
        vectors = model.encode([person.description for person in persons_list])
        query_vector = normalize(vectors, norm='l2')
        
        # Prepare data for insertion
        data = [
            {
                "vector": query_vector[i],
                "name": persons_list[i].name,
                "description": persons_list[i].description,
                "metadata": metadata if metadata else None
            }
            for i in range(len(persons_list))
        ]
        
        # Insert into Milvus collection
        client.insert(
            collection_name=PERSON_COLLECTION,
            data=data
        )
        
        return len(data)
    except Exception as e:
        raise e


def search_person(query: str, top_k: int):
    try:
        if not client.has_collection(PERSON_COLLECTION):
            return []
        
        client.load_collection(PERSON_COLLECTION)
        
        encoded_query = model.encode([query])
        vectorNormal = normalize(encoded_query, norm='l2')
        
        res = client.search(
            collection_name=PERSON_COLLECTION,
            data=vectorNormal,
            limit=top_k,
            output_fields=["name", "description"]
        )
        
        results = [
            {
                "id": hit["id"],
                "name": hit["entity"]["name"],
                "description": hit["entity"]["description"],
                "similarity": round(1 - hit["distance"], 4)
            }
            for hit in res[0]
        ]
        
        return results
        
    except Exception as e:
        raise e

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
