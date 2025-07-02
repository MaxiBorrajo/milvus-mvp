from http.client import HTTPException
from fastapi import FastAPI, File, UploadFile, Query
from pydantic import BaseModel
from typing import List
from app.utils import extract_text_from_file
from app.milvus_client import setup_collection, insert_documents, search_documents, insert_images, search_similar_images, get_all_vectors
import tempfile
import os
from pathlib import Path
from fastapi.responses import FileResponse
from typing import Annotated
from sklearn.decomposition import PCA
import numpy as np


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

@app.get('/vectors')
def get_vectors(dim: int = Query(None, description="Dimensión a la que reducir los vectores (opcional)")):
    """
    Devuelve todos los vectores almacenados. Si se pasa 'dim', reduce la dimensionalidad de los vectores a ese valor usando PCA.
    """
    data = get_all_vectors()
    if not data:
        return []
    vectors = np.array([d["vector"] for d in data])
    n_samples, n_features = vectors.shape
    if dim is not None and dim < vectors.shape[1]:
        if dim > n_features:
            raise HTTPException(
                status_code=400,
                detail=f"dim ({dim}) no puede ser mayor que la dimensión original ({n_features})"
            )
        if dim > n_samples:
            raise HTTPException(
                status_code = 400,
                detail=f"dim ({dim}) no puede ser mayor que la cantidad de vectores ({n_samples})"
            )
          
        pca = PCA(n_components=dim)
        reduced = pca.fit_transform(vectors)
        
        for i, d in enumerate(data):
            d["vector"] = reduced[i].tolist()
    return data