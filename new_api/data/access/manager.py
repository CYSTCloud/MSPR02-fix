"""
Gestionnaire d'accès aux données pour l'API EPIVIZ 4.1
------------------------------------------------------
Centralise l'accès aux données en utilisant les différents adaptateurs
disponibles selon une stratégie de priorité.
"""

from typing import Dict, List, Optional, Type, Union

import pandas as pd

from ...core.exceptions import DataNotFoundError
from ...core.logging_config import get_logger, trace_logs
from ..adapters.base import DataAdapter, DataContext
from ..adapters.enhanced_data import EnhancedDataAdapter
from ..adapters.raw_data import RawDataAdapter

# Logger pour ce module
logger = get_logger("epiviz_api.data.access")


class DataAccessManager:
    """
    Gestionnaire central d'accès aux données.
    
    Coordonne l'utilisation des différents adaptateurs de données selon
    une stratégie de priorité, permettant d'accéder aux données de manière
    transparente quelle que soit leur source.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'accès aux données avec les adaptateurs disponibles."""
        self.adapters: List[DataAdapter] = []
        self._initialize_adapters()
    
    def _initialize_adapters(self) -> None:
        """Initialise et enregistre les adaptateurs de données disponibles."""
        # Enregistrer les adaptateurs par ordre de priorité
        self.adapters.append(EnhancedDataAdapter(priority=100))  # Priorité maximale
        self.adapters.append(RawDataAdapter(priority=80))
        
        # Trier les adaptateurs par priorité décroissante
        self.adapters.sort(key=lambda adapter: adapter.priority, reverse=True)
        
        logger.info(
            f"Gestionnaire d'accès aux données initialisé avec {len(self.adapters)} adaptateurs: "
            f"{', '.join(adapter.name for adapter in self.adapters)}"
        )
    
    def register_adapter(self, adapter: DataAdapter) -> None:
        """
        Enregistre un nouvel adaptateur de données.
        
        Args:
            adapter: Adaptateur à enregistrer
        """
        self.adapters.append(adapter)
        # Maintenir le tri par priorité
        self.adapters.sort(key=lambda a: a.priority, reverse=True)
        logger.info(f"Nouvel adaptateur enregistré: {adapter.name} (priorité {adapter.priority})")
    
    @trace_logs
    def get_data(self, context: DataContext) -> pd.DataFrame:
        """
        Récupère les données selon le contexte spécifié en utilisant
        les adaptateurs disponibles par ordre de priorité.
        
        Stratégie:
        1. Parcourir les adaptateurs par ordre de priorité
        2. Utiliser le premier adaptateur capable de gérer le contexte
        3. En cas d'échec, passer à l'adaptateur suivant
        
        Args:
            context: Contexte de données avec les paramètres de filtrage
            
        Returns:
            DataFrame pandas contenant les données demandées
            
        Raises:
            DataNotFoundError: Si aucun adaptateur ne peut fournir les données demandées
        """
        logger.info(f"Récupération de données avec contexte: {context}")
        
        errors = []
        
        for adapter in self.adapters:
            if adapter.can_handle(context):
                logger.debug(f"Tentative d'utilisation de l'adaptateur: {adapter.name}")
                try:
                    data = adapter.load_data(context)
                    logger.info(
                        f"Données récupérées via {adapter.name}: {len(data)} lignes "
                        f"pour {len(data['country'].unique() if 'country' in data.columns else [])} pays"
                    )
                    return data
                except Exception as e:
                    error_msg = f"Échec de l'adaptateur {adapter.name}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    # Continuer avec le prochain adaptateur
        
        # Si on arrive ici, aucun adaptateur n'a pu fournir les données
        error_details = [{"msg": err, "type": "adapter_failure"} for err in errors]
        raise DataNotFoundError(
            message="Impossible de récupérer les données demandées via les adaptateurs disponibles",
            details=error_details
        )
    
    @trace_logs
    def get_historical_data(
        self,
        country: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Récupère les données historiques pour un pays spécifique.
        
        Méthode pratique qui crée le contexte approprié et appelle get_data.
        
        Args:
            country: Pays pour lequel récupérer les données
            start_date: Date de début optionnelle (format: YYYY-MM-DD)
            end_date: Date de fin optionnelle (format: YYYY-MM-DD)
            metrics: Liste de métriques à inclure
            
        Returns:
            DataFrame pandas contenant les données historiques
            
        Raises:
            DataNotFoundError: Si les données ne sont pas trouvées
        """
        context = DataContext(
            country=country,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics or ["total_cases", "new_cases", "total_deaths", "new_deaths"],
            required_columns=["country", "date_value"]
        )
        
        return self.get_data(context)
    
    @trace_logs
    def get_multi_country_data(
        self,
        countries: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        metric: str = "total_cases"
    ) -> pd.DataFrame:
        """
        Récupère les données pour plusieurs pays pour une métrique spécifique.
        
        Méthode pratique pour la comparaison entre pays.
        
        Args:
            countries: Liste des pays à comparer
            start_date: Date de début optionnelle
            end_date: Date de fin optionnelle
            metric: Métrique à comparer
            
        Returns:
            DataFrame pandas contenant les données pour la comparaison
            
        Raises:
            DataNotFoundError: Si les données ne sont pas trouvées
        """
        context = DataContext(
            countries=countries,
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            required_columns=["country", "date_value", metric]
        )
        
        return self.get_data(context)
    
    @trace_logs
    def get_latest_data(self, countries: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Récupère les données les plus récentes pour chaque pays.
        
        Args:
            countries: Liste optionnelle de pays à inclure
            
        Returns:
            DataFrame pandas contenant les dernières données disponibles
            
        Raises:
            DataNotFoundError: Si les données ne sont pas trouvées
        """
        context = DataContext(
            countries=countries,
            required_columns=["country", "date_value"]
        )
        
        # Récupérer toutes les données
        data = self.get_data(context)
        
        # Trouver la date la plus récente pour chaque pays
        latest_data = data.sort_values("date_value").groupby("country").last().reset_index()
        
        logger.info(
            f"Dernières données récupérées pour {len(latest_data)} pays "
            f"à la date {latest_data['date_value'].max() if not latest_data.empty else 'N/A'}"
        )
        
        return latest_data
    
    def get_available_countries(self) -> List[str]:
        """
        Récupère la liste des pays disponibles dans les données.
        
        Returns:
            Liste des pays disponibles, triés par ordre alphabétique
        """
        all_countries = set()
        
        for adapter in self.adapters:
            try:
                # Créer un contexte minimal
                context = DataContext(required_columns=["country"])
                
                if adapter.can_handle(context):
                    # Récupérer seulement la colonne country pour économiser de la mémoire
                    data = adapter.load_data(context)
                    if "country" in data.columns:
                        countries = set(data["country"].unique())
                        all_countries.update(countries)
                        logger.debug(
                            f"Pays trouvés via {adapter.name}: {len(countries)}"
                        )
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des pays via {adapter.name}: {e}")
        
        # Convertir en liste et trier
        countries_list = sorted(list(all_countries))
        logger.info(f"Liste des pays disponibles récupérée: {len(countries_list)} pays")
        
        return countries_list


# Instance globale du gestionnaire d'accès aux données
data_manager = DataAccessManager()
