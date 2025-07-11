import os
import numpy as np
from pathlib import Path
from typing import List
from pymilvus import  MilvusClient
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from app.feature_extractor import FeatureExtractor
from io import BytesIO
from PIL import Image
import numpy as np

COLLECTION_NAME = "demo_collection"
PERSON_COLLECTION = 'person'
DIMENSION = 768

IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

client = MilvusClient(uri="http://localhost:19530")
model = SentenceTransformer("paraphrase-albert-small-v2")
PERSON_VECTOR_DIM = model.get_sentence_embedding_dimension()

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

    metrics = ["COSINE", "L2", "IP"]
    for metric in metrics:
        collection_name = f"{PERSON_COLLECTION}_{metric.lower()}"
        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)
        client.create_collection(
            collection_name=collection_name,
            dimension=PERSON_VECTOR_DIM,
            auto_id=True,
            enable_dynamic_field=True,
            metric_type=metric
        )



def get_all_vectors_from_collection(collection_name, limit=100):
    client.load_collection(collection_name)
    
    if collection_name == COLLECTION_NAME:
        output_fields = ["id", "vector", "text", "subject", "filename"]
    elif collection_name == "images":
        output_fields = ["id", "vector", "filename"]
    elif collection_name == PERSON_COLLECTION:
        output_fields = ["id", "vector", "name", "description"]
    elif collection_name.startswith(PERSON_COLLECTION + "_"):
        output_fields = ["id", "vector", "name", "description"]
    else:
        output_fields = ["id", "vector"]
    
    try:
        results = client.query(
            collection_name=collection_name,
            filter=None,
            output_fields=output_fields,
            limit=limit
        )
        return results
    except Exception as e:
        print(f"Error obteniendo vectores de {collection_name}: {e}")
        return []

# Obtener todos los vectores y metadatos de la colección principal
def get_all_vectors(limit=100):
    return get_all_vectors_from_collection(COLLECTION_NAME, limit)

# Obtener vectores con información completa para visualizaciones
def get_vectors_for_visualization(collection_name, limit=100):
    """
    Obtiene vectores con información completa para visualizaciones.
    Incluye labels y tooltips para cada punto.
    """
    if collection_name == "all":
        return get_all_vectors_combined(limit)
    
    # Mapear nombres de colección a nombres reales
    if collection_name.lower() == "texts":
        actual_collection = COLLECTION_NAME
    elif collection_name.lower() == "images":
        actual_collection = "images"
    elif collection_name.lower() == "persons":
        actual_collection = f"{PERSON_COLLECTION}_cosine"
    elif collection_name.lower().startswith("persons_"):
        # Manejar colecciones específicas por métrica
        actual_collection = collection_name
    else:
        actual_collection = collection_name
    
    data = get_all_vectors_from_collection(actual_collection, limit)
    
    # Agregar información para visualizaciones según el tipo
    if collection_name.lower() == "texts":  # Textos
        for item in data:
            item["type"] = "text"
            item["label"] = item.get("text", "Texto")[:50] + "..." if len(item.get("text", "")) > 50 else item.get("text", "Texto")
            item["tooltip"] = f"Texto: {item.get('text', 'Sin texto')[:100]}..."
    
    elif collection_name.lower() == "images":  # Imágenes
        for item in data:
            item["type"] = "image"
            item["label"] = item.get("filename", "Imagen")
            item["tooltip"] = f"Imagen: {item.get('filename', 'Sin nombre')}"
    
    elif collection_name.lower() == "persons":  # Personas
        for item in data:
            item["type"] = "person"
            item["label"] = item.get("name", "Persona")
            item["tooltip"] = f"Persona: {item.get('name', 'Sin nombre')} - {item.get('description', 'Sin descripción')[:100]}..."
    
    return data

# Obtener vectores de todas las colecciones
def get_all_vectors_combined(limit=100):
    texts = get_all_vectors_from_collection(COLLECTION_NAME, limit)
    images = get_all_vectors_from_collection("images", limit)
    # Para 'all', usar COSINE como representante de personas
    persons = get_all_vectors_from_collection(f"{PERSON_COLLECTION}_cosine", limit)
    
    # Agregar tipo de dato y información útil para visualizaciones
    for item in texts:
        item["type"] = "text"
        item["label"] = item.get("text", "Texto")[:50] + "..." if len(item.get("text", "")) > 50 else item.get("text", "Texto")
        item["tooltip"] = f"Texto: {item.get('text', 'Sin texto')[:100]}..."
    
    for item in images:
        item["type"] = "image"
        item["label"] = item.get("filename", "Imagen")
        item["tooltip"] = f"Imagen: {item.get('filename', 'Sin nombre')}"
    
    for item in persons:
        item["type"] = "person"
        item["label"] = item.get("name", "Persona")
        item["tooltip"] = f"Persona: {item.get('name', 'Sin nombre')} - {item.get('description', 'Sin descripción')[:100]}..."
    
    return texts + images + persons






# Función nueva para eliminar por IDs

#def delete_vectors_by_ids(ids: List[str], batch_size: int = 50):
#    client.load_collection(COLLECTION_NAME)
#    deleted_ids = []
#
#    for i in range(0, len(ids), batch_size):
#        batch = ids[i:i + batch_size]
#        expr = f'id in [{",".join(batch)}]'
#        try:
#            client.delete(collection_name=COLLECTION_NAME, filter=expr)
#            deleted_ids.extend(batch)
#        except Exception as e:
#            print(f"Error deleting batch {batch}: {e}")
#            continue
#
#    return deleted_ids
