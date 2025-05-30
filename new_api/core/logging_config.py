"""
Configuration avancée du système de journalisation pour l'API EPIVIZ 4.1
-------------------------------------------------------------------------
Implémente un système de journalisation sophistiqué avec différents niveaux,
formats, handlers et fonctionnalités avancées pour une traçabilité complète.
"""

import json
import logging
import sys
import time
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .config import settings, Paths

# Classe pour formater les logs au format JSON
class JsonFormatter(logging.Formatter):
    """Formatter sophistiqué pour logs au format JSON structuré."""
    
    def __init__(
        self,
        fmt_keys: Optional[Dict[str, str]] = None,
    ):
        """
        Initialise le formateur avec un mapping de clés personnalisables.
        
        Args:
            fmt_keys: Dictionnaire pour personnaliser les clés dans la sortie JSON
        """
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys else {}
    
    def format(self, record: logging.LogRecord) -> str:
        """Formate un enregistrement de log en JSON."""
        log_data = {
            # Informations temporelles
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
            
            # Informations sur le logger
            "name": record.name,
            "level": record.levelname,
            "level_no": record.levelno,
            
            # Informations sur l'emplacement
            "file": record.pathname,
            "line": record.lineno,
            "module": record.module,
            "function": record.funcName,
            
            # Informations sur le processus
            "process": record.process,
            "process_name": record.processName,
            "thread": record.thread,
            "thread_name": record.threadName,
            
            # Message principal
            "message": record.getMessage(),
        }
        
        # Ajouter des informations d'exception si présentes
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "value": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        
        # Ajouter des informations contextuelles si présentes
        if hasattr(record, "data") and record.data:
            log_data["data"] = record.data
        
        # Ajouter tout attribut personnalisé
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith("_") and key != "args":
                try:
                    # Tenter de sérialiser, ignorer si impossible
                    json.dumps({key: value})
                    log_data[key] = value
                except (TypeError, OverflowError):
                    pass
        
        # Remplacer les clés selon le mapping configuré
        for key, fmt_key in self.fmt_keys.items():
            if key in log_data:
                log_data[fmt_key] = log_data.pop(key)
        
        return json.dumps(log_data)


# Classe d'enregistreur personnalisé pour ajouter des données contextuelles
class ContextLogger(logging.Logger):
    """Logger avancé permettant d'ajouter des données contextuelles aux logs."""
    
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self._context = {}
    
    def set_context(self, **kwargs) -> None:
        """Définit le contexte global pour ce logger."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Efface le contexte global pour ce logger."""
        self._context.clear()
    
    def _log_with_context(
        self,
        level: int,
        msg: str,
        args: tuple,
        exc_info: Optional[tuple] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Ajoute le contexte aux données supplémentaires du log."""
        extra_with_context = extra or {}
        
        # Fusionner le contexte global avec les données spécifiques
        context_data = {**self._context}
        if data:
            context_data.update(data)
        
        if context_data:
            extra_with_context["data"] = context_data
        
        # Ajouter les kwargs comme données supplémentaires
        if kwargs:
            if "data" not in extra_with_context:
                extra_with_context["data"] = {}
            extra_with_context["data"].update(kwargs)
        
        # Appeler la méthode de journalisation originale
        super()._log(
            level, msg, args, exc_info=exc_info, extra=extra_with_context,
            stack_info=stack_info, stacklevel=stacklevel + 1
        )
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log au niveau DEBUG avec contexte et données supplémentaires."""
        self._log_with_context(logging.DEBUG, msg, args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log au niveau INFO avec contexte et données supplémentaires."""
        self._log_with_context(logging.INFO, msg, args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log au niveau WARNING avec contexte et données supplémentaires."""
        self._log_with_context(logging.WARNING, msg, args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log au niveau ERROR avec contexte et données supplémentaires."""
        self._log_with_context(logging.ERROR, msg, args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log au niveau CRITICAL avec contexte et données supplémentaires."""
        self._log_with_context(logging.CRITICAL, msg, args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log d'exception avec contexte et données supplémentaires."""
        kwargs["exc_info"] = kwargs.get("exc_info", True)
        self.error(msg, *args, **kwargs)


# Configuration du système de journalisation
def setup_logging() -> None:
    """Configure le système de journalisation sophistiqué pour l'application."""
    # Remplacer la classe Logger par notre implémentation personnalisée
    logging.setLoggerClass(ContextLogger)
    
    # Récupérer le niveau de log depuis les paramètres
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Créer le répertoire pour les logs s'il n'existe pas
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Formatters
    text_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    json_formatter = JsonFormatter()
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(text_formatter)
    console_handler.setLevel(log_level)
    
    # Handler pour fichier rotatif (taille)
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10_000_000,  # 10 MB
        backupCount=10,
        encoding="utf-8",
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(log_level)
    
    # Handler pour les erreurs critiques avec rotation quotidienne
    critical_handler = TimedRotatingFileHandler(
        filename=log_file.parent / "critical.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    critical_handler.setFormatter(json_formatter)
    critical_handler.setLevel(logging.ERROR)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Supprimer les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Ajouter nos handlers personnalisés
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(critical_handler)
    
    # Configuration spécifique pour les modules de l'application
    app_logger = logging.getLogger("epiviz_api")
    app_logger.setLevel(log_level)
    
    # Réduire le niveau de verbosité pour certaines bibliothèques
    for logger_name in ["uvicorn", "uvicorn.access"]:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = []  # Supprimer les handlers existants
        mod_logger.propagate = False
        
        # Ajouter un handler spécifique pour uvicorn avec niveau moins verbeux
        uvicorn_handler = logging.StreamHandler(sys.stdout)
        uvicorn_handler.setFormatter(text_formatter)
        uvicorn_handler.setLevel(logging.WARNING if logger_name == "uvicorn" else logging.ERROR)
        mod_logger.addHandler(uvicorn_handler)
    
    # Log de démarrage
    app_logger.info(
        "Système de journalisation initialisé",
        data={
            "log_level": settings.LOG_LEVEL,
            "log_file": str(settings.LOG_FILE),
            "environment": settings.ENV,
        }
    )


# Fonction pour obtenir un logger personnalisé
def get_logger(name: str) -> ContextLogger:
    """
    Récupère un logger contextuel personnalisé.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger contextuel configuré
    """
    return logging.getLogger(name)


# Décorateur pour ajouter un ID de trace aux logs d'une fonction
def trace_logs(f):
    """Décorateur pour ajouter un ID de trace aux logs générés dans une fonction."""
    def wrapper(*args, **kwargs):
        trace_id = str(uuid.uuid4())
        logger = get_logger(f.__module__)
        
        if isinstance(logger, ContextLogger):
            logger.set_context(trace_id=trace_id)
        
        try:
            return f(*args, **kwargs)
        finally:
            if isinstance(logger, ContextLogger):
                logger.clear_context()
    
    return wrapper
