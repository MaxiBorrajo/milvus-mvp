from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.milvus_client import setup_collection, insert_documents, search_documents

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
