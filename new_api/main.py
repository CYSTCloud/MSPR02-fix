"""
Point d'entrée principal de l'API EPIVIZ 4.1
--------------------------------------------
Configure et lance l'application FastAPI avec toutes les routes
et middleware nécessaires.
"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import API_VERSION, DEBUG_MODE, APP_NAME, CORS_ALLOWED_ORIGINS
from core.exceptions import (
    APIError, register_exception_handlers, DataNotFoundError, 
    ModelNotFoundError, PredictionError, ValidationError
)
from core.logging_config import get_logger, init_logging
from routes.api import router as api_router

# Initialiser la journalisation
init_logging()
logger = get_logger("epiviz_api.main")

# Créer l'application FastAPI
app = FastAPI(
    title=APP_NAME,
    description="API moderne pour la visualisation et la prédiction de données COVID-19",
    version=API_VERSION,
    debug=DEBUG_MODE,
)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer les gestionnaires d'exceptions
register_exception_handlers(app)

# Inclure les routes de l'API
app.include_router(api_router, prefix="/api")

# Routes de base
@app.get("/")
async def root():
    """Route racine de l'API."""
    return {
        "name": APP_NAME,
        "version": API_VERSION,
        "status": "operational",
        "documentation": "/docs",
    }

@app.get("/health")
async def health_check():
    """Point de terminaison pour la vérification de l'état de santé de l'API."""
    return {
        "status": "healthy",
        "version": API_VERSION,
    }

# Middleware pour la journalisation des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware pour journaliser les requêtes entrantes et leur traitement."""
    logger.info(f"Requête entrante: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"Réponse envoyée: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
        # Renvoyer une réponse d'erreur formatée
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "Une erreur interne est survenue lors du traitement de la requête.",
                "details": str(e) if DEBUG_MODE else "Consultez les journaux pour plus de détails."
            }
        )

# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Démarrage de l'application {APP_NAME} v{API_VERSION}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG_MODE)
