"""
Adaptateur pour les données brutes (data_to_train_covid19.csv)
-------------------------------------------------------------
Implémente un adaptateur spécialisé pour charger et traiter
le fichier CSV brut contenant les données d'entraînement COVID-19.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from ...core.config import Paths, COLUMN_MAPPING
from ...core.exceptions import DataNotFoundError, DataValidationError
from ...core.logging_config import get_logger, trace_logs
from .base import DataAdapter, DataContext

# Logger pour ce module
logger = get_logger("epiviz_api.data.adapters.raw")


class RawDataAdapter(DataAdapter):
    """
    Adaptateur spécialisé pour les données brutes.
    
    Charge et traite les données depuis le fichier CSV brut principal
    contenant les données historiques COVID-19.
    """
    
    def __init__(self, priority: int = 80):
        """
        Initialise l'adaptateur pour les données brutes.
        
        Args:
            priority: Priorité de l'adaptateur (valeur moyenne par défaut)
        """
        super().__init__(name="raw_data", priority=priority)
        self._data: Optional[pd.DataFrame] = None
        self._available_countries: Set[str] = set()
    
    def can_handle(self, context: DataContext) -> bool:
        """
        Vérifie si cet adaptateur peut gérer le contexte de données spécifié.
        
        Un adaptateur de données brutes peut gérer le contexte si:
        1. Le fichier de données brutes existe
        2. Si un pays spécifique est demandé, il doit être disponible
        
        Args:
            context: Contexte de données à vérifier
            
        Returns:
            True si l'adaptateur peut gérer ce contexte, False sinon
        """
        # Vérifier si le fichier existe
        if not Paths.DATA_DIR.exists():
            return False
        
        # Charger les données si nécessaire pour vérifier les pays disponibles
        if not self._available_countries:
            self._load_metadata()
        
        # Si aucun pays n'est disponible, cet adaptateur ne peut pas gérer la demande
        if not self._available_countries:
            return False
        
        # Si un pays spécifique est demandé, vérifier qu'il est disponible
        if context.country and context.country not in self._available_countries:
            self.logger.debug(
                f"Pays demandé '{context.country}' non disponible dans les données brutes"
            )
            return False
        
        # Si une liste de pays est demandée, vérifier qu'au moins un est disponible
        if context.countries:
            available = [c for c in context.countries if c in self._available_countries]
            if not available:
                self.logger.debug(
                    f"Aucun des pays demandés {context.countries} n'est disponible "
                    f"dans les données brutes"
                )
                return False
        
        return True
    
    def _load_metadata(self) -> None:
        """
        Charge les métadonnées des données brutes pour identifier
        les pays disponibles sans charger toutes les données.
        """
        if not Paths.DATA_DIR.exists():
            self.logger.warning(f"Fichier de données brutes non trouvé: {Paths.DATA_DIR}")
            return
        
        try:
            # Charger uniquement la colonne du pays pour économiser de la mémoire
            country_data = pd.read_csv(Paths.DATA_DIR, usecols=["country"])
            self._available_countries = set(country_data["country"].unique())
            
            self.logger.info(
                f"Métadonnées des données brutes chargées: "
                f"{len(self._available_countries)} pays disponibles"
            )
        except Exception as e:
            # En cas d'erreur (ex: nom de colonne incorrect), essayer une approche plus robuste
            try:
                # Lire les premières lignes pour inférer les colonnes
                df_sample = pd.read_csv(Paths.DATA_DIR, nrows=10)
                
                # Chercher une colonne qui pourrait contenir des noms de pays
                country_columns = [
                    col for col in df_sample.columns 
                    if col.lower() in ["country", "country/region", "location", "region", "country_region"]
                ]
                
                if country_columns:
                    # Utiliser la première colonne identifiée
                    country_col = country_columns[0]
                    country_data = pd.read_csv(Paths.DATA_DIR, usecols=[country_col])
                    self._available_countries = set(country_data[country_col].unique())
                    
                    self.logger.info(
                        f"Métadonnées des données brutes chargées (colonne '{country_col}'): "
                        f"{len(self._available_countries)} pays disponibles"
                    )
                else:
                    self.logger.error(
                        f"Impossible d'identifier une colonne de pays dans les données brutes"
                    )
            except Exception as e2:
                self.logger.error(
                    f"Erreur lors du chargement des métadonnées des données brutes: {e2}"
                )
    
    @trace_logs
    def load_data(self, context: DataContext) -> pd.DataFrame:
        """
        Charge les données brutes selon le contexte spécifié.
        
        Stratégie:
        1. Charger le fichier CSV complet si pas déjà en mémoire
        2. Normaliser les noms de colonnes
        3. Filtrer selon le contexte
        4. Enrichir avec des colonnes calculées si nécessaire
        5. Valider et traiter les données
        
        Args:
            context: Contexte de données contenant les paramètres de filtrage
            
        Returns:
            DataFrame pandas contenant les données demandées
            
        Raises:
            DataNotFoundError: Si les données demandées ne sont pas trouvées
            DataValidationError: Si les données ne respectent pas le schéma attendu
        """
        self.logger.info(f"Chargement des données brutes avec contexte: {context}")
        
        # Charger les données si pas déjà en mémoire
        if self._data is None:
            if not Paths.DATA_DIR.exists():
                raise DataNotFoundError(
                    message=f"Fichier de données brutes non trouvé: {Paths.DATA_DIR}",
                    details=[{
                        "msg": f"Chemin: {Paths.DATA_DIR}",
                        "type": "file_not_found"
                    }]
                )
            
            try:
                self.logger.debug(f"Chargement du fichier {Paths.DATA_DIR}")
                self._data = pd.read_csv(Paths.DATA_DIR)
                self._data = self._normalize_column_names(self._data)
                
                # Mettre à jour la liste des pays disponibles
                if "country" in self._data.columns:
                    self._available_countries = set(self._data["country"].unique())
                
                self.logger.info(
                    f"Données brutes chargées: {len(self._data)} lignes, "
                    f"{len(self._available_countries)} pays"
                )
            except Exception as e:
                raise DataNotFoundError(
                    message=f"Erreur lors du chargement des données brutes: {str(e)}",
                    details=[{
                        "msg": str(e),
                        "type": "data_loading_error"
                    }]
                )
        
        # Copier les données pour éviter de modifier l'original
        data = self._data.copy()
        
        # Filtrer par pays si spécifié
        if context.countries:
            available_countries = [c for c in context.countries if c in self._available_countries]
            if not available_countries:
                raise DataNotFoundError(
                    message=f"Aucun des pays demandés n'est disponible dans les données brutes",
                    details=[{
                        "msg": f"Pays demandés: {', '.join(context.countries)}",
                        "type": "country_not_found"
                    }]
                )
            
            data = data[data["country"].isin(available_countries)]
        
        # Enrichir les données avec des calculs dérivés si nécessaire
        data = self._enrich_data(data)
        
        # Valider les données
        self.validate_data(data, context)
        
        # Appliquer les filtres et transformations standards
        processed_data = self.process_data(data, context)
        
        self.logger.info(
            f"Données brutes traitées: {len(processed_data)} lignes "
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
        if "date_value" not in df.columns:
            date_columns = [col for col in df.columns if "date" in col.lower()]
            if date_columns:
                self.logger.debug(f"Création de date_value à partir de {date_columns[0]}")
                df["date_value"] = pd.to_datetime(df[date_columns[0]])
            else:
                self.logger.warning("Aucune colonne de date trouvée pour créer date_value")
        
        # Convertir date_value en datetime si ce n'est pas déjà le cas
        if "date_value" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["date_value"]):
            df["date_value"] = pd.to_datetime(df["date_value"])
        
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
            
            # Calculer new_deaths à partir des total_deaths estimés
            df = df.sort_values(["country", "date_value"])
            df["new_deaths"] = df.groupby("country")["total_deaths"].diff().fillna(0)
        
        return df
