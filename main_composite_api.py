from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from config import EMBEDDING_SERVICE_URL, DB_SERVICE_URL

app = FastAPI()

class Document(BaseModel):
    documents: list[str]

@app.post("/process_document")
async def process_document(doc: Document):
    try:
        # Call Embedding Service
        response = requests.post(f"{EMBEDDING_SERVICE_URL}/encode_documents", json=doc.dict(), timeout=10)
        if response.status_code != 200:
            return {"error": f"Embedding service failed: {response.status_code} {response.text}"}
        
        embeddings = response.json()["embeddings"]

        # Insert into Database
        for embedding, text in zip(embeddings, doc.documents):
            db_response = requests.post(f"{DB_SERVICE_URL}/insert_embedding/", 
                                        json={"document_text": text, "embedding": embedding}, 
                                        timeout=10)
            if db_response.status_code != 200:
                return {"error": f"Database service failed: {db_response.status_code} {db_response.text}"}

        return {"status": "success", "message": "Document processed and stored"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/search")
async def search_documents(query: str):
    try:
        # Get query embedding
        response = requests.post(f"{EMBEDDING_SERVICE_URL}/encode_documents", 
                                  json={"documents": [query]}, timeout=10)
        if response.status_code != 200:
            return {"error": f"Embedding service failed: {response.status_code} {response.text}"}

        query_embedding = response.json()["embeddings"][0]

        # Search in Database
        db_response = requests.post(f"{DB_SERVICE_URL}/search_embeddings/", 
                                     json=query_embedding, timeout=10)
        if db_response.status_code != 200:
            return {"error": f"Database service failed: {db_response.status_code} {db_response.text}"}

        search_results = db_response.json()["relevant_documents"]

        # Generate ChatGPT response (placeholder)
        gpt_response = "ChatGPT-enhanced answer based on search results."

        return {"results": search_results, "enhanced_response": gpt_response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
