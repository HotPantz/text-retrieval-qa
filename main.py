from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import json
import numpy as np

app = FastAPI()
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

class Document(BaseModel):
    documents: list[str]

class Query(BaseModel):
    query: str

def save_embeddings(data, filename="embeddings.json"):
    try:
        with open(filename, "w") as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Erreur de sauvegarde des embeddings : {e}")
        raise HTTPException(status_code=500, detail="Erreur de sauvegarde des embeddings.")

def load_embeddings(filename="embeddings.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Erreur de format JSON lors du chargement des embeddings.")
        return []

@app.post("/encode_documents")
async def encode_documents(doc: Document):
    embeddings_data = load_embeddings()
    for idx, text in enumerate(doc.documents, start=len(embeddings_data)):
        try:
            embedding = model.encode(text).tolist()
        except Exception as e:
            print(f"Erreur d'encodage pour le document '{text}': {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de l'encodage du document.")
        
        embeddings_data.append({"id": idx, "text": text, "embedding": embedding})
    save_embeddings(embeddings_data)
    return {"status": "success", "message": "Documents encoded and stored successfully"}

@app.post("/search_documents")
async def search_documents(query: Query):
    try:
        query_embedding = model.encode(query.query)
    except Exception as e:
        print(f"Erreur lors de l'encodage de la requête : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'encodage de la requête.")

    embeddings_data = load_embeddings()
    if not embeddings_data:
        raise HTTPException(status_code=404, detail="Aucun document encodé n'a été trouvé.")

    results = []
    for doc in embeddings_data:
        try:
            if not isinstance(doc["embedding"], list):
                print(f"Erreur : embedding du document {doc['id']} n'est pas une liste.")
                continue
            
            similarity = util.cos_sim(query_embedding, np.array(doc["embedding"], dtype=np.float32)).item()
            results.append({"id": doc["id"], "text": doc["text"], "similarity_score": similarity})
        except Exception as e:
            print(f"Erreur lors du calcul de la similarité pour le document {doc['id']} : {e}")
            continue  

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
    return {"relevant_documents": results[:5]}
