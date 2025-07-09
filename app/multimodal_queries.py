import os
import time

from pymilvus import MilvusClient
from multimodal_encoder import CLIPMultimodal

COLLECTION_NAME = "multimodal"
COLLECTION_DIMENSION = 512

client = MilvusClient(uri="http://localhost:19530")


MODEL_PATH ="openai/clip-vit-base-patch32"
encoder = CLIPMultimodal(MODEL_PATH, MODEL_PATH)

def setup_multimodal():
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name= COLLECTION_NAME,
        vector_field_name="vector",
        dimension= COLLECTION_DIMENSION,
        auto_id=True,
        enable_dynamic_field=True,
        metric_type="COSINE"
    )

def insert_multimodal(items, data_type):
    vectores = encoder.encode_imagenes([item.data for item in items]) if data_type == "image" else encoder.encode_textos([item.data for item in items])
    data = [
        {
            "vector": vectores[i],
            "data": items[i].data,
            "type": data_type,
            "filename": items[i].metadata.filename,
            "author": items[i].metadata.author,
            "date": int(time.mktime(items[i].metadata.date.timetuple())) if items[i].metadata.date else None,
            "alt": items[i].metadata.alt
        }
        for i in range(len(items))
        ]
    res = client.insert(collection_name=COLLECTION_NAME, data=data)
    return res["insert_count"]


def search_multimodal(query, type, top_k:int):
    vector = []
    if type == "text":
        vector = encoder.encode_textos([query])
    elif type == "image":
        vector = encoder.encode_imagenes([query])
    else:
        raise ValueError("Error en tipo")
    
    resultados = client.search(
        collection_name = COLLECTION_NAME,
        data=vector,
        output_fields=["filename", "author", "type", "data", "date"],
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )[0]

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
        for resultado in resultados
    ]
