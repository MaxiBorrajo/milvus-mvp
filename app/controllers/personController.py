import numpy as np
import traceback

from fastapi import Query

from matplotlib import pyplot as plt

from app.milvus_client import search_person ,  insert_persons, PERSON_COLLECTION
from main import app,InsertPersonRequest

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
    