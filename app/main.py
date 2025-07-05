from http.client import HTTPException
from fastapi import FastAPI, File, UploadFile, Form 
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ValidationError
from typing import List
from app.utils import extract_text_from_file
from app.milvus_client import setup_collection, insert_documents, search_documents, insert_images, search_similar_images
from app.multimodal_queries import insert_images_multimodal, insert_text_multimodal, setup_multimodal, search_multimodal
import tempfile
import os
import json
from pathlib import Path
from typing import Annotated, Optional, List



IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
setup_collection()

# ===== MULTIMODAL ======
setup_multimodal()

# 🧾 Request schemas
class TextItem(BaseModel):
    text: str
    subject: str = "general"

class MetadataItem(BaseModel):
    author: str | None = None
    date: str | None = None
    alt: str | None = None

class MultimodalItem(BaseModel):
    data: str
    alt: str = ""
    filename: str | None = None
    author: str | None = None
    date: str | None = None
    alt: str | None = None

class MultimodalRequest(BaseModel):
    items: List[MultimodalItem]

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

# ===== MULTIMODAL ======
@app.post("/insert-text-multimodal")
def post_insert_texts_multimodal(req: MultimodalRequest):
    inserted_count = insert_text_multimodal(req.items)
    ratio = (inserted_count / len(req.items) * 100)
    return {"inserted": inserted_count, "ratio": f"{ratio:.2f}%"}


@app.post("/insert-image-multimodal")
async def post_insert_images_multimodal(files: List[UploadFile] = File(...), metadatas: str = Form(...)):


    try:
        json_metadatas = json.loads(metadatas)
        metadatas = [MetadataItem(**metadata) for metadata in json_metadatas]
    except (json.JSONDecodeError, ValidationError):
        return JSONResponse(status_code=400, content={"error": "Datos de metadata inválidos"})

    if len(files) != len(metadatas):
        return JSONResponse(status_code=400,content={"error": f"La cantidad de imagenes no coincide con los metadatos. Hay {len(files)} imágenes pero {len(metadatas)} metadatos"})
    

    images = []
    for i, file in enumerate(files):
        file_path = IMAGE_DIR / file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())
        metadata = metadatas[i]
        images.append(MultimodalItem(
            data=str(file_path),
            filename=file.filename,
            author=metadata.author,
            date=metadata.date,
            alt=metadata.alt)
        )


    inserted_count = insert_images_multimodal(images)
    ratio = (inserted_count / len(images) * 100)
    return {"inserted": inserted_count, "ratio": f"{ratio:.2f}%"}


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