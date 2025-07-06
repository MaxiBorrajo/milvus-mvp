from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from feature_extractor import FeatureExtractor
import os
<<<<<<< HEAD
from io import BytesIO
from PIL import Image
=======
import numpy as np
>>>>>>> 6b521d1723308344fd379351591b0b754b0011ed

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
<<<<<<< HEAD
def upsert_with_selection(search_image_path: str, new_image_path: str, selected_filename: str, top_k: int = 5):
    extractor = FeatureExtractor("resnet34")
    
    try:
        # 1. Buscar imágenes similares
        search_embedding = extractor(search_image_path)
        similar_images = client.search(
            collection_name="images",
            data=[search_embedding],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["id", "filename"],
            consistency_level="Strong"
        )[0]

        print(f"Encontradas {len(similar_images)} imágenes similares")
        
        # 2. Verificar que la imagen seleccionada esté en los resultados
        selected_id = None
        for img in similar_images:
            if img["entity"]["filename"] == selected_filename:
                selected_id = img["id"]
                break
        
        if not selected_id:
            raise ValueError(f"La imagen {selected_filename} no fue encontrada en los resultados")
        
        # 3. Eliminar la imagen seleccionada
        client.delete(
            collection_name="images",
            ids=[selected_id],
            consistency_level="Strong"
        )
        
        # 4. Insertar nueva imagen
        new_embedding = extractor(new_image_path)
        new_id = client.insert(
            collection_name="images",
            data=[{"vector": new_embedding, "filename": new_image_path.split("/")[-1]}]
        )["ids"][0]
        
        return {
            "status": "upserted",
            "new_id": new_id,
            "deleted_id": selected_id,
            "similar_images": [
                {
                    "filename": img["entity"]["filename"],
                    "score": round(1 - img["distance"], 4),
                    "id": img["id"]
                } 
                for img in similar_images
            ]
        }
        
    except Exception as e:
        print(f"Error en upsert con selección: {str(e)}")
        raise
=======

# Obtener todos los vectores y metadatos de una colección específica
def get_all_vectors_from_collection(collection_name, limit=100):
    client.load_collection(collection_name)
    
    # Definir campos según el tipo de colección
    if collection_name == COLLECTION_NAME:  # Colección de textos
        output_fields = ["id", "vector", "text", "subject", "filename"]
    elif collection_name == "images":  # Colección de imágenes
        output_fields = ["id", "vector", "filename"]
    elif collection_name == PERSON_COLLECTION:  # Colección de personas
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
        actual_collection = PERSON_COLLECTION
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
    persons = get_all_vectors_from_collection(PERSON_COLLECTION, limit)
    
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
>>>>>>> 6b521d1723308344fd379351591b0b754b0011ed
