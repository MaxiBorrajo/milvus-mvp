
from sklearn.preprocessing import normalize

from milvus_client import client,model,PERSON_COLLECTION


def insert_persons(persons_list, metadata=None):
    """
    Inserts a list of persons into all Milvus collections with their vector embeddings.
    
    Args:
        persons_list: List of Person objects (with .description, .name, .skills attributes)
        metadata: Optional dictionary of additional metadata (e.g., source_file)
    
    Returns:
        int: Number of persons inserted
    """
    try:
        # Encode person descriptions using model
        vectors = model.encode([person.description for person in persons_list])
        
        # Insert into all metric collections with appropriate normalization
        metrics = ["COSINE", "L2", "IP"]
        
        for metric in metrics:
            collection_name = f"{PERSON_COLLECTION}_{metric.lower()}"
            
            # Prepare data with appropriate normalization for each metric
            if metric == "COSINE":
                # COSINE needs L2 normalization
                normalized_vectors = normalize(vectors, norm='l2')
                data = [
                    {
                        "vector": normalized_vectors[i],
                        "name": persons_list[i].name,
                        "description": persons_list[i].description,
                        "metadata": metadata if metadata else None
                    }
                    for i in range(len(persons_list))
                ]
            else:
                # L2 and IP use raw vectors (no normalization)
                data = [
                    {
                        "vector": vectors[i],
                        "name": persons_list[i].name,
                        "description": persons_list[i].description,
                        "metadata": metadata if metadata else None
                    }
                    for i in range(len(persons_list))
                ]
            
            client.insert(
                collection_name=collection_name,
                data=data
            )
           
        
        return len(data)
    except Exception as e:
        raise e


def search_person(query: str, top_k: int, metric_type: str = "COSINE"):
    try:
        collection_name = f"{PERSON_COLLECTION}_{metric_type.lower()}"
        
        if not client.has_collection(collection_name):
            return []
        
        client.load_collection(collection_name)
        
        encoded_query = model.encode([query])
        
        if metric_type == "COSINE":
            query_vector = normalize(encoded_query, norm='l2')
        else:
            query_vector = encoded_query
        
        res = client.search(
            collection_name=collection_name,
            data=query_vector,
            limit=top_k,
            output_fields=["name", "description"]
        )
        
        results = []
        for hit in res[0]:
            if metric_type == "COSINE":
                similarity = hit["distance"]
            elif metric_type == "L2":
                similarity = max(0, 1 - (hit["distance"] / 1000))
            elif metric_type == "IP":
                similarity = max(0, min(1, hit["distance"] / 100))

            results.append({
                "id": hit["id"],
                "name": hit["entity"]["name"],
                "description": hit["entity"]["description"],
                "similarity": round(similarity, 4)
            })
        
        return results
        
    except Exception as e:
        raise e
