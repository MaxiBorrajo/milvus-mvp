import os

from pymilvus import MilvusClient
from app.multimodal_encoder import CLIPMultimodal

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

def insert_text_multimodal(items):
    vectores = encoder.encode_textos([item.data for item in items])
    data = [
        {
            "vector": vectores[i],
            "data": items[i].data,
            "type": "text",
            "filename": items[i].filename,
            "author": items[i].author,
            "date": items[i].date,
            "alt": items[i].alt
        }
        for i in range(len(items))
        ]
    res = client.insert(collection_name=COLLECTION_NAME, data=data)
    return res["insert_count"]

def insert_images_multimodal(items):
    vectores = encoder.encode_imagenes([item.data for item in items])
    data = [
        {
            "vector": vectores[i],
            "data": items[i].data,
            "type": "image",
            "filename": items[i].filename,
            "author": items[i].author,
            "date": items[i].date,
            "alt": items[i].alt
        }
        for i in range(len(items))
        ]
    res = client.insert(collection_name=COLLECTION_NAME, data=data)
    return res["insert_count"]

# def search_multimodal_by_text(text, top_k:int):
#     vector = encoder.encode_textos([text])
    
#     resultados = client.search(
#         collection_name = COLLECTION_NAME,
#         data=vector,
#         output_fields=["filename", "author", "type", "text", "date"],
#         search_params={"metric_type": "COSINE"},
#         limit=top_k
#     )

#     host = "http://localhost:8000/images"

#     print(resultados)

#     return [
#         {
#             "filename": get_or_none(resultado["entity"], "filename"),
#             "score": round(1 - resultado["distance"], 5),
#             "author": get_or_none(resultado["entity"], "author"),
#             "date": get_or_none(resultado["entity"], "date"),
#             "type": resultado["entity"].get("type"),
#             "text": get_or_none(resultado["entity"], "text"),
#             "url": f"{host}/{resultado['entity']['filename']}" if resultado["entity"]["type"] == "image" else None
#         }
#         for resultado in resultados[0]
#     ]


def search_multimodal(query, type, top_k:int):
    vector
    if type == "text":
        vector = encoder.encode_textos([query])
    elif type == "image":
        vector = encoder.encode_imagenes([query])
    else:
        raise ValueError("Error en tipo")
    
    resultados = client.search(
        collection_name = COLLECTION_NAME,
        data=vector,
        output_fields=["filename", "author", "type", "text", "date"],
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )

    host = "http://localhost:8000/images"

    print(resultados)

    return [
        {
            "filename": resultado["entity"].get("filename"),
            "score": round(1 - resultado["distance"], 5),
            "author": resultado["entity"].get("author"),
            "date": resultado["entity"].get("date"),
            "type": resultado["entity"].get("type"),
            "text": resultado["entity"].get("text"),
            "url": f"{host}/{resultado['entity']['filename']}" if resultado["entity"]["type"] == "image" else None
        }
        for resultado in resultados[0]
    ]
