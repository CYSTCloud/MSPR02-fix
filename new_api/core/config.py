"""
Configuration centrale pour l'API EPIVIZ 4.1
--------------------------------------------
Centralise tous les paramètres et constantes utilisés dans l'application.
Supporte différents environnements (développement, test, production).
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseSettings, Field, root_validator

# Chemin racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chemins principaux
class Paths:
    """Gestion sophistiquée des chemins de l'application."""
    ROOT_DIR = BASE_DIR
    # Chemin vers le répertoire de l'ancienne API (pour la compatibilité)
    OLD_API_DIR = BASE_DIR / "api"
    # Chemin vers le fichier de données brutes
    DATA_DIR = BASE_DIR / "data" / "data_to_train_covid19.csv"
    # Si le fichier ci-dessus n'existe pas, vérifier s'il est dans la racine
    if not DATA_DIR.exists():
        DATA_DIR = BASE_DIR / "data_to_train_covid19.csv"
    # Répertoire des données améliorées
    ENHANCED_DATA_DIR = BASE_DIR / "enhanced_data"
    # Répertoire des modèles entraînés (vérifier plusieurs emplacements possibles)
    MODELS_DIR = BASE_DIR / "models"
    if not MODELS_DIR.exists():
        MODELS_DIR = BASE_DIR / "trained_models"
        if not MODELS_DIR.exists():
            MODELS_DIR = OLD_API_DIR / "models"
    # Autres chemins
    PROCESSED_DATA_DIR = BASE_DIR / "processed_data" / "prepared_covid_data.csv"
    MODEL_DATA_DIR = BASE_DIR / "model_data"
    LOGS_DIR = BASE_DIR / "logs"
    # Créer le répertoire de logs s'il n'existe pas
    if not LOGS_DIR.exists():
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Attention: Impossible de créer le répertoire de logs: {e}")
    
    @classmethod
    def get_enhanced_data_files(cls) -> List[Path]:
        """Récupère tous les fichiers de données améliorées disponibles."""
        if not cls.ENHANCED_DATA_DIR.exists():
            return []
        return list(cls.ENHANCED_DATA_DIR.glob("*_enhanced.csv"))
    
    @classmethod
    def get_country_model_path(cls, country: str, model_type: str) -> Optional[Path]:
        """Récupère le chemin d'un modèle spécifique pour un pays donné."""
        country_dir = cls.MODELS_DIR / country
        if not country_dir.exists():
            return None
        
        model_path = country_dir / f"{model_type}.pkl"
        if model_path.exists():
            return model_path
        
        # Recherche de modèles alternatifs si le modèle demandé n'existe pas
        available_models = list(country_dir.glob("*.pkl"))
        if available_models:
            return available_models[0]
        
        return None
    
    @classmethod
    def ensure_dirs_exist(cls) -> None:
        """S'assure que tous les répertoires nécessaires existent."""
        cls.LOGS_DIR.mkdir(exist_ok=True, parents=True)
        # Ne pas créer les autres répertoires, car ils doivent déjà exister dans le projet

# Configuration de l'environnement
class Settings(BaseSettings):
    """Configuration avancée et paramétrable de l'application."""
    # Informations sur l'application
    APP_NAME: str = "EPIVIZ 4.1 API"
    APP_VERSION: str = "4.1.0"
    APP_DESCRIPTION: str = "API sophistiquée pour la prédiction des cas de COVID-19"
    
    # Configuration de l'environnement
    ENV: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(True, env="DEBUG")
    
    # Configuration du serveur
    HOST: str = Field("127.0.0.1", env="HOST")
    PORT: int = Field(8000, env="PORT")
    
    # Configuration CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization", "Content-Type", "Accept", "Origin", 
        "User-Agent", "DNT", "Cache-Control", "X-Mx-ReqToken", 
        "Keep-Alive", "X-Requested-With", "If-Modified-Since",
        "X-CSRF-Token"
    ]
    
    # Configuration du cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    
    # Configuration des logs
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: Path = Field(Paths.LOGS_DIR / "api.log", env="LOG_FILE")
    
    # Configuration des modèles
    DEFAULT_MODEL_TYPE: str = "xgboost"
    FALLBACK_STRATEGY: str = "simulate"  # Options: simulate, nearest, average
    
    # Paramètres de simulation
    SIMULATION_GROWTH_FACTOR: float = 1.05
    SIMULATION_VOLATILITY: float = 0.2
    
    # Paramètres de pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1000
    
    # Validations avancées
    @root_validator
    def validate_paths(cls, values: Dict) -> Dict:
        """Valide les chemins et adapte la configuration si nécessaire."""
        # Vérification et adaptation des chemins critiques
        if not Paths.MODELS_DIR.exists():
            print(f"AVERTISSEMENT: Répertoire des modèles non trouvé: {Paths.MODELS_DIR}")
        
        if not any([Paths.DATA_DIR.exists(), Paths.ENHANCED_DATA_DIR.exists()]):
            print(f"AVERTISSEMENT: Aucune source de données trouvée. La génération de données simulées sera utilisée.")
        
        # Création des répertoires de logs
        Paths.ensure_dirs_exist()
        
        return values
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Instance de configuration globale
settings = Settings()

# Variables exportées pour l'API principale
API_VERSION = settings.APP_VERSION
DEBUG_MODE = settings.DEBUG
APP_NAME = settings.APP_NAME
CORS_ALLOWED_ORIGINS = settings.CORS_ORIGINS

# Identifiants des pays avec modèles améliorés
ENHANCED_MODEL_COUNTRIES = ["France", "US", "Brazil", "Germany", "Italy", "Spain", "United Kingdom", "China"]

# Colonnes requises pour les opérations de base
REQUIRED_COLUMNS = {
    "essential": ["country", "date_value"],
    "historical": ["total_cases", "new_cases", "total_deaths", "new_deaths"],
    "prediction": ["date", "predicted_cases", "prediction_interval_lower", "prediction_interval_upper"]
}

# Dictionnaire de correspondance pour renommage de colonnes
COLUMN_MAPPING = {
    "Country/Region": "country",
    "Date": "date_value",
    "date": "date_value",
    "confirmed": "total_cases",
    "deaths": "total_deaths",
    "recovered": "total_recovered",
    "active": "active_cases",
}

# Facteurs de croissance pour la génération de données simulées
GROWTH_FACTORS = {
    "US": 1.08,
    "Brazil": 1.07,
    "Russia": 1.06,
    "France": 1.05,
    "default": 1.04
}

# Exportation des objets principaux
__all__ = ["settings", "Paths", "ENHANCED_MODEL_COUNTRIES", "REQUIRED_COLUMNS", "COLUMN_MAPPING", "GROWTH_FACTORS"]
