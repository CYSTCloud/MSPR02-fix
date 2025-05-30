"""
Interfaces et classes de base pour les adaptateurs de données
------------------------------------------------------------
Définit l'architecture des adaptateurs permettant d'accéder aux
différentes sources de données de manière unifiée et transparente.
"""

import abc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from ...core.config import REQUIRED_COLUMNS
from ...core.exceptions import DataNotFoundError, DataValidationError
from ...core.logging_config import get_logger

# Logger pour ce module
logger = get_logger("epiviz_api.data.adapters")


class DataContext:
    """
    Contexte de données contenant les paramètres pour la récupération de données.
    
    Permet de passer les paramètres de filtrage et de traitement de manière
    structurée entre les différentes couches de l'application.
    """
    
    def __init__(
        self,
        country: Optional[str] = None,
        countries: Optional[List[str]] = None,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        metric: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        required_columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        **kwargs
    ):
        """
        Initialise un contexte de données avec les paramètres spécifiés.
        
        Args:
            country: Pays individuel pour le filtrage
            countries: Liste de pays pour le filtrage
            start_date: Date de début pour le filtrage temporel
            end_date: Date de fin pour le filtrage temporel
            metric: Métrique principale pour l'analyse
            metrics: Liste de métriques pour l'analyse
            required_columns: Colonnes requises dans les données
            limit: Limite pour la pagination
            offset: Décalage pour la pagination
            sort_by: Colonne pour le tri
            sort_order: Ordre de tri ('asc' ou 'desc')
            **kwargs: Paramètres supplémentaires spécifiques
        """
        # Paramètres de filtrage géographique
        self.country = country
        self.countries = countries or ([country] if country else [])
        
        # Paramètres de filtrage temporel
        self.start_date = start_date
        self.end_date = end_date
        
        # Paramètres de sélection de métriques
        self.metric = metric
        self.metrics = metrics or ([metric] if metric else [])
        
        # Paramètres de structure de données
        self.required_columns = required_columns or REQUIRED_COLUMNS["essential"]
        
        # Paramètres de pagination et tri
        self.limit = limit
        self.offset = offset
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "asc"
        
        # Paramètres supplémentaires
        self.params = kwargs
    
    def __str__(self) -> str:
        """Représentation sous forme de chaîne de caractères."""
        return (
            f"DataContext(country={self.country}, countries={self.countries}, "
            f"start_date={self.start_date}, end_date={self.end_date}, "
            f"metric={self.metric}, metrics={self.metrics})"
        )
    
    def get_param(self, name: str, default: Any = None) -> Any:
        """Récupère un paramètre supplémentaire par son nom."""
        return self.params.get(name, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le contexte en dictionnaire."""
        result = {
            "country": self.country,
            "countries": self.countries,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "metric": self.metric,
            "metrics": self.metrics,
            "required_columns": self.required_columns,
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
        }
        result.update(self.params)
        return result


class DataAdapter(abc.ABC):
    """
    Interface de base pour tous les adaptateurs de données.
    
    Définit le contrat que tous les adaptateurs de données doivent respecter
    pour assurer l'interopérabilité dans le système.
    """
    
    def __init__(self, name: str, priority: int = 0):
        """
        Initialise un adaptateur de données.
        
        Args:
            name: Nom unique de l'adaptateur
            priority: Priorité de l'adaptateur (plus la valeur est élevée, plus
                      l'adaptateur sera prioritaire)
        """
        self.name = name
        self.priority = priority
        self.logger = get_logger(f"epiviz_api.data.adapters.{name}")
    
    @abc.abstractmethod
    def can_handle(self, context: DataContext) -> bool:
        """
        Vérifie si cet adaptateur peut gérer le contexte de données spécifié.
        
        Args:
            context: Contexte de données à vérifier
            
        Returns:
            True si l'adaptateur peut gérer ce contexte, False sinon
        """
        pass
    
    @abc.abstractmethod
    def load_data(self, context: DataContext) -> pd.DataFrame:
        """
        Charge les données selon le contexte spécifié.
        
        Args:
            context: Contexte de données contenant les paramètres de filtrage
            
        Returns:
            DataFrame pandas contenant les données demandées
            
        Raises:
            DataNotFoundError: Si les données demandées ne sont pas trouvées
            DataValidationError: Si les données ne respectent pas le schéma attendu
        """
        pass
    
    def validate_data(self, data: pd.DataFrame, context: DataContext) -> bool:
        """
        Valide que les données respectent le schéma attendu.
        
        Args:
            data: DataFrame à valider
            context: Contexte de données avec les colonnes requises
            
        Returns:
            True si les données sont valides
            
        Raises:
            DataValidationError: Si les données ne respectent pas le schéma attendu
        """
        # Vérifier que les colonnes requises sont présentes
        missing_columns = [col for col in context.required_columns if col not in data.columns]
        if missing_columns:
            raise DataValidationError(
                message=f"Colonnes requises manquantes: {', '.join(missing_columns)}",
                details=[{
                    "msg": f"Colonne manquante: {col}",
                    "type": "missing_column",
                    "loc": ["body", col]
                } for col in missing_columns]
            )
        
        # Vérifier qu'il y a des données
        if data.empty:
            raise DataNotFoundError(
                message="Aucune donnée trouvée correspondant aux critères",
                details=[{
                    "msg": "Données vides",
                    "type": "empty_data",
                    "loc": ["body"]
                }]
            )
        
        return True
    
    def process_data(self, data: pd.DataFrame, context: DataContext) -> pd.DataFrame:
        """
        Effectue le traitement standard des données après chargement.
        
        Inclut le filtrage par pays et dates, la sélection des colonnes,
        le tri et la pagination.
        
        Args:
            data: DataFrame brut chargé
            context: Contexte de données avec les paramètres de traitement
            
        Returns:
            DataFrame traité
        """
        # Filtrage par pays
        if context.countries:
            data = data[data["country"].isin(context.countries)]
        
        # Conversion et filtrage par dates
        if "date_value" in data.columns:
            data["date_value"] = pd.to_datetime(data["date_value"])
            
            if context.start_date:
                start_date = pd.to_datetime(context.start_date)
                data = data[data["date_value"] >= start_date]
            
            if context.end_date:
                end_date = pd.to_datetime(context.end_date)
                data = data[data["date_value"] <= end_date]
        
        # Tri des données
        if context.sort_by and context.sort_by in data.columns:
            ascending = context.sort_order.lower() == "asc"
            data = data.sort_values(by=context.sort_by, ascending=ascending)
        
        # Pagination
        if context.offset is not None:
            data = data.iloc[context.offset:]
        
        if context.limit is not None:
            data = data.iloc[:context.limit]
        
        return data
    
    def __repr__(self) -> str:
        """Représentation de l'adaptateur."""
        return f"{self.__class__.__name__}(name={self.name}, priority={self.priority})"
