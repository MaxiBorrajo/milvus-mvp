import numpy as np
import numpy as np

from milvus_client import client,COLLECTION_NAME,model

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