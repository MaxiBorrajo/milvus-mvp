import os
import time

from fastapi.responses import JSONResponse
from pymilvus import MilvusClient
from app.multimodal_encoder import encode_text, encode_image
from app.milvus_client import model, client

COLLECTION_NAME_MULTIMODAL = "multimodal_collection"
COLLECTION_NAME_TEXT = "text_collection"

def setup_multimodal():
    if client.has_collection(COLLECTION_NAME_MULTIMODAL):
        client.drop_collection(COLLECTION_NAME_MULTIMODAL)
    client.create_collection(
        collection_name=COLLECTION_NAME_MULTIMODAL,
        dimension=512,  # CLIP ViT-B/32 produce vectores de 512 dimensiones
        auto_id=True,
        enable_dynamic_field=True
    )
    if client.has_collection(COLLECTION_NAME_TEXT):
        client.drop_collection(COLLECTION_NAME_TEXT)
    client.create_collection(
        collection_name=COLLECTION_NAME_TEXT,
        dimension=768,  # CLIP ViT-B/32 produce vectores de 512 dimensiones
        auto_id=True,
        enable_dynamic_field=True
    )


def insert_multimodal(items, data_type):
    if data_type == "image":
        vectores = encode_image([item.data for item in items])
        data = [
            {
                "vector": vectores[i],
                "data": items[i].data,
                "type": data_type,
                **vars(items[i].metadata)
            }
            for i in range(len(items))
        ]
        res = client.insert(collection_name=COLLECTION_NAME_MULTIMODAL, data=data)
        return res["insert_count"]

    elif data_type == "text":
        textos = [item.data for item in items]
        vectores_texto = model.encode(textos)
        data_texto = [
            {
                "vector": vectores_texto[i],
                "data": textos[i],
                "type": data_type,
                **vars(items[i].metadata)
            }
            for i in range(len(items))
        ]
        
        res_texto = client.insert(collection_name=COLLECTION_NAME_TEXT, data=data_texto)
        return res_texto["insert_count"]

def search_multimodal(query, type, tipo):
    vector_multimodal = encode_text(query)
    vector_text = model.encode([query])

    output_fields = ["id", "filename", "tipo_fragmento", "type", "data"]

    # Buscar imagen (multimodal)
    resultados_multimodal = client.search(
        collection_name=COLLECTION_NAME_MULTIMODAL,
        data=[vector_multimodal],
        output_fields=output_fields,
        search_params={"metric_type": "COSINE"},
        filter=f'tipo_fragmento == "{tipo}"',
        limit=1
    )

    # Determinar cuántos resultados de texto buscar
    num_imagenes = len(resultados_multimodal[0]) if resultados_multimodal and len(resultados_multimodal) > 0 else 0
    texto_limit = 2 if num_imagenes == 1 else 3

    # Buscar texto
    resultados_texto = client.search(
        collection_name=COLLECTION_NAME_TEXT,
        data=vector_text,
        output_fields=output_fields,
        search_params={"metric_type": "COSINE"},
        filter=f'tipo_fragmento == "{tipo}"',
        limit=texto_limit
    )

    todos_resultados = []
    host = "http://localhost:8000/images"

    from copy import deepcopy

    def procesar_resultados(resultados, fuente):
        lista = []
        if resultados:
            for r in resultados[0]:
                entity = deepcopy(r["entity"])  # 👈 importante
                entity["id"] = r["id"]  # opcional, si querés usar el ID del resultado
                if entity.get("type") == "image" and entity.get("filename"):
                    entity["url"] = f"{host}/{entity['filename']}"
                else:
                    entity["url"] = None
                lista.append(entity)
        return lista


    todos_resultados.extend(procesar_resultados(resultados_multimodal, "multimodal"))
    todos_resultados.extend(procesar_resultados(resultados_texto, "text"))


    return JSONResponse(content=todos_resultados)
