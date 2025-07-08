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
        dimension=512,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE",
    )

    # Crear colecciones separadas para cada métrica de personas
    metrics = ["COSINE", "L2", "IP"]
    for metric in metrics:
        collection_name = f"{PERSON_COLLECTION}_{metric.lower()}"
        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)
        client.create_collection(
            collection_name=collection_name,
            dimension=DIMENSION,
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
        
        # Apply appropriate normalization for each metric
        if metric_type == "COSINE":
            # COSINE needs L2 normalization
            query_vector = normalize(encoded_query, norm='l2')
        else:
            # L2 and IP use raw vectors (no normalization)
            query_vector = encoded_query
        
        res = client.search(
            collection_name=collection_name,
            data=query_vector,
            limit=top_k,
            output_fields=["name", "description"]
            # No necesitamos search_params porque la colección ya tiene la métrica correcta
        )
        
        results = []
        for hit in res[0]:
            if metric_type == "COSINE":
                # Para COSINE, devolver solo la distancia (se multiplicará por 100 en frontend)
                similarity = hit["distance"]
            elif metric_type == "L2":
                similarity = max(0, 1 - (hit["distance"] / 1000))
            elif metric_type == "IP":
                similarity = max(0, min(1, hit["distance"] / 100))
            
            # Debug opcional
            print(f"Nombre: {hit['entity']['name']}, Distancia: {hit['distance']}, Similitud: {similarity}")

            results.append({
                "id": hit["id"],
                "name": hit["entity"]["name"],
                "description": hit["entity"]["description"],
                "similarity": round(similarity, 4)
            })
        
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
    
    # Definir campos según el tipo de colección
    if collection_name == COLLECTION_NAME:  # Colección de textos
        output_fields = ["id", "vector", "text", "subject", "filename"]
    elif collection_name == "images":  # Colección de imágenes
        output_fields = ["id", "vector", "filename"]
    elif collection_name == PERSON_COLLECTION:  # Colección de personas (usar COSINE por defecto)
        output_fields = ["id", "vector", "name", "description"]
    elif collection_name.startswith(PERSON_COLLECTION + "_"):  # Colecciones de personas por métrica
        output_fields = ["id", "vector", "name", "description"]
    else:
        # Fallback: intentar obtener todos los campos disponibles
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
