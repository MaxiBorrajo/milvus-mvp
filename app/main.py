import base64
from fastapi import HTTPException
import io
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from matplotlib import pyplot as plt
from pydantic import BaseModel
from typing import List
from utils import extract_text_from_file
from milvus_client import search_person, setup_collection, insert_documents, search_documents, insert_images, search_similar_images, get_all_vectors, get_all_vectors_from_collection, get_all_vectors_combined, insert_persons
import tempfile
import os
from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse, Response
from typing import Annotated
from sklearn.decomposition import PCA
import numpy as np


IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

setup_collection()

@app.get("/")
def read_root():
    return {"message": "Backend funcionando correctamente", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/debug/collections")
def debug_collections():
    """Endpoint para debuggear el estado de las colecciones"""
    try:
        from milvus_client import client, PERSON_COLLECTION, COLLECTION_NAME
        
        collections_info = {}
        
        # Verificar colección de personas
        if client.has_collection(PERSON_COLLECTION):
            collections_info["person_collection"] = {
                "exists": True,
                "name": PERSON_COLLECTION
            }
        else:
            collections_info["person_collection"] = {
                "exists": False,
                "name": PERSON_COLLECTION
            }
        
        # Verificar colección principal
        if client.has_collection(COLLECTION_NAME):
            collections_info["main_collection"] = {
                "exists": True,
                "name": COLLECTION_NAME
            }
        else:
            collections_info["main_collection"] = {
                "exists": False,
                "name": COLLECTION_NAME
            }
        
        return collections_info
        
    except Exception as e:
        return {"error": str(e)}

# 🧾 Request schemas
class TextItem(BaseModel):
    text: str
    subject: str = "general"


class PersonaItem(BaseModel):
    description: str
    name: str

class InsertPersonRequest(BaseModel):
    items: List[PersonaItem]

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
@app.get("/search")
def search_text(query: str, top_k: int = 5):
    results = search_documents(query, top_k)
    return {
        "query": query,
        "results": results
    }

# 🔹 Insertar personas
@app.post('/insert-person')
def insert_person(req: InsertPersonRequest):
    try:
        inserted_count = insert_persons(req.items)
        return {"inserted": inserted_count}
    except Exception as e:
        return {"error": str(e), "inserted": 0}

@app.get("/find-person")
def find_person(query: str, top_k: int = 1):
    try:
        results = search_person(query, top_k)
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        return {
            "query": query,
            "results": [],
            "error": str(e)
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
    data = get_all_vectors(100)
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

def get_vectors_by_collection(collection: str, limit: int):
    """Función helper para obtener vectores según la colección especificada"""
    if collection.lower() == "texts":
        return get_all_vectors_from_collection("demo_collection", limit)
    elif collection.lower() == "images":
        return get_all_vectors_from_collection("images", limit)
    elif collection.lower() == "all":
        return get_all_vectors_combined(limit)
    else:
        raise HTTPException(
            status_code=400, 
            detail="collection debe ser 'texts', 'images' o 'all'"
        )

@app.get("/visualize-2d")
async def visualize_vectors_2d(
    limit: int = 100, 
    collection: str = Query("texts", description="Colección: 'texts', 'images' o 'all'")
):
    """Endpoint que devuelve visualización 2D de vectores usando PCA"""
    data = get_vectors_by_collection(collection, limit)
    
    if not data:
        raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
    # Extraer solo los vectores
    vectors = np.array([d["vector"] for d in data])
    
    # Reducción a 2D usando PCA
    reducer = PCA(n_components=2)
    vectors_2d = reducer.fit_transform(vectors)
    
    # Crear gráfico 2D
    plt.figure(figsize=(10, 8))
    
    # Si tenemos tipos diferentes, usar colores diferentes
    if collection.lower() == "all" and len(data) > 0:
        text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
        image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
        
        if text_indices:
            plt.scatter(vectors_2d[text_indices, 0], vectors_2d[text_indices, 1], 
                       alpha=0.6, s=50, c='blue', label='Textos')
        if image_indices:
            plt.scatter(vectors_2d[image_indices, 0], vectors_2d[image_indices, 1], 
                       alpha=0.6, s=50, c='red', label='Imágenes')
        plt.legend()
    else:
        plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], alpha=0.6, s=50)
    
    plt.title(f"Visualización 2D de {len(vectors)} vectores - {collection.upper()} (PCA)")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.grid(True, alpha=0.3)
    
    # Convertir gráfico a imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return {
        "image_base64": image_base64,
        "method": "PCA",
        "dimensions": 2,
        "collection": collection,
        "total_vectors": len(vectors),
        "original_dimension": vectors.shape[1]
    }

@app.get("/visualize-3d")
async def visualize_vectors_3d(
    limit: int = 100, 
    collection: str = Query("texts", description="Colección: 'texts', 'images' o 'all'")
):
    """Endpoint que devuelve visualización 3D de vectores usando PCA"""
    data = get_vectors_by_collection(collection, limit)
    
    if not data:
        raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
    # Extraer solo los vectores
    vectors = np.array([d["vector"] for d in data])
    
    # Reducción a 3D usando PCA
    reducer = PCA(n_components=3)
    vectors_3d = reducer.fit_transform(vectors)
    
    # Crear gráfico 3D
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Si tenemos tipos diferentes, usar colores diferentes
    if collection.lower() == "all" and len(data) > 0:
        text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
        image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
        
        if text_indices:
            ax.scatter(vectors_3d[text_indices, 0], vectors_3d[text_indices, 1], vectors_3d[text_indices, 2], 
                      alpha=0.6, s=50, c='blue', label='Textos')
        if image_indices:
            ax.scatter(vectors_3d[image_indices, 0], vectors_3d[image_indices, 1], vectors_3d[image_indices, 2], 
                      alpha=0.6, s=50, c='red', label='Imágenes')
        ax.legend()
    else:
        ax.scatter(vectors_3d[:, 0], vectors_3d[:, 1], vectors_3d[:, 2], alpha=0.6, s=50)
    
    ax.set_title(f"Visualización 3D de {len(vectors)} vectores - {collection.upper()} (PCA)")
    ax.set_xlabel("Componente Principal 1")
    ax.set_ylabel("Componente Principal 2")
    ax.set_zlabel("Componente Principal 3")
    
    # Convertir gráfico a imagen
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return {
        "image_base64": image_base64,
        "method": "PCA",
        "dimensions": 3,
        "collection": collection,
        "total_vectors": len(vectors),
        "original_dimension": vectors.shape[1]
    }

@app.get("/download-2d")
async def download_visualization_2d(
    limit: int = 100,
    collection: str = Query("texts", description="Colección: 'texts', 'images' o 'all'")
):
    """Endpoint que devuelve la visualización 2D como archivo PNG descargable"""
    data = get_vectors_by_collection(collection, limit)
    
    if not data:
        raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
    # Extraer solo los vectores
    vectors = np.array([d["vector"] for d in data])
    n_samples, n_features = vectors.shape
    if n_samples < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan al menos 2 vectores para visualización 2D. Solo hay {n_samples} vectores."
        )
    
    # Reducción a 2D usando PCA
    reducer = PCA(n_components=2)
    vectors_2d = reducer.fit_transform(vectors)
    
    # Crear gráfico 2D
    plt.figure(figsize=(10, 8))
    
    # Si tenemos tipos diferentes, usar colores diferentes
    if collection.lower() == "all" and len(data) > 0:
        text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
        image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
        
        if text_indices:
            plt.scatter(vectors_2d[text_indices, 0], vectors_2d[text_indices, 1], 
                       alpha=0.6, s=50, c='blue', label='Textos')
        if image_indices:
            plt.scatter(vectors_2d[image_indices, 0], vectors_2d[image_indices, 1], 
                       alpha=0.6, s=50, c='red', label='Imágenes')
        plt.legend()
    else:
        plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], alpha=0.6, s=50)
    
    plt.title(f"Visualización 2D de {len(vectors)} vectores - {collection.upper()} (PCA)")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.grid(True, alpha=0.3)
    
    # Guardar en buffer y devolver como archivo
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=vectors_2d_{collection}_{len(vectors)}_vectors.png"}
    )

@app.get("/download-3d")
async def download_visualization_3d(
    limit: int = 100,
    collection: str = Query("texts", description="Colección: 'texts', 'images' o 'all'")
):
    """Endpoint que devuelve la visualización 3D como archivo PNG descargable"""
    data = get_vectors_by_collection(collection, limit)
    
    if not data:
        raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
    # Extraer solo los vectores
    vectors = np.array([d["vector"] for d in data])
    n_samples, n_features = vectors.shape
    if n_samples < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan al menos 3 vectores para visualización 3D. Solo hay {n_samples} vectores."
        )
    
    # Reducción a 3D usando PCA
    reducer = PCA(n_components=3)
    vectors_3d = reducer.fit_transform(vectors)
    
    # Crear gráfico 3D
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Si tenemos tipos diferentes, usar colores diferentes
    if collection.lower() == "all" and len(data) > 0:
        text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
        image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
        
        if text_indices:
            ax.scatter(vectors_3d[text_indices, 0], vectors_3d[text_indices, 1], vectors_3d[text_indices, 2], 
                      alpha=0.6, s=50, c='blue', label='Textos')
        if image_indices:
            ax.scatter(vectors_3d[image_indices, 0], vectors_3d[image_indices, 1], vectors_3d[image_indices, 2], 
                      alpha=0.6, s=50, c='red', label='Imágenes')
        ax.legend()
    else:
        ax.scatter(vectors_3d[:, 0], vectors_3d[:, 1], vectors_3d[:, 2], alpha=0.6, s=50)
    
    ax.set_title(f"Visualización 3D de {len(vectors)} vectores - {collection.upper()} (PCA)")
    ax.set_xlabel("Componente Principal 1")
    ax.set_ylabel("Componente Principal 2")
    ax.set_zlabel("Componente Principal 3")
    
    # Guardar en buffer y devolver como archivo
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=vectors_3d_{collection}_{len(vectors)}_vectors.png"}
    )