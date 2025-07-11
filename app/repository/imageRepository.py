import os

from app.feature_extractor import FeatureExtractor


from milvus_client import client


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
            "id": hit.id
        }
        for hit in results[0]
    ]



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
 

