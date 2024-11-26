from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sentence_transformers import util
import numpy as np
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de l'application FastAPI
app = FastAPI()

# Configuration de la base de données
DATABASE_URL = "mariadb+pymysql://user:12345@localhost/workflow_db"
try:
    engine = create_engine(DATABASE_URL)
    engine.connect()
    logger.info("Database connection successful.")
except Exception as e:
    logger.error(f"Database connection error: {e}")
    raise HTTPException(status_code=500, detail="Database connection failed.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour la table des embeddings
class EmbeddingModel(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Modèle Pydantic pour les données de l'API
class EmbeddingData(BaseModel):
    document_text: str
    embedding: list[float]

# Dépendance pour la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route pour insérer un embedding dans la base de données
@app.post("/insert_embedding/")
def insert_embedding(data: EmbeddingData, db: SessionLocal = Depends(get_db)):
    logger.info(f"Inserting embedding for document: {data.document_text[:30]}...")
    if not isinstance(data.embedding, list) or len(data.embedding) == 0:
        raise HTTPException(status_code=400, detail="Invalid embedding format.")
    try:
        db_embedding = EmbeddingModel(
            document_text=data.document_text,
            embedding=data.embedding
        )
        db.add(db_embedding)
        db.commit()
        db.refresh(db_embedding)
        logger.info(f"Embedding inserted with ID: {db_embedding.id}")
        return {"status": "success", "id": db_embedding.id}
    except Exception as e:
        logger.error(f"Error during insertion: {e}")
        raise HTTPException(status_code=500, detail="Error inserting embedding.")

# Route pour rechercher des embeddings similaires dans la base
@app.post("/search_embeddings/")
def search_embeddings(query_embedding: list[float], db: SessionLocal = Depends(get_db)):
    logger.info("Searching for similar embeddings...")
    if not isinstance(query_embedding, list) or len(query_embedding) == 0:
        raise HTTPException(status_code=400, detail="Invalid query embedding format.")
    try:
        query_vector = np.array(query_embedding)
        results = []

        embeddings = db.execute(select(EmbeddingModel)).scalars().all()
        for doc in embeddings:
            try:
                doc_vector = np.array(doc.embedding)
                similarity = float(util.cos_sim(query_vector, doc_vector).item())
                results.append({"id": doc.id, "document_text": doc.document_text, "similarity_score": similarity})
            except Exception as e:
                logger.warning(f"Error processing document {doc.id}: {e}")
                continue

        results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
        logger.info(f"Search completed. {len(results)} results found.")
        return {"relevant_documents": results[:5]}
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving embeddings.")
