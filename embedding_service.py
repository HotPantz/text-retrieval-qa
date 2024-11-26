from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

class Document(BaseModel):
    documents: list[str]

# Route d'encodage corrigée
@app.post("/embed/encode_documents")
async def embed(doc: Document):
    try:
        embeddings = [model.encode(text).tolist() for text in doc.documents]
        return {"embeddings": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
