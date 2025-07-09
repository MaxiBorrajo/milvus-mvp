import os
import time

from pymilvus import milvus_client


IMAGE_COLLECTION_NAME = "image_multimodal"
IMAGE_COLLECTION_DIMENSION = 512
TEXT_COLLECTION_NAME = "text_multimodal"
TEXT_COLLECTION_DIMENSION = 512

client = MilvusClient(uri="http://localhost:19530")
model = SentenceTransformer("paraphrase-albert-small-v2")

def setup_multimodal():
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name= IMAGE_COLLECTION_NAME,
        vector_field_name="vector",
        dimension= IMAGE_COLLECTION_DIMENSION,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE"
    )
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name= TEXT_COLLECTION_NAME,
        vector_field_name="vector",
        dimension= TEXT_COLLECTION_DIMENSION,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE"
    )


def insert_multimodal(items, data_type):
    vectores = encode_image([item.data for item in items]) if data_type == "image" else model.encode([item.text for item in items])
    data = [
        {
            "vector": vectores[i],
            "data": items[i].data,
            "type": data_type,
            "fase_historia": items[i].metadata.fase_historia,
            "path_imagen": items[i].metadata.path_imagen,
            "path_audio": items[i].metadata.path_audio,
            "filename": items[i].metadata.filename,
        }
        for i in range(len(items))
        ]
    res = client.insert(collection_name=COLLECTION_NAME, data=data)
    return res["insert_count"]


def search_multimodal(query, top_k:int):
     multimodal_vector = encode_query([query])
     text_vector = model.encode([query])
    
    image_resultados = client.search(
        collection_name = IMAGE_COLLECTION_NAME,
        data=vector,
        output_fields=[
            "data",
            "type",
            "fase_historia",
            "path_imagen",
            "path_audio",
            "filename"],
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )

    text_resultados = client.search(
        collection_name = TEXT_COLLECTION_NAME,
        data=vector,
        output_fields=[
            "data",
            "type",
            "fase_historia",
            "path_imagen",
            "path_audio",
            "filename"],
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )



    host = "http://localhost:8000/images"


    return [
        {
            "filename": resultado["entity"].get("filename"),
            "score": round(resultado["distance"], 2),
            "author": resultado["entity"].get("author"),
            "date": resultado["entity"].get("date"),
            "type": resultado["entity"].get("type"),
            "data": resultado["entity"].get("data"),
            "url": f"{host}/{resultado['entity']['filename']}" if resultado["entity"]["type"] == "image" else None
        }
        for resultado in image_resultados+text_resultados
    ]
