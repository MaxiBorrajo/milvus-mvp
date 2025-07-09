import os
import time

from pymilvus import MilvusClient
from app.multimodal_encoder import encode_text, encode_image
from app.milvus_client import model, client

COLLECTION_NAME_MULTIMODAL = "multimodal_collection"
COLLECTION_NAME_TEXT = "text_collection"

def setup_multimodal():
    for name in [COLLECTION_NAME_MULTIMODAL, COLLECTION_NAME_TEXT]:
        if client.has_collection(name):
            client.drop_collection(name)
        client.create_collection(
            collection_name=name,
            dimension=768,  # nuevo tamaño para BLIP base
            auto_id=True,
            enable_dynamic_field=True
        )



def insert_multimodal(items, data_type):
    if data_type == "image":
        # Para imágenes: usar encode_image y guardar en multimodal_collection
        vectores = encode_image([item.data for item in items])
        data = [
            {
                "vector": vectores[i],
                "data": items[i].data,
                "type": data_type,
                "filename": items[i].metadata.filename,
                "fase_historia": items[i].metadata.fase_historia,
                "path_imagen": items[i].metadata.path_imagen,
                "path_audio": items[i].metadata.path_audio,
            }
            for i in range(len(items))
        ]
        res = client.insert(collection_name=COLLECTION_NAME_MULTIMODAL, data=data)
        return res["insert_count"]
    
    elif data_type == "text":
        # Para textos: usar encode_text para multimodal y model.encode para text_collection
        textos = [item.data for item in items]
        
        # Procesar con encode_text para multimodal_collection
        vectores_multimodal = []
        for texto in textos:
            vector = encode_text(texto)
            vectores_multimodal.append(vector)
        
        # Procesar con model.encode para text_collection
        vectores_texto = model.encode(textos)
        
        # Insertar en multimodal_collection
        data_multimodal = [
            {
                "vector": vectores_multimodal[i],
                "data": textos[i],
                "type": data_type,
                "filename": items[i].metadata.filename,
                "fase_historia": items[i].metadata.fase_historia,
                "path_imagen": items[i].metadata.path_imagen,
                "path_audio": items[i].metadata.path_audio,
            }
            for i in range(len(items))
        ]
        
        # Insertar en text_collection
        data_texto = [
            {
                "vector": vectores_texto[i],
                "data": textos[i],
                "type": data_type,
                "filename": items[i].metadata.filename,
                "fase_historia": items[i].metadata.fase_historia,
                "path_imagen": items[i].metadata.path_imagen,
                "path_audio": items[i].metadata.path_audio,
            }
            for i in range(len(items))
        ]
        
        res_multimodal = client.insert(collection_name=COLLECTION_NAME_MULTIMODAL, data=data_multimodal)
        res_texto = client.insert(collection_name=COLLECTION_NAME_TEXT, data=data_texto)
        return res_multimodal["insert_count"] + res_texto["insert_count"]


def search_multimodal(query, type, top_k: int):
    # Codificar la query para ambas colecciones
    vector_multimodal = encode_text(query)
    vector_text = model.encode([query])
    
    output_fields = ["filename", "path_audio", "path_imagen", "fase_historia", "type", "data"]
    
    # Buscar en multimodal_collection
    resultados_multimodal = client.search(
        collection_name=COLLECTION_NAME_MULTIMODAL,
        data=[vector_multimodal],
        output_fields=output_fields,
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )
    
    # Buscar en text_collection
    resultados_texto = client.search(
        collection_name=COLLECTION_NAME_TEXT,
        data=vector_text,
        output_fields=output_fields,
        search_params={"metric_type": "COSINE"},
        limit=top_k
    )
    
    # Combinar resultados
    todos_resultados = []
    host = "http://localhost:8000/images"
    
    # Procesar resultados de multimodal_collection
    for resultado in resultados_multimodal:
        entity = resultado["entity"]
        url = None
        if entity.get("type") == "image":
            url = f"{host}/{entity['filename']}"
        
        todos_resultados.append({
            "filename": entity.get("filename"),
            "score": round(resultado["distance"], 2),
            "path_imagen": entity.get("path_imagen"),
            "path_audio": entity.get("path_audio"),
            "fase_historia": entity.get("fase_historia"),
            "type": entity.get("type"),
            "data": entity.get("data"),
            "url": url
        })
    
    # Procesar resultados de text_collection
    for resultado in resultados_texto:
        entity = resultado["entity"]
        url = None
        if entity.get("type") == "image":
            url = f"{host}/{entity['filename']}"
        
        todos_resultados.append({
            "filename": entity.get("filename"),
            "score": round(resultado["distance"], 2),
            "path_imagen": entity.get("path_imagen"),
            "path_audio": entity.get("path_audio"),
            "fase_historia": entity.get("fase_historia"),
            "type": entity.get("type"),
            "data": entity.get("data"),
            "url": url
        })
    
    return todos_resultados
  