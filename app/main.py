from http.client import HTTPException
from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from typing import List
from app.utils import extract_text_from_file
from app.milvus_client import upsert_with_selection,setup_collection, insert_documents, search_documents, insert_images, search_similar_images
import tempfile
import os
from pathlib import Path
from fastapi.responses import FileResponse
from typing import Annotated
from fastapi import HTTPException
import traceback
import tempfile





IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
setup_collection()

# 🧾 Request schemas
class TextItem(BaseModel):
    text: str
    subject: str = "general"

class InsertRequest(BaseModel):
    items: List[TextItem]
 
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# 🔹 Insertar textos
@app.post("/insert")
def insert_texts(req: InsertRequest):
    inserted_count = insert_documents(req.items)
    return {"inserted": inserted_count}

# 🔹 Buscar textos
@app.post("/search")
def search_text(req: SearchRequest):
    results = search_documents(req.query, req.top_k)
    return {
        "query": req.query,
        "results": results
    }

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


class ImagePairUpsertRequest(BaseModel):
    search_image: UploadFile = File(...)
    new_image: UploadFile = File(...)
    filename: str  # Nombre único para la nueva imagen

class UpsertSelectionRequest(BaseModel):
    search_image: UploadFile = File(...)
    new_image: UploadFile = File(...)
    selected_filename: str
    top_k: int = 5

@app.post("/upsert-with-selection")
async def upsert_with_selection_route(
    search_image: UploadFile = File(...),
    new_image: UploadFile = File(...),
    selected_filename: str = Form(...),
    top_k: int = Form(5)
):
    try:
        # Validar archivos
        if not (search_image.content_type.startswith('image/') and 
                new_image.content_type.startswith('image/')):
            raise HTTPException(status_code=400, detail="Solo se aceptan imágenes (JPEG/PNG)")

        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(delete=False) as tmp_search:
            tmp_search.write(await search_image.read())
            search_temp = tmp_search.name
            
        with tempfile.NamedTemporaryFile(delete=False) as tmp_new:
            tmp_new.write(await new_image.read())
            new_temp = tmp_new.name
            
        try:
            result = upsert_with_selection(
                search_temp, 
                new_temp, 
                selected_filename,
                top_k
            )
            return result
        finally:
            os.unlink(search_temp)
            os.unlink(new_temp)
                        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")