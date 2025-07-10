import base64
import io
import tempfile
import os
import json
import numpy as np
import traceback

from fastapi import FastAPI, File, UploadFile, Query, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi import HTTPException
from fastapi import status

from matplotlib import pyplot as plt
from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from typing import List
from pydantic import BaseModel, ValidationError, validator
from pathlib import Path
from sklearn.decomposition import PCA
from typing import  List
from datetime import datetime

from app.utils import extract_text_from_file
from app.milvus_client import search_person, setup_collection, insert_documents, search_documents, insert_images, search_similar_images, get_all_vectors, get_all_vectors_from_collection, get_all_vectors_combined, subirImagenes, delete_image_byId, delete_if_similar, get_vectors_for_visualization, insert_persons, PERSON_COLLECTION, vectorsForAFileName, delete_vectors_by_ids, delete_documents_by_filename_service, count_vectors_by_attribute
from app.multimodal_queries import insert_multimodal, setup_multimodal, search_multimodal






IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

setup_collection()

@app.on_event("startup")
def cargar_imagenes_existentes():
    subirImagenes(IMAGE_DIR, insert_images)
    
setup_multimodal()


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
        from app.milvus_client import client, PERSON_COLLECTION, COLLECTION_NAME
        
        collections_info = {}
        
        collections_info["person_collection"] = {
            "exists": client.has_collection(PERSON_COLLECTION),
            "name": PERSON_COLLECTION
        }
        collections_info["main_collection"] = {
            "exists": client.has_collection(COLLECTION_NAME),
            "name": COLLECTION_NAME
        }
    
        return collections_info
        
    except Exception as e:
        return {"error": str(e)}

class TextItem(BaseModel):
    text: str
    subject: str = "general"


class PersonaItem(BaseModel):
    description: str
    name: str

class InsertPersonRequest(BaseModel):
    items: List[PersonaItem]

class MetadataItem(BaseModel):
    tipo_fragmento: str | None = None
    filename: str | None = None

class MultimodalItem(BaseModel):
    data: str
    metadata: MetadataItem

class MultimodalRequest(BaseModel):
    items: List[MultimodalItem]

class InsertRequest(BaseModel):
    items: List[TextItem]
 
class SearchRequest(BaseModel):
    pregunta: str
    tipo: str

# Modelo de respuesta para la eliminación
class DeleteResponse(BaseModel):
    filename: str
    deleted_count: int
    deleted_ids: List[str]

# 🔹 Insertar textos
@app.post("/insert")
def insert_texts(req: InsertRequest):
    inserted_count = insert_documents(req.items)
    return {"inserted": inserted_count}

# ============= MULTIMODAL ==========================

@app.post("/insert-text-multimodal")
def post_insert_texts_multimodal(req: MultimodalRequest):
    if not req.items:
        return {"inserted": 0, "ratio": "0.00%"}

    inserted_count = insert_multimodal(req.items, "text")
    if inserted_count is None:
        inserted_count = 0
    ratio = (inserted_count / len(req.items) * 100) if len(req.items) > 0 else 0
    return {"inserted": inserted_count, "ratio": f"{ratio:.2f}%"}

@app.post("/insert-image-multimodal")
async def post_insert_images_multimodal(files: List[UploadFile] = File(...), metadatas = Form(...)):
    try:
        json_metadatas = json.loads(metadatas)
        metadatas = [MetadataItem(**metadata) for metadata in json_metadatas]
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(status_code=400, detail="Datos de metadata inv\u00e1lidos")

    if len(files) != len(metadatas):
        raise HTTPException(status_code=400, detail=f"Cantidad de imágenes y metadatos no coinciden. Hay {len(files)} imágenes pero {len(metadatas)} metadatos")

    images = []
    for i, file in enumerate(files):
        if file.filename is None:
            raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")
        file_path = IMAGE_DIR / str(file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        metadata = metadatas[i]
        metadata.filename = file.filename
        images.append(MultimodalItem(data=str(file_path), metadata=metadata))

    inserted_count = insert_multimodal(images, "image")
    if inserted_count is None:
        inserted_count = 0
    ratio = (inserted_count / len(images) * 100) if len(images) > 0 else 0
    return {"inserted": inserted_count, "ratio": f"{ratio:.2f}%"}

@app.get("/search-by-text-multimodal")
def search_multimodal_text(pregunta: str, tipo: str):
    return search_multimodal(pregunta, "text", tipo)

# @app.post("/search-by-image-multimodal")
# async def search_multimodal_image(file: UploadFile = File(...), top_k: int = 5):
#     file_path = IMAGE_DIR / file.filename

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     return search_multimodal(str(file_path), "image", top_k)



@app.get("/search")
def search_text(query: str, top_k: int = 5):
    results = search_documents(query, top_k)
    return {
        "query": query,
        "results": results
    }

@app.post('/insert-person')
def insert_person(req: InsertPersonRequest):
    try:
        inserted_count = insert_persons(req.items)
        return {"inserted": inserted_count}
    except Exception as e:
        return {"error": str(e), "inserted": 0}

@app.get("/find-person")
def find_person(
    query: str, 
    top_k: int = 1,
    metric_type: str = Query("COSINE", description="Tipo de métrica: L2, IP, COSINE, HAMMING, JACCARD")
):
    try:
        results = search_person(query, top_k, metric_type)
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
    
@app.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        if not file.filename:
            continue  # Omitir archivos sin nombre
        file_path = IMAGE_DIR / str(file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        inserted_count = insert_images([str(file_path)], metadata={"filename": file.filename})
        results.append({
            "filename": file.filename,
            "status": "inserted",
            "inserted_count": inserted_count
        })

    return results

@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        if not file.filename:
            continue  # Omitir archivos sin nombre
        contenido_bytes = await file.read()
        # Nos aseguramos de que file.filename es str, nunca None
        filename = str(file.filename)
        content = extract_text_from_file(contenido_bytes, filename)
        items = []
        for fragment in content:
            item = TextItem(text=fragment, subject="uploaded")
            items.append(item)
        inserted_count = insert_documents(items, metadata={"filename": file.filename})
        results.append({"filename": file.filename, "status": "inserted", "inserted_count": inserted_count})        

    return results


@app.post("/search-images")
async def search_images(file: UploadFile = File(...), top_k: int = 5):
    
    try:
        if not file.filename:
            raise ValueError("El archivo no tiene nombre.")
        # Asegurarse de que file.filename es str y no None
        filename = str(file.filename)
        suffix = os.path.splitext(filename)[1]
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
def get_vectors(
    collection: str = Query("texts", description="Colección: 'texts', 'images', 'persons' o 'all'"),
    dim: int = Query(None, description="Dimensión a la que reducir los vectores (opcional)"),
    limit: int = Query(100, description="Número máximo de vectores a devolver")
):
    """
    Devuelve todos los vectores almacenados de la colección especificada con información completa para visualizaciones.
    Si se pasa 'dim', reduce la dimensionalidad de los vectores a ese valor usando PCA.
    """
    data = get_vectors_for_visualization(collection, limit)
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
    
    return {
        "data": data,
        "metadata": {
            "total_vectors": len(data),
            "original_dimension": n_features,
            "reduced_dimension": dim if dim else n_features,
            "collection": collection
        }
    }

def get_vectors_by_collection(collection: str, limit: int):
    """Función helper para obtener vectores según la colección especificada"""
    if collection.lower() == "texts":
        return get_all_vectors_from_collection("demo_collection", limit)
    elif collection.lower() == "images":
        return get_all_vectors_from_collection("images", limit)
    elif collection.lower() == "persons":
        # Usar COSINE por defecto para compatibilidad
        return get_all_vectors_from_collection(f"{PERSON_COLLECTION}_cosine", limit)
    elif collection.lower().startswith("persons_"):
        # Manejar colecciones específicas por métrica (persons_cosine, persons_l2, persons_ip)
        return get_all_vectors_from_collection(collection, limit)
    elif collection.lower() == "all":
        return get_all_vectors_combined(limit)
    else:
        raise HTTPException(
            status_code=400, 
            detail="collection debe ser 'texts', 'images', 'persons', 'persons_cosine', 'persons_l2', 'persons_ip' o 'all'"
        )

@app.get("/visualize-2d")
async def visualize_vectors_2d(
    limit: int = 100, 
    collection: str = Query("texts", description="Colección: 'texts', 'images', 'persons' o 'all'")
):
    """Endpoint que devuelve visualización 2D de vectores usando PCA"""
    data = get_vectors_for_visualization(collection, limit)
    
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
        person_indices = [i for i, d in enumerate(data) if d.get("type") == "person"]
        
        if text_indices:
            plt.scatter(vectors_2d[text_indices, 0], vectors_2d[text_indices, 1], 
                       alpha=0.6, s=50, c='blue', label='Textos')
        if image_indices:
            plt.scatter(vectors_2d[image_indices, 0], vectors_2d[image_indices, 1], 
                       alpha=0.6, s=50, c='red', label='Imágenes')
        if person_indices:
            plt.scatter(vectors_2d[person_indices, 0], vectors_2d[person_indices, 1], 
                       alpha=0.6, s=50, c='green', label='Personas')
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

# @app.get("/visualize-3d")
# async def visualize_vectors_3d(
#     limit: int = 100, 
#     collection: str = Query("texts", description="Colección: 'texts', 'images', 'persons' o 'all'")
# ):
#     """Endpoint que devuelve visualización 3D de vectores usando PCA"""
#     data = get_vectors_for_visualization(collection, limit)
    
#     if not data:
#         raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
#     # Extraer solo los vectores
#     vectors = np.array([d["vector"] for d in data])
    
#     # Reducción a 3D usando PCA
#     reducer = PCA(n_components=3)
#     vectors_3d = reducer.fit_transform(vectors)
    
#     # Crear gráfico 3D
#     fig = plt.figure(figsize=(12, 10))
#     ax = fig.add_subplot(111, projection='3d')
    
#     # Si tenemos tipos diferentes, usar colores diferentes
#     if collection.lower() == "all" and len(data) > 0:
#         text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
#         image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
#         person_indices = [i for i, d in enumerate(data) if d.get("type") == "person"]
        
#         if text_indices:
#             ax.scatter(vectors_3d[text_indices, 0], vectors_3d[text_indices, 1], vectors_3d[text_indices, 2], 
#                       alpha=0.6, s=50, c='blue', label='Textos')
#         if image_indices:
#             ax.scatter(vectors_3d[image_indices, 0], vectors_3d[image_indices, 1], vectors_3d[image_indices, 2], 
#                       alpha=0.6, s=50, c='red', label='Imágenes')
#         if person_indices:
#             ax.scatter(vectors_3d[person_indices, 0], vectors_3d[person_indices, 1], vectors_3d[person_indices, 2], 
#                       alpha=0.6, s=50, c='green', label='Personas')
#         ax.legend()
#     else:
#         ax.scatter(vectors_3d[:, 0], vectors_3d[:, 1], vectors_3d[:, 2], alpha=0.6, s=50)
    
#     ax.set_title(f"Visualización 3D de {len(vectors)} vectores - {collection.upper()} (PCA)")
#     ax.set_xlabel("Componente Principal 1")
#     ax.set_ylabel("Componente Principal 2")
#     ax.set_zlabel("Componente Principal 3")
    
#     # Convertir gráfico a imagen
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
#     buf.seek(0)
#     image_base64 = base64.b64encode(buf.read()).decode('utf-8')
#     plt.close()
    
#     return {
#         "image_base64": image_base64,
#         "method": "PCA",
#         "dimensions": 3,
#         "collection": collection,
#         "total_vectors": len(vectors),
#         "original_dimension": vectors.shape[1]
#     }

# @app.get("/download-2d")
# async def download_visualization_2d(
#     limit: int = 100,
#     collection: str = Query("texts", description="Colección: 'texts', 'images', 'persons' o 'all'")
# ):
#     """Endpoint que devuelve la visualización 2D como archivo PNG descargable"""
#     data = get_vectors_for_visualization(collection, limit)
    
#     if not data:
#         raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
#     # Extraer solo los vectores
#     vectors = np.array([d["vector"] for d in data])
#     n_samples, n_features = vectors.shape
#     if n_samples < 2:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Se necesitan al menos 2 vectores para visualización 2D. Solo hay {n_samples} vectores."
#         )
    
#     # Reducción a 2D usando PCA
#     reducer = PCA(n_components=2)
#     vectors_2d = reducer.fit_transform(vectors)
    
#     # Crear gráfico 2D
#     plt.figure(figsize=(10, 8))
    
#     # Si tenemos tipos diferentes, usar colores diferentes
#     if collection.lower() == "all" and len(data) > 0:
#         text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
#         image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
        
#         if text_indices:
#             plt.scatter(vectors_2d[text_indices, 0], vectors_2d[text_indices, 1], 
#                        alpha=0.6, s=50, c='blue', label='Textos')
#         if image_indices:
#             plt.scatter(vectors_2d[image_indices, 0], vectors_2d[image_indices, 1], 
#                        alpha=0.6, s=50, c='red', label='Imágenes')
#         plt.legend()
#     else:
#         plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], alpha=0.6, s=50)
    
#     plt.title(f"Visualización 2D de {len(vectors)} vectores - {collection.upper()} (PCA)")
#     plt.xlabel("Componente Principal 1")
#     plt.ylabel("Componente Principal 2")
#     plt.grid(True, alpha=0.3)
    
#     # Guardar en buffer y devolver como archivo
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
#     buf.seek(0)
#     plt.close()
    
#     return Response(
#         content=buf.getvalue(),
#         media_type="image/png",
#         headers={"Content-Disposition": f"attachment; filename=vectors_2d_{collection}_{len(vectors)}_vectors.png"}
#     )

# @app.get("/download-3d")
# async def download_visualization_3d(
#     limit: int = 100,
#     collection: str = Query("texts", description="Colección: 'texts', 'images', 'persons' o 'all'")
# ):
#     """Endpoint que devuelve la visualización 3D como archivo PNG descargable"""
#     data = get_vectors_for_visualization(collection, limit)
    
#     if not data:
#         raise HTTPException(status_code=404, detail="No se encontraron vectores")
    
#     # Extraer solo los vectores
#     vectors = np.array([d["vector"] for d in data])
#     n_samples, n_features = vectors.shape
#     if n_samples < 3:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Se necesitan al menos 3 vectores para visualización 3D. Solo hay {n_samples} vectores."
#         )
    
#     # Reducción a 3D usando PCA
#     reducer = PCA(n_components=3)
#     vectors_3d = reducer.fit_transform(vectors)
    
#     # Crear gráfico 3D
#     fig = plt.figure(figsize=(12, 10))
#     ax = fig.add_subplot(111, projection='3d')
    
#     # Si tenemos tipos diferentes, usar colores diferentes
#     if collection.lower() == "all" and len(data) > 0:
#         text_indices = [i for i, d in enumerate(data) if d.get("type") == "text"]
#         image_indices = [i for i, d in enumerate(data) if d.get("type") == "image"]
#         person_indices = [i for i, d in enumerate(data) if d.get("type") == "person"]
        
#         if text_indices:
#             ax.scatter(vectors_3d[text_indices, 0], vectors_3d[text_indices, 1], vectors_3d[text_indices, 2], 
#                       alpha=0.6, s=50, c='blue', label='Textos')
#         if image_indices:
#             ax.scatter(vectors_3d[image_indices, 0], vectors_3d[image_indices, 1], vectors_3d[image_indices, 2], 
#                       alpha=0.6, s=50, c='red', label='Imágenes')
#         if person_indices:
#             ax.scatter(vectors_3d[person_indices, 0], vectors_3d[person_indices, 1], vectors_3d[person_indices, 2], 
#                       alpha=0.6, s=50, c='green', label='Personas')
#         ax.legend()
#     else:
#         ax.scatter(vectors_3d[:, 0], vectors_3d[:, 1], vectors_3d[:, 2], alpha=0.6, s=50)
    
#     ax.set_title(f"Visualización 3D de {len(vectors)} vectores - {collection.upper()} (PCA)")
#     ax.set_xlabel("Componente Principal 1")
#     ax.set_ylabel("Componente Principal 2")
#     ax.set_zlabel("Componente Principal 3")
    
#     # Guardar en buffer y devolver como archivo
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
#     buf.seek(0)
#     plt.close()
    
#     return Response(
#         content=buf.getvalue(),
#         media_type="image/png",
#         headers={"Content-Disposition": f"attachment; filename=vectors_3d_{collection}_{len(vectors)}_vectors.png"}
#     )

@app.post("/manage-image")
async def manage_image(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        # Guardar imágenes temporales
        suffix1 = os.path.splitext(file1.filename or "")[1]
        suffix2 = os.path.splitext(file2.filename or "")[1]
        
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
        if file2.filename is None:
            raise ValueError("El archivo file2 no tiene nombre.")
        file2_path = IMAGE_DIR / Path(file2.filename)
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
        # Asegurarse de que file.filename no sea None antes de usar splitext
        filename = file.filename if file.filename is not None else "tempfile"
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
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
        # Asegurarse de que file.filename no sea None antes de usar splitext
        filename = file.filename if file.filename is not None else "tempfile"
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        similar_images = search_similar_images(tmp_path, top_k=1)
        
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
    
#por ids 
@app.delete("/documents/by-filenamePorIds/{filename}", response_model=DeleteResponse)
async def delete_documents_by_filename(filename: str):
    """
    Endpoint para eliminar todos los documentos asociados a un filename
    """
    try:
        # 1. Obtener todos los documentos del filename
        documents = vectorsForAFileName(filename)
        
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron documentos con el filename: {filename}"
            )
        
        # 2. Extraer los IDs
        ids_to_delete = [str(doc["id"]) for doc in documents]
        
        # 3. Eliminar los documentos
        delete_result = delete_vectors_by_ids(ids_to_delete)
        
        return {
            "filename": filename,
            "deleted_count": len(ids_to_delete),
            "deleted_ids": ids_to_delete
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar documentos: {str(e)}"
        )

@app.get("/count-vectors")
def count_vectors_endpoint(
    collection: str = Query(..., description="Nombre de la colección"),
    field: str = Query(..., description="Campo por el que filtrar"),
    value: str = Query(..., description="Valor del campo a buscar")
):
    """
    Devuelve la cantidad de vectores en una colección según un atributo específico.
    """
    try:
        count = count_vectors_by_attribute(collection, field, value)
        return {
            "collection": collection,
            "field": field,
            "value": value,
            "count": count
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/delete-vector")
def delete_vector_by_id(
    collection: str = Query(..., description="Nombre de la colección"),
    id: int = Query(..., description="ID del vector a eliminar")
):
    """
    Elimina un vector de una colección por su id.
    """
    try:
        from app.milvus_client import client
        client.load_collection(collection)
        res = client.delete(collection_name=collection, ids=[id])
        return {
            "collection": collection,
            "id": id,
            "delete_count": res.get("delete_count", 0),
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}

