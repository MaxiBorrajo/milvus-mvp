
import numpy as np
import traceback

from fastapi import File, UploadFile,HTTPException
from fastapi import HTTPException
from fastapi import status
from matplotlib import pyplot as plt
from fastapi import  File,  UploadFile

from typing import List
from pathlib import Path
from typing import  List

from app.utils import extract_text_from_file
from app.milvus_client import vectorsForAFileName,delete_documents_by_filename_service,delete_vectors_by_ids,search_person, setup_collection, insert_documents, search_documents, insert_images, search_similar_images, get_all_vectors, get_all_vectors_from_collection, get_all_vectors_combined, subirImagenes, delete_image_byId, delete_if_similar, get_vectors_for_visualization, insert_persons, PERSON_COLLECTION, vectorsForAFileName, delete_vectors_by_ids, delete_documents_by_filename_service
from main import app, TextItem,InsertRequest







@app.get("/search")
def search_text(query: str, top_k: int = 5):
    results = search_documents(query, top_k)
    return {
        "query": query,
        "results": results
    }

# 🔹 Insertar textos
@app.post("/insert")
def insert_texts(req: InsertRequest):
    inserted_count = insert_documents(req.items)
    return {"inserted": inserted_count}


@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        content = extract_text_from_file(await file.read(), file.filename)
        items = []
        for fragment in content:
            item = TextItem(text=fragment, subject="uploaded")
            items.append(item)
        inserted_count = insert_documents(items, metadata={"filename": file.filename})
        results.append({"filename": file.filename, "status": "inserted", "inserted_count": inserted_count})        

    return results



@app.get("/documents/by-filename/{filename}", response_model=List[TextItem])
async def get_documents_by_filename(filename: str):
    """
    Endpoint para recuperar todos los fragmentos de un archivo específico
    usando el schema TextItem con el filename como subject
    """
    try:
        # 1. Obtener los resultados crudos
        raw_results = vectorsForAFileName(filename)
        
        if not raw_results:
            return []
            
        # 2. Adaptar a TextItem con filename como subject
        formatted_results = []
        for item in raw_results:
            formatted_results.append(
                TextItem(
                    text=item.get("text", ""),
                    subject=item.get("filename", "unknown")  # Usamos el filename como subject
                )
            )
        
        return formatted_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )


@app.delete("/documents/by-filename/{filename}")
async def delete_by_filename_direct(filename: str):
    """
    Endpoint para eliminar documentos por filename
    Returns:
        JSON: Resultado de la operación con status code apropiado
    """
    try:
        result = delete_documents_by_filename_service(filename)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar documentos: {str(e)}"
        )