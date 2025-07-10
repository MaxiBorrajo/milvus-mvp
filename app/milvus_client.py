import os
import numpy as np
from pathlib import Path
from typing import List
from pymilvus import  MilvusClient
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from feature_extractor import FeatureExtractor
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

def search_documents(query: str, top_k: int):
    client.load_collection(COLLECTION_NAME)
    query_vector = model.encode([query])
    # Milvus espera una lista de listas para el parámetro 'data'
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
    Inserts a list of persons into all Milvus collections with their vector embeddings.
    
    Args:
        persons_list: List of Person objects (with .description, .name, .skills attributes)
        metadata: Optional dictionary of additional metadata (e.g., source_file)
    
    Returns:
        int: Number of persons inserted
    """
    try:
        # Encode person descriptions using model
        vectors = model.encode([person.description for person in persons_list])
        
        # Insert into all metric collections with appropriate normalization
        metrics = ["COSINE", "L2", "IP"]
        
        for metric in metrics:
            collection_name = f"{PERSON_COLLECTION}_{metric.lower()}"
            
            # Prepare data with appropriate normalization for each metric
            if metric == "COSINE":
                # COSINE needs L2 normalization
                normalized_vectors = normalize(vectors, norm='l2')
                data = [
                    {
                        "vector": normalized_vectors[i],
                        "name": persons_list[i].name,
                        "description": persons_list[i].description,
                        "metadata": metadata if metadata else None
                    }
                    for i in range(len(persons_list))
                ]
            else:
                # L2 and IP use raw vectors (no normalization)
                data = [
                    {
                        "vector": vectors[i],
                        "name": persons_list[i].name,
                        "description": persons_list[i].description,
                        "metadata": metadata if metadata else None
                    }
                    for i in range(len(persons_list))
                ]
            
            client.insert(
                collection_name=collection_name,
                data=data
            )
           
        
        return len(data)
    except Exception as e:
        raise e


def search_person(query: str, top_k: int, metric_type: str = "COSINE"):
    try:
        collection_name = f"{PERSON_COLLECTION}_{metric_type.lower()}"
        
        if not client.has_collection(collection_name):
            return []
        
        client.load_collection(collection_name)
        
        encoded_query = model.encode([query])
        
        if metric_type == "COSINE":
            query_vector = normalize(encoded_query, norm='l2')
        else:
            query_vector = encoded_query
        
        res = client.search(
            collection_name=collection_name,
            data=query_vector,
            limit=top_k,
            output_fields=["name", "description"]
        )
        
        results = []
        for hit in res[0]:
            if metric_type == "COSINE":
                similarity = hit["distance"]
            elif metric_type == "L2":
                similarity = max(0, 1 - (hit["distance"] / 1000))
            elif metric_type == "IP":
                similarity = max(0, min(1, hit["distance"] / 100))

            results.append({
                "id": hit["id"],
                "name": hit["entity"]["name"],
                "description": hit["entity"]["description"],
                "similarity": round(similarity, 4)
            })
        
        return results
        
    except Exception as e:
        raise e

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

    base_url = "http://localhost:8000/images"

    return [
        {
            "filename": hit["entity"]["filename"],
            "score": round(1 - hit["distance"], 4),
            "url": f"{base_url}/{hit['entity']['filename']}",
            "id": hit["id"]
        }
        for hit in results[0]
    ]

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
            filter="",
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


def delete_if_similar(similar_images: list, threshold: float = 0.01):  # Threshold bajo (cerca de 0)
    if similar_images:
        top_result = similar_images[0]
        
        # Si el score es cercano a 0 (idéntico), borramos
        if top_result["score"] <= threshold: 
            client.delete(
                collection_name="images",
                ids=[top_result["id"]]
            )
            return True, top_result["id"]
    
    return False, None

def delete_image_byId(vector_id: int):
    """Elimina una imagen por su ID vectorial"""
    client.delete(
        collection_name="images",
        ids=[vector_id]  # Corregido: usa el parámetro real
    )


    
def subirImagenes(path, funcion):
    for nombre_archivo in os.listdir(path):
        ruta_completa = os.path.join(path, nombre_archivo)
        if os.path.isfile(ruta_completa) and nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', 'jfif' )):
            metadata = {"filename": nombre_archivo}  
            funcion([ruta_completa], metadata)



def vectorsForAFileName(filename: str):
    # Cargar la colección (esto puede variar según la versión de Milvus)
    client.load_collection(COLLECTION_NAME)
    
    # Realizar la consulta con filtro
    res = client.query(
        collection_name=COLLECTION_NAME,
        filter=f"filename == '{filename}'",  # Filtro por nombre de archivo
        output_fields=["text", "filename", "vector","id"]  # Campos a recuperar
    )
    
    return res

# Función nueva para eliminar por IDs

def delete_vectors_by_ids(ids: List[str], batch_size: int = 50):
    client.load_collection(COLLECTION_NAME)
    deleted_ids = []

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        expr = f'id in [{",".join(batch)}]'
        try:
            client.delete(collection_name=COLLECTION_NAME, filter=expr)
            deleted_ids.extend(batch)
        except Exception as e:
            print(f"Error deleting batch {batch}: {e}")
            continue

    return deleted_ids

def delete_documents_by_filename_service(filename: str):

    client.load_collection(COLLECTION_NAME)
    res = client.delete(
        collection_name=COLLECTION_NAME,
        filter=f"filename == '{filename}'"
    )
    
    return {
        "filename": filename,
        "deleted_count": res["delete_count"],
        "method": "direct_filename_filter"
    }

def count_vectors_by_attribute(collection_name: str, field: str, value: str) -> int:
    """
    Cuenta la cantidad de vectores en una colección según un atributo específico.
    Args:
        collection_name (str): Nombre de la colección.
        field (str): Nombre del campo por el que filtrar.
        value (str): Valor del campo a buscar.
    Returns:
        int: Cantidad de vectores que cumplen el filtro.
    """
    client.load_collection(collection_name)
    filter_expr = f'{field} == "{value}"'
    results = client.query(
        collection_name=collection_name,
        filter=filter_expr,
        output_fields=[field]
    )
    return len(results)