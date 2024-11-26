from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()

# Configurations des URL des services
SEARCH_SERVICE_URL = "http://localhost:8002/search_embeddings/"
EMBEDDING_SERVICE_URL = "http://127.0.0.1:8001/embed"

# Configuration des templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Affiche le formulaire pour soumettre une requête."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    """Soumet une requête et affiche les résultats."""
    try:
        # Étape 1 : Obtenir l'embedding de la requête
        embedding_response = requests.post(EMBEDDING_SERVICE_URL, json={"documents": [query]})
        if embedding_response.status_code != 200:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Erreur dans le service d'embedding", "query": query},
            )

        embedding = embedding_response.json()["embeddings"][0]

        # Étape 2 : Effectuer une recherche
        search_response = requests.post(SEARCH_SERVICE_URL, json=embedding)
        if search_response.status_code != 200:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Erreur dans le service de recherche", "query": query},
            )

        results = search_response.json().get("relevant_documents", [])

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "query": query, "results": results},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Erreur inattendue : {str(e)}", "query": query},
        )
