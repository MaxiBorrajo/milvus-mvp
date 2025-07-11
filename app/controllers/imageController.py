
import tempfile
import os
import numpy as np
import traceback

from fastapi import File, UploadFile,HTTPException
from fastapi.responses import FileResponse
from fastapi import HTTPException

from matplotlib import pyplot as plt
from fastapi import  File,  UploadFile
from typing import List
from pathlib import Path
from typing import  List

from app.milvus_client import  insert_images, search_similar_images, delete_image_byId,delete_if_similar
from main import app






IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        file_path = IMAGE_DIR / file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        inserted_count = insert_images([str(file_path)], metadata={"filename": file.filename})
        results.append({
            "filename": file.filename,
            "status": "inserted",
            "inserted_count": inserted_count
        })

    return results


@app.post("/search-images")
async def search_images(file: UploadFile = File(...), top_k: int = 5):
    
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        return search_similar_images(tmp_path, top_k)
    except Exception as e:
        return {"error": str(e)}


@app.get("/images/{filename}")
def get_image(filename: str):
    file_path = IMAGE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)




@app.post("/manage-image")
async def manage_image(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        # Guardar imágenes temporales
        suffix1 = os.path.splitext(file1.filename)[1]
        suffix2 = os.path.splitext(file2.filename)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix1) as tmp1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=suffix2) as tmp2:
            # Leer contenido una sola vez
            file1_content = await file1.read()
            file2_content = await file2.read()
            
            tmp1.write(file1_content)
            tmp_path1 = tmp1.name
            tmp2.write(file2_content)
            tmp_path2 = tmp2.name

        # Buscar similitudes para file1
        similar_images = search_similar_images(tmp_path1, top_k=1)
        print(f"DEBUG: Similar images found: {similar_images}")

        # Crear directorio si no existe
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Guardar file2 en IMAGE_DIR
        file2_path = IMAGE_DIR / file2.filename
        with open(file2_path, "wb") as f:
            f.write(file2_content)  # Usamos el contenido ya leído

        # Operación de borrado
        deleted, deleted_filename = delete_if_similar(similar_images, threshold=0)
        
        # Insertar file2 desde el archivo guardado (no el temporal)
        insert_images([str(file2_path)], metadata={"filename": file2.filename})

        return {
            "file1_deleted": deleted,
            "deleted_filename": deleted_filename,
            "file2_inserted": file2.filename,
            "file2_path": str(file2_path),  # Devuelve la ruta para verificación
            "similarity_results": similar_images
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e)}
    finally:
        # Limpiar archivos temporales
        if 'tmp_path1' in locals() and os.path.exists(tmp_path1):
            os.unlink(tmp_path1)
        if 'tmp_path2' in locals() and os.path.exists(tmp_path2):
            os.unlink(tmp_path2)

@app.delete("/delete-image")
async def delete_image(file: UploadFile = File (...)):

    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name 

        similar_images = search_similar_images(tmp_path, top_k=1)
        deleted = False 
        deleted_id = None 
        if similar_images:
            deleted_id = similar_images[0]["id"]
            delete_image_byId(deleted_id)
            deleted = True 

        return {
            "action": "deleted" if deleted else "there are not any similar image",
            "deleted_id": deleted_id if deleted else None,
            "similarity_score": similar_images[0]["score"] if deleted else None
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Limpieza del archivo temporal
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/replace-closest-image")
async def replace_closest_image(file: UploadFile = File(...)):
    try:
        # Guardar imagen temporal
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        file_content = await file.read()

        # Paso 1: Buscar la más cercana
        similar_images = search_similar_images(tmp_path, top_k=1)
        
         # Guardar file2 en IMAGE_DIR
        file_path = IMAGE_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(file_content)  # Usamos el contenido ya leído


        # Paso 2: Eliminar si existe
        deleted = False
        deleted_id = None
        if similar_images:
            deleted_id = similar_images[0]["id"]
            delete_image_byId(deleted_id)
            deleted = True

        insert_images([tmp_path], metadata={"filename": file.filename})

        return {
            "action": "replaced" if deleted else "inserted",
            "deleted_id": deleted_id,
            "new_filename": file.filename,
            "similarity_score": similar_images[0]["score"] if deleted else None
        }

    except Exception as e:
        return {"error": str(e)}
