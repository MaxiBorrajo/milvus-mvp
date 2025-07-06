from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from app.feature_extractor import FeatureExtractor
import os
from io import BytesIO
from PIL import Image

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