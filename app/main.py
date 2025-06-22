from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.milvus_client import insert_texts, search_text

app = FastAPI()

class InsertPayload(BaseModel):
    texts: List[str]

class QueryPayload(BaseModel):
    query: str
    top_k: int = 3

@app.post("/insert")
def insert(payload: InsertPayload):
    insert_texts(payload.texts)
    return {"inserted": len(payload.texts)}

@app.post("/search")
def search(payload: QueryPayload):
    results = search_text(payload.query, payload.top_k)
    return {"results": results}
