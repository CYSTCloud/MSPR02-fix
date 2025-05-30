"""
Adaptateur pour les données améliorées (enhanced_data)
-----------------------------------------------------
Implémente un adaptateur spécialisé pour charger et traiter
les fichiers CSV améliorés stockés dans le répertoire enhanced_data.
"""

import os
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from ...core.config import Paths, COLUMN_MAPPING
from ...core.exceptions import DataNotFoundError, DataValidationError
from ...core.logging_config import get_logger, trace_logs
from .base import DataAdapter, DataContext

# Logger pour ce module
logger = get_logger("epiviz_api.data.adapters.enhanced")


class EnhancedDataAdapter(DataAdapter):
    """
    Adaptateur spécialisé pour les données améliorées.
    
    Charge et combine les données améliorées à partir des fichiers CSV
    stockés dans le répertoire enhanced_data.
    """
    
    def __init__(self, priority: int = 100):
        """
        Initialise l'adaptateur pour les données améliorées.
        
        Args:
            priority: Priorité de l'adaptateur (valeur élevée par défaut)
        """
        super().__init__(name="enhanced_data", priority=priority)
        self._cache: Dict[str, pd.DataFrame] = {}
        self._available_countries: Set[str] = set()
        self._scan_available_data()
    
    def _scan_available_data(self) -> None:
        """
        Analyse le répertoire des données améliorées pour identifier
        les pays disponibles et mettre à jour le cache interne.
        """
        if not Paths.ENHANCED_DATA_DIR.exists():
            self.logger.warning(
                f"Répertoire de données améliorées non trouvé: {Paths.ENHANCED_DATA_DIR}"
            )
            return
        
        # Rechercher tous les fichiers CSV dans le répertoire enhanced_data
        csv_files = list(Paths.ENHANCED_DATA_DIR.glob("*_enhanced.csv"))
        
        if not csv_files:
            self.logger.warning("Aucun fichier de données améliorées trouvé")
            return
        
        # Extraire les noms de pays des noms de fichiers
        for file_path in csv_files:
            country_name = file_path.stem.replace("_enhanced", "")
            self._available_countries.add(country_name)
        
        self.logger.info(
            f"Données améliorées disponibles pour {len(self._available_countries)} pays: "
            f"{', '.join(sorted(self._available_countries))}"
        )
    
    def can_handle(self, context: DataContext) -> bool:
        """
        Vérifie si cet adaptateur peut gérer le contexte de données spécifié.
        
        Un adaptateur de données améliorées peut gérer le contexte si:
        1. Le répertoire des données améliorées existe
        2. Il y a des fichiers CSV dans ce répertoire
        3. Si un pays spécifique est demandé, il doit être disponible
        
        Args:
            context: Contexte de données à vérifier
            
        Returns:
            True si l'adaptateur peut gérer ce contexte, False sinon
        """
        # Vérifier si le répertoire existe
        if not Paths.ENHANCED_DATA_DIR.exists():
            return False
        
        # Si aucun pays n'est disponible, cet adaptateur ne peut pas gérer la demande
        if not self._available_countries:
            return False
        
        # Si un pays spécifique est demandé, vérifier qu'il est disponible
        if context.country and context.country not in self._available_countries:
            self.logger.debug(
                f"Pays demandé '{context.country}' non disponible dans les données améliorées"
            )
            return False
        
        # Si une liste de pays est demandée, vérifier qu'au moins un est disponible
        if context.countries:
            available = [c for c in context.countries if c in self._available_countries]
            if not available:
                self.logger.debug(
                    f"Aucun des pays demandés {context.countries} n'est disponible "
                    f"dans les données améliorées"
                )
                return False
        
        return True
    
    @trace_logs
    def load_data(self, context: DataContext) -> pd.DataFrame:
        """
        Charge les données améliorées selon le contexte spécifié.
        
        Stratégie:
        1. Identifier les pays à charger
        2. Charger et combiner les fichiers CSV correspondants
        3. Effectuer les transformations nécessaires
        4. Valider et traiter les données
        
        Args:
            context: Contexte de données contenant les paramètres de filtrage
            
        Returns:
            DataFrame pandas contenant les données demandées
            
        Raises:
            DataNotFoundError: Si les données demandées ne sont pas trouvées
            DataValidationError: Si les données ne respectent pas le schéma attendu
        """
        self.logger.info(f"Chargement des données améliorées avec contexte: {context}")
        
        # Déterminer les pays à charger
        countries_to_load = context.countries if context.countries else list(self._available_countries)
        available_countries = [c for c in countries_to_load if c in self._available_countries]
        
        if not available_countries:
            raise DataNotFoundError(
                message=f"Aucun des pays demandés n'est disponible dans les données améliorées",
                details=[{
                    "msg": f"Pays demandés: {', '.join(countries_to_load)}",
                    "type": "country_not_found"
                }]
            )
        
        # Charger et combiner les données de chaque pays
        dataframes = []
        for country in available_countries:
            # Vérifier si les données sont déjà en cache
            if country in self._cache:
                self.logger.debug(f"Utilisation des données en cache pour {country}")
                dataframes.append(self._cache[country])
                continue
            
            # Charger les données depuis le fichier
            file_path = Paths.ENHANCED_DATA_DIR / f"{country}_enhanced.csv"
            if not file_path.exists():
                self.logger.warning(f"Fichier non trouvé pour {country}: {file_path}")
                continue
            
            try:
                self.logger.debug(f"Chargement du fichier {file_path}")
                df = pd.read_csv(file_path)
                
                # Ajouter la colonne country si elle n'existe pas
                if "country" not in df.columns:
                    df["country"] = country
                
                # Normaliser les noms de colonnes
                df = self._normalize_column_names(df)
                
                # Convertir les dates en datetime
                if "date_value" in df.columns:
                    df["date_value"] = pd.to_datetime(df["date_value"])
                
                # Mettre en cache pour utilisation future
                self._cache[country] = df
                dataframes.append(df)
                
                self.logger.debug(f"Données chargées avec succès pour {country}: {len(df)} lignes")
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des données pour {country}: {e}")
                # Continuer avec les autres pays
        
        # Vérifier que des données ont été chargées
        if not dataframes:
            raise DataNotFoundError(
                message="Aucune donnée améliorée n'a pu être chargée",
                details=[{
                    "msg": f"Pays demandés: {', '.join(available_countries)}",
                    "type": "data_loading_error"
                }]
            )
        
        # Combiner les données
        combined_data = pd.concat(dataframes, ignore_index=True)
        
        # Enrichir les données avec des calculs dérivés si nécessaire
        combined_data = self._enrich_data(combined_data)
        
        # Valider les données
        self.validate_data(combined_data, context)
        
        # Appliquer les filtres et transformations standards
        processed_data = self.process_data(combined_data, context)
        
        self.logger.info(
            f"Données améliorées chargées avec succès: {len(processed_data)} lignes "
            f"pour {len(processed_data['country'].unique())} pays"
        )
        
        return processed_data
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise les noms de colonnes selon la convention de l'application.
        
        Args:
            df: DataFrame à normaliser
            
        Returns:
            DataFrame avec noms de colonnes normalisés
        """
        # Appliquer les mappings connus
        for old_name, new_name in COLUMN_MAPPING.items():
            if old_name in df.columns and new_name not in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Normaliser les noms en minuscules avec underscore
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        
        return df
    
    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrichit les données avec des colonnes calculées supplémentaires.
        
        Args:
            df: DataFrame à enrichir
            
        Returns:
            DataFrame enrichi
        """
        # Créer la colonne date_value si elle n'existe pas
        if "date_value" not in df.columns and "date" in df.columns:
            df["date_value"] = pd.to_datetime(df["date"])
        
        # Calculer new_cases si manquant mais total_cases présent
        if "new_cases" not in df.columns and "total_cases" in df.columns:
            self.logger.debug("Calcul de new_cases à partir de total_cases")
            # Grouper par pays et trier par date pour calculer la différence
            df = df.sort_values(["country", "date_value"])
            df["new_cases"] = df.groupby("country")["total_cases"].diff().fillna(0)
        
        # Calculer total_cases si manquant mais new_cases présent
        if "total_cases" not in df.columns and "new_cases" in df.columns:
            self.logger.debug("Calcul de total_cases à partir de new_cases")
            df = df.sort_values(["country", "date_value"])
            df["total_cases"] = df.groupby("country")["new_cases"].cumsum()
        
        # Calculer new_deaths si manquant mais total_deaths présent
        if "new_deaths" not in df.columns and "total_deaths" in df.columns:
            self.logger.debug("Calcul de new_deaths à partir de total_deaths")
            df = df.sort_values(["country", "date_value"])
            df["new_deaths"] = df.groupby("country")["total_deaths"].diff().fillna(0)
        
        # Calculer total_deaths si manquant mais new_deaths présent
        if "total_deaths" not in df.columns and "new_deaths" in df.columns:
            self.logger.debug("Calcul de total_deaths à partir de new_deaths")
            df = df.sort_values(["country", "date_value"])
            df["total_deaths"] = df.groupby("country")["new_deaths"].cumsum()
        
        # Estimer total_deaths si complètement manquant
        if "total_deaths" not in df.columns and "total_cases" in df.columns:
            self.logger.debug("Estimation de total_deaths à partir de total_cases (taux de mortalité de 2%)")
            df["total_deaths"] = (df["total_cases"] * 0.02).astype(int)
        
        return df
