"""
Registre de modèles pour l'API EPIVIZ 4.1
-----------------------------------------
Implémente un système sophistiqué de découverte, chargement
et gestion des modèles prédictifs.
"""

import os
import pickle
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from ...core.config import Paths, ENHANCED_MODEL_COUNTRIES
from ...core.exceptions import ModelNotFoundError
from ...core.logging_config import get_logger, trace_logs

# Logger pour ce module
logger = get_logger("epiviz_api.models.loaders")


class ModelRegistry:
    """
    Registre central des modèles prédictifs disponibles.
    
    Gère la découverte, le chargement et le cache des modèles
    pour garantir des performances optimales et une utilisation
    efficace des ressources.
    """
    
    def __init__(self):
        """Initialise le registre de modèles avec découverte automatique."""
        self.registry: Dict[str, Dict[str, str]] = {}
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.model_metadata: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._discover_models()
    
    def _discover_models(self) -> None:
        """
        Découvre et enregistre automatiquement tous les modèles disponibles.
        
        Parcourt le répertoire des modèles pour identifier tous les modèles
        disponibles par pays et par type, et les enregistre dans le registre.
        """
        if not Paths.MODELS_DIR.exists():
            logger.warning(f"Répertoire de modèles non trouvé: {Paths.MODELS_DIR}")
            return
        
        logger.info(f"Découverte des modèles dans {Paths.MODELS_DIR}")
        
        # Parcourir les sous-répertoires (un par pays)
        for country_dir in os.listdir(Paths.MODELS_DIR):
            country_path = Path(Paths.MODELS_DIR) / country_dir
            
            if not country_path.is_dir():
                continue
            
            # Initialiser l'entrée pour ce pays
            self.registry[country_dir] = {}
            
            # Chercher tous les fichiers de modèle (.pkl)
            model_files = list(country_path.glob("*.pkl"))
            
            if not model_files:
                logger.warning(f"Aucun modèle trouvé pour {country_dir}")
                continue
            
            # Enregistrer chaque modèle
            for model_file in model_files:
                model_type = model_file.stem
                self.registry[country_dir][model_type] = str(model_file)
                
                # Charger les métadonnées si disponibles
                self._load_model_metadata(country_dir, model_type, model_file)
            
            logger.info(
                f"Modèles découverts pour {country_dir}: "
                f"{', '.join(self.registry[country_dir].keys())}"
            )
        
        # Résumé des modèles découverts
        countries = list(self.registry.keys())
        logger.info(
            f"Découverte des modèles terminée: {len(countries)} pays avec modèles: "
            f"{', '.join(countries)}"
        )
    
    def _load_model_metadata(self, country: str, model_type: str, model_file: Path) -> None:
        """
        Charge les métadonnées d'un modèle si disponibles.
        
        Args:
            country: Pays du modèle
            model_type: Type du modèle
            model_file: Chemin vers le fichier du modèle
        """
        # Initialiser les dictionnaires si nécessaire
        if country not in self.model_metadata:
            self.model_metadata[country] = {}
        
        # Chercher un fichier de métadonnées associé
        metadata_file = model_file.with_suffix('.json')
        if metadata_file.exists():
            try:
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                self.model_metadata[country][model_type] = metadata
                logger.debug(f"Métadonnées chargées pour {country}/{model_type}")
            except Exception as e:
                logger.warning(f"Erreur lors du chargement des métadonnées pour {country}/{model_type}: {e}")
                # Métadonnées par défaut
                self.model_metadata[country][model_type] = {
                    "created_at": datetime.now().isoformat(),
                    "metrics": {}
                }
        else:
            # Chercher dans un fichier CSV de comparaison de modèles
            comparison_file = model_file.parent / "models_comparison.csv"
            if comparison_file.exists():
                try:
                    df = pd.read_csv(comparison_file)
                    # Filtrer pour ce modèle spécifique
                    model_data = df[df["model"] == model_type]
                    if not model_data.empty:
                        # Convertir en dictionnaire de métriques
                        metrics = model_data.iloc[0].to_dict()
                        # Supprimer les colonnes non métriques
                        for key in ["model", "country"]:
                            if key in metrics:
                                del metrics[key]
                        
                        self.model_metadata[country][model_type] = {
                            "created_at": datetime.now().isoformat(),
                            "metrics": metrics
                        }
                        logger.debug(f"Métadonnées extraites du CSV pour {country}/{model_type}")
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction des métadonnées du CSV pour {country}/{model_type}: {e}")
                    # Métadonnées par défaut
                    self.model_metadata[country][model_type] = {
                        "created_at": datetime.now().isoformat(),
                        "metrics": {}
                    }
            else:
                # Aucune métadonnée trouvée, utiliser des valeurs par défaut
                self.model_metadata[country][model_type] = {
                    "created_at": datetime.now().isoformat(),
                    "metrics": {}
                }
    
    def get_available_countries(self) -> List[str]:
        """
        Récupère la liste des pays pour lesquels des modèles sont disponibles.
        
        Returns:
            Liste des pays avec modèles disponibles
        """
        return sorted(list(self.registry.keys()))
    
    def get_available_model_types(self, country: str) -> List[str]:
        """
        Récupère les types de modèles disponibles pour un pays donné.
        
        Args:
            country: Pays pour lequel récupérer les types de modèles
            
        Returns:
            Liste des types de modèles disponibles
            
        Raises:
            ModelNotFoundError: Si aucun modèle n'est disponible pour ce pays
        """
        if country not in self.registry:
            raise ModelNotFoundError(
                message=f"Aucun modèle disponible pour {country}",
                details=[{
                    "msg": f"Pays: {country}",
                    "type": "country_not_found"
                }]
            )
        
        return sorted(list(self.registry[country].keys()))
    
    def has_model(self, country: str, model_type: str = "xgboost") -> bool:
        """
        Vérifie si un modèle spécifique est disponible pour un pays donné.
        
        Args:
            country: Pays à vérifier
            model_type: Type de modèle à vérifier
            
        Returns:
            True si le modèle est disponible, False sinon
        """
        return country in self.registry and model_type in self.registry[country]
    
    def get_enhanced_countries(self) -> List[str]:
        """
        Récupère la liste des pays pour lesquels des modèles améliorés sont disponibles.
        
        Returns:
            Liste des pays avec modèles améliorés
        """
        enhanced_countries = []
        
        for country in self.registry:
            # Vérifier si le pays a un modèle amélioré ou LSTM
            if "enhanced" in self.registry[country] or "lstm" in self.registry[country]:
                enhanced_countries.append(country)
        
        # Ajouter les pays définis comme ayant des modèles améliorés dans la configuration
        for country in ENHANCED_MODEL_COUNTRIES:
            if country in self.registry and country not in enhanced_countries:
                enhanced_countries.append(country)
        
        return sorted(enhanced_countries)
    
    @trace_logs
    def get_model(self, country: str, model_type: str = "xgboost") -> Any:
        """
        Récupère un modèle avec stratégie de repli sophistiquée.
        
        Stratégie:
        1. Essayer de charger le modèle spécifié
        2. Si non disponible, essayer des alternatives similaires
        3. Si toujours pas disponible, lever une exception
        
        Args:
            country: Pays pour lequel récupérer le modèle
            model_type: Type de modèle à récupérer
            
        Returns:
            Modèle chargé
            
        Raises:
            ModelNotFoundError: Si le modèle demandé ou une alternative n'est pas trouvé
        """
        # Vérifier si le modèle est déjà chargé
        if country in self.loaded_models and model_type in self.loaded_models[country]:
            logger.debug(f"Utilisation du modèle {model_type} pour {country} depuis le cache")
            return self.loaded_models[country][model_type]
        
        # Vérifier si le modèle spécifié est disponible
        if self.has_model(country, model_type):
            model_path = self.registry[country][model_type]
            model = self._load_model(model_path, model_type)
            
            # Stocker dans le cache
            if country not in self.loaded_models:
                self.loaded_models[country] = {}
            self.loaded_models[country][model_type] = model
            
            logger.info(f"Modèle {model_type} pour {country} chargé depuis {model_path}")
            return model
        
        # Stratégies de repli
        # 1. Essayer des types de modèles alternatifs
        alternative_types = self._get_alternative_model_types(model_type)
        for alt_type in alternative_types:
            if self.has_model(country, alt_type):
                logger.info(f"Utilisation du modèle alternatif {alt_type} pour {country} à la place de {model_type}")
                return self.get_model(country, alt_type)
        
        # 2. Vérifier si un modèle par défaut est disponible
        if self.has_model(country, "default"):
            logger.info(f"Utilisation du modèle par défaut pour {country}")
            return self.get_model(country, "default")
        
        # Aucun modèle disponible
        raise ModelNotFoundError(
            message=f"Aucun modèle {model_type} ou alternative disponible pour {country}",
            details=[{
                "msg": f"Pays: {country}, Type de modèle: {model_type}",
                "type": "model_not_found"
            }]
        )
    
    def _load_model(self, model_path: str, model_type: str) -> Any:
        """
        Charge un modèle depuis un fichier.
        
        Args:
            model_path: Chemin vers le fichier du modèle
            model_type: Type du modèle (pour journalisation)
            
        Returns:
            Modèle chargé
            
        Raises:
            ModelNotFoundError: Si le chargement échoue
        """
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            logger.debug(f"Modèle {model_type} chargé depuis {model_path}")
            return model
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle {model_type} depuis {model_path}: {e}")
            raise ModelNotFoundError(
                message=f"Erreur lors du chargement du modèle: {str(e)}",
                details=[{
                    "msg": str(e),
                    "type": "model_loading_error"
                }]
            )
    
    def _get_alternative_model_types(self, model_type: str) -> List[str]:
        """
        Récupère une liste de types de modèles alternatifs.
        
        Args:
            model_type: Type de modèle principal
            
        Returns:
            Liste de types de modèles alternatifs par ordre de préférence
        """
        alternatives = {
            "enhanced": ["lstm", "xgboost", "gradient_boosting", "random_forest"],
            "lstm": ["enhanced", "xgboost", "gradient_boosting", "random_forest"],
            "xgboost": ["gradient_boosting", "random_forest", "lstm", "enhanced"],
            "gradient_boosting": ["xgboost", "random_forest", "lstm"],
            "random_forest": ["gradient_boosting", "xgboost", "decision_tree"],
            "linear_regression": ["ridge_regression", "lasso_regression"],
            "ridge_regression": ["lasso_regression", "linear_regression"],
            "lasso_regression": ["ridge_regression", "linear_regression"],
            "decision_tree": ["random_forest", "gradient_boosting"]
        }
        
        return alternatives.get(model_type, ["xgboost", "gradient_boosting", "random_forest"])
    
    def get_model_metrics(self, country: str, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère les métriques pour un modèle spécifique ou tous les modèles d'un pays.
        
        Args:
            country: Pays pour lequel récupérer les métriques
            model_type: Type de modèle spécifique (optionnel)
            
        Returns:
            Dictionnaire de métriques
            
        Raises:
            ModelNotFoundError: Si le pays ou le modèle n'est pas trouvé
        """
        if country not in self.model_metadata:
            raise ModelNotFoundError(
                message=f"Aucune métadonnée disponible pour {country}",
                details=[{
                    "msg": f"Pays: {country}",
                    "type": "country_not_found"
                }]
            )
        
        if model_type:
            if model_type not in self.model_metadata[country]:
                raise ModelNotFoundError(
                    message=f"Aucune métadonnée disponible pour {country}/{model_type}",
                    details=[{
                        "msg": f"Pays: {country}, Type de modèle: {model_type}",
                        "type": "model_not_found"
                    }]
                )
            
            return self.model_metadata[country][model_type]
        
        # Retourner toutes les métriques pour ce pays
        return self.model_metadata[country]
    
    def clear_cache(self, country: Optional[str] = None, model_type: Optional[str] = None) -> None:
        """
        Vide le cache des modèles chargés.
        
        Args:
            country: Pays spécifique à vider (optionnel)
            model_type: Type de modèle spécifique à vider (optionnel)
        """
        if country:
            if country in self.loaded_models:
                if model_type:
                    if model_type in self.loaded_models[country]:
                        del self.loaded_models[country][model_type]
                        logger.info(f"Cache vidé pour {country}/{model_type}")
                else:
                    del self.loaded_models[country]
                    logger.info(f"Cache vidé pour {country}")
        else:
            self.loaded_models = {}
            logger.info("Cache de modèles entièrement vidé")


# Instance globale du registre de modèles
model_registry = ModelRegistry()
