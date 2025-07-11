
import json
import numpy as np
import traceback

from fastapi import  File, UploadFile, Query, Form, HTTPException

from fastapi import HTTPException

from matplotlib import pyplot as plt
from fastapi import File, Form, UploadFile
from typing import List
from pydantic import ValidationError


from app.repository.multimodalRepositoty.multiModalRepository import insert_multimodal, search_multimodal
from main import app,MultimodalRequest,MultimodalItem,MetadataItem,IMAGE_DIR

@app.post("/insert-text-multimodal")
def post_insert_texts_multimodal(req: MultimodalRequest):
    if not req.items:
        return {"inserted": 0, "ratio": "0.00%"}

    inserted_count = insert_multimodal(req.items, "text")
    ratio = (inserted_count / len(req.items) * 100)
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
        file_path = IMAGE_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        metadata = metadatas[i]
        metadata.filename = file.filename
        images.append(MultimodalItem(data=str(file_path), metadata=metadata))

    inserted_count = insert_multimodal(images, "image")
    ratio = (inserted_count / len(images) * 100)
    return {"inserted": inserted_count, "ratio": f"{ratio:.2f}%"}


@app.get("/search-by-text-multimodal")
def search_multimodal_text(pregunta: str, tipo: str):
    return search_multimodal(pregunta, "text", tipo)