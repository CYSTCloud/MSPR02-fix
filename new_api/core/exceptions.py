"""
Gestionnaires d'exceptions sophistiqués pour l'API EPIVIZ 4.1
-------------------------------------------------------------
Implémente un système complet de gestion d'exceptions avec hiérarchie
d'exceptions personnalisées, middlewares de récupération et formatage
standardisé des réponses d'erreur.
"""

import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from .logging_config import get_logger

# Logger pour ce module
logger = get_logger("epiviz_api.exceptions")


# Modèles Pydantic pour la structure des réponses d'erreur
class ErrorDetail(BaseModel):
    """Modèle pour les détails d'une erreur spécifique."""
    loc: Optional[List[Union[str, int]]] = None
    msg: str
    type: str
    code: Optional[str] = None
    ctx: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Modèle pour la réponse standardisée en cas d'erreur."""
    status: str = "error"
    code: int
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None


# Hiérarchie d'exceptions personnalisées
class EPIVIZException(Exception):
    """Classe de base pour toutes les exceptions spécifiques à l'application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[Dict[str, Any]]] = None,
        code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or []
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class DataNotFoundError(EPIVIZException):
    """Exception levée lorsque des données requises ne sont pas trouvées."""
    
    def __init__(
        self,
        message: str = "Les données demandées n'ont pas été trouvées",
        details: Optional[List[Dict[str, Any]]] = None,
        code: str = "DATA_NOT_FOUND",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
            code=code,
        )


class ModelNotFoundError(EPIVIZException):
    """Exception levée lorsqu'un modèle requis n'est pas trouvé."""
    
    def __init__(
        self,
        message: str = "Le modèle demandé n'a pas été trouvé",
        details: Optional[List[Dict[str, Any]]] = None,
        code: str = "MODEL_NOT_FOUND",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
            code=code,
        )


class DataValidationError(EPIVIZException):
    """Exception levée lors de la validation des données."""
    
    def __init__(
        self,
        message: str = "Les données ne respectent pas le schéma attendu",
        details: Optional[List[Dict[str, Any]]] = None,
        code: str = "DATA_VALIDATION_ERROR",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            code=code,
        )


class PredictionError(EPIVIZException):
    """Exception levée lors d'une erreur dans le processus de prédiction."""
    
    def __init__(
        self,
        message: str = "Erreur lors de la génération des prédictions",
        details: Optional[List[Dict[str, Any]]] = None,
        code: str = "PREDICTION_ERROR",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            code=code,
        )


class ConfigurationError(EPIVIZException):
    """Exception levée lors d'une erreur de configuration."""
    
    def __init__(
        self,
        message: str = "Erreur de configuration de l'application",
        details: Optional[List[Dict[str, Any]]] = None,
        code: str = "CONFIGURATION_ERROR",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            code=code,
        )


# Gestionnaires d'exceptions pour FastAPI
def create_error_response(
    status_code: int,
    message: str,
    request: Request,
    details: Optional[List[Dict[str, Any]]] = None,
    exc_info: Optional[tuple] = None,
) -> JSONResponse:
    """
    Crée une réponse d'erreur standardisée.
    
    Args:
        status_code: Code de statut HTTP
        message: Message d'erreur principal
        request: Objet de requête FastAPI
        details: Détails supplémentaires sur l'erreur
        exc_info: Informations sur l'exception (type, valeur, traceback)
        
    Returns:
        Réponse JSON formatée
    """
    # Préparer les détails d'erreur
    error_details = []
    if details:
        for detail in details:
            error_details.append(ErrorDetail(**detail))
    
    # Récupérer l'ID de requête et l'ID de trace s'ils existent
    request_id = getattr(request.state, "request_id", None)
    trace_id = getattr(request.state, "trace_id", None)
    
    # Construire la réponse d'erreur
    error_response = ErrorResponse(
        status="error",
        code=status_code,
        message=message,
        details=error_details if error_details else None,
        path=str(request.url),
        request_id=request_id,
        trace_id=trace_id,
    )
    
    # Journaliser l'erreur avec contexte
    log_context = {
        "status_code": status_code,
        "path": str(request.url),
        "method": request.method,
        "request_id": request_id,
        "trace_id": trace_id,
        "client_ip": request.client.host if request.client else None,
    }
    
    if details:
        log_context["details"] = details
    
    if exc_info:
        log_context["exception_type"] = exc_info[0].__name__
        log_context["exception_value"] = str(exc_info[1])
        log_context["traceback"] = "".join(traceback.format_exception(*exc_info))
    
    logger.error(f"Erreur HTTP {status_code}: {message}", data=log_context)
    
    # Renvoyer la réponse JSON
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error_response),
        headers={"Access-Control-Allow-Origin": "*"},
    )


# Gestionnaires d'exceptions spécifiques
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Gestionnaire pour les exceptions HTTP standard."""
    details = [{"msg": exc.detail, "type": "http_exception"}]
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        request=request,
        details=details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Gestionnaire pour les erreurs de validation de requête."""
    details = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", "Erreur de validation"),
            "type": error.get("type", "validation_error"),
        }
        details.append(error_detail)
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Erreur de validation des données de la requête",
        request=request,
        details=details,
    )


async def epiviz_exception_handler(request: Request, exc: EPIVIZException) -> JSONResponse:
    """Gestionnaire pour les exceptions spécifiques à l'application."""
    details = []
    if exc.details:
        for detail in exc.details:
            if isinstance(detail, dict):
                if "msg" not in detail:
                    detail["msg"] = str(exc)
                if "type" not in detail:
                    detail["type"] = exc.__class__.__name__
                details.append(detail)
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        request=request,
        details=details if details else None,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Gestionnaire pour toutes les exceptions non gérées."""
    exc_info = sys.exc_info()
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Erreur interne du serveur",
        request=request,
        details=[{"msg": str(exc), "type": exc.__class__.__name__}],
        exc_info=exc_info,
    )


# Middleware de stabilité pour la gestion globale des exceptions
async def stability_middleware(request: Request, call_next):
    """
    Middleware assurant la stabilité de l'API même en cas d'erreur catastrophique.
    
    Enveloppe l'exécution de la requête dans un try/except pour capturer toutes
    les exceptions, y compris celles qui pourraient survenir dans d'autres middlewares.
    """
    import uuid
    
    # Générer un ID de requête unique pour traçabilité
    request.state.request_id = str(uuid.uuid4())
    
    try:
        # Tentative normale de traitement
        response = await call_next(request)
        return response
    except Exception as e:
        # Capture de toutes les exceptions non gérées
        exc_info = sys.exc_info()
        
        logger.critical(
            f"Exception catastrophique non gérée: {str(e)}",
            exc_info=True,
            data={"request_id": request.state.request_id, "path": str(request.url)}
        )
        
        # Réponse dégradée mais fonctionnelle
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Erreur critique du serveur",
            request=request,
            exc_info=exc_info,
        )


# Fonction pour configurer les gestionnaires d'exception sur l'application
def configure_exception_handlers(app: FastAPI) -> None:
    """
    Configure tous les gestionnaires d'exception sur l'application FastAPI.
    
    Args:
        app: Instance de l'application FastAPI
    """
    # Middleware de stabilité (doit être ajouté en premier)
    app.middleware("http")(stability_middleware)
    
    # Gestionnaires d'exceptions spécifiques
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(EPIVIZException, epiviz_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Gestionnaires pour les exceptions personnalisées
    app.add_exception_handler(DataNotFoundError, epiviz_exception_handler)
    app.add_exception_handler(ModelNotFoundError, epiviz_exception_handler)
    app.add_exception_handler(DataValidationError, epiviz_exception_handler)
    app.add_exception_handler(PredictionError, epiviz_exception_handler)
    app.add_exception_handler(ConfigurationError, epiviz_exception_handler)
    
    logger.info("Gestionnaires d'exceptions configurés avec succès")
