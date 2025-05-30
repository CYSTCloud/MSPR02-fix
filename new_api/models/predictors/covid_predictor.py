"""
Système de prédiction avancé pour l'API EPIVIZ 4.1
--------------------------------------------------
Implémente des prédicteurs sophistiqués pour générer des
prévisions de cas COVID-19 à partir des modèles entraînés.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from ...core.exceptions import PredictionError
from ...core.logging_config import get_logger, trace_logs
from ...data.access.manager import data_manager
from ..loaders.registry import model_registry

# Logger pour ce module
logger = get_logger("epiviz_api.models.predictors")


class COVIDPredictor:
    """
    Prédicteur avancé pour les cas COVID-19.
    
    Utilise les modèles entraînés pour générer des prédictions
    sophistiquées avec intervalles de confiance et métriques de qualité.
    """
    
    def __init__(self):
        """Initialise le prédicteur COVID-19."""
        self.logger = logger
    
    @trace_logs
    def predict(
        self,
        country: str,
        days: int = 14,
        model_type: str = "xgboost",
        use_enhanced: bool = False
    ) -> Dict[str, any]:
        """
        Génère des prédictions pour un pays spécifique.
        
        Args:
            country: Pays pour lequel générer les prédictions
            days: Nombre de jours à prédire
            model_type: Type de modèle à utiliser
            use_enhanced: Utiliser le pipeline de prédiction amélioré
            
        Returns:
            Dictionnaire contenant les prédictions et métadonnées
            
        Raises:
            PredictionError: Si la génération des prédictions échoue
        """
        self.logger.info(
            f"Génération de prédictions pour {country} sur {days} jours "
            f"avec modèle {model_type} (enhanced: {use_enhanced})"
        )
        
        try:
            # Déterminer le type de modèle effectif
            effective_model_type = "enhanced" if use_enhanced else model_type
            
            # Vérifier si le pays a un modèle amélioré si demandé
            if use_enhanced and not country in model_registry.get_enhanced_countries():
                self.logger.warning(
                    f"Modèle amélioré non disponible pour {country}, "
                    f"utilisation du modèle standard {model_type}"
                )
                effective_model_type = model_type
            
            # Charger le modèle
            model = model_registry.get_model(country, effective_model_type)
            
            # Préparer les données d'entrée pour la prédiction
            X = self._prepare_prediction_data(country)
            
            # Effectuer la prédiction selon le type de modèle
            if use_enhanced:
                predictions = self._generate_enhanced_predictions(model, X, days)
            else:
                predictions = self._generate_standard_predictions(model, X, days)
            
            # Récupérer les métriques du modèle
            metrics = model_registry.get_model_metrics(country, effective_model_type)
            
            # Construire la réponse
            result = {
                "country": country,
                "predictions": predictions,
                "model_used": effective_model_type,
                "prediction_days": days,
                "generated_at": datetime.now().isoformat(),
                "metrics": metrics.get("metrics", {})
            }
            
            self.logger.info(f"Prédictions générées avec succès pour {country}")
            return result
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des prédictions pour {country}: {e}")
            raise PredictionError(
                message=f"Échec de la génération des prédictions pour {country}: {str(e)}",
                details=[{
                    "msg": str(e),
                    "type": "prediction_error",
                    "country": country,
                    "model_type": model_type
                }]
            )
    
    def _prepare_prediction_data(self, country: str) -> pd.DataFrame:
        """
        Prépare les données d'entrée pour la prédiction.
        
        Args:
            country: Pays pour lequel préparer les données
            
        Returns:
            DataFrame prêt pour la prédiction
            
        Raises:
            PredictionError: Si la préparation des données échoue
        """
        try:
            # Récupérer les données historiques les plus récentes
            historical_data = data_manager.get_historical_data(
                country=country,
                metrics=["total_cases", "new_cases", "total_deaths", "new_deaths"]
            )
            
            if historical_data.empty:
                raise PredictionError(
                    message=f"Aucune donnée historique trouvée pour {country}",
                    details=[{
                        "msg": f"Pays: {country}",
                        "type": "no_historical_data"
                    }]
                )
            
            # Trier par date et prendre les 30 derniers jours (ou moins si moins disponible)
            historical_data = historical_data.sort_values("date_value")
            recent_data = historical_data.tail(30)
            
            # Calculer des caractéristiques supplémentaires
            features = self._calculate_features(recent_data)
            
            self.logger.debug(
                f"Données préparées pour {country}: {len(features)} lignes "
                f"avec {len(features.columns)} caractéristiques"
            )
            
            return features
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la préparation des données pour {country}: {e}")
            raise PredictionError(
                message=f"Échec de la préparation des données pour {country}: {str(e)}",
                details=[{
                    "msg": str(e),
                    "type": "data_preparation_error",
                    "country": country
                }]
            )
    
    def _calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule des caractéristiques avancées pour la prédiction.
        
        Args:
            data: DataFrame contenant les données historiques
            
        Returns:
            DataFrame avec caractéristiques calculées
        """
        # Copier pour éviter de modifier l'original
        df = data.copy()
        
        # Calculer la moyenne mobile sur 7 jours pour les nouveaux cas
        if "new_cases" in df.columns:
            df["new_cases_7d_avg"] = df["new_cases"].rolling(window=7, min_periods=1).mean()
        
        # Calculer le taux de croissance des nouveaux cas
        if "new_cases" in df.columns:
            df["new_cases_growth"] = df["new_cases"].pct_change().fillna(0)
            
            # Taux de croissance moyenne sur 7 jours
            df["new_cases_growth_7d_avg"] = df["new_cases_growth"].rolling(window=7, min_periods=1).mean()
        
        # Calculer le taux de mortalité
        if "total_deaths" in df.columns and "total_cases" in df.columns:
            df["mortality_rate"] = (df["total_deaths"] / df["total_cases"].replace(0, np.nan)).fillna(0)
        
        # Ajouter des caractéristiques temporelles
        df["day_of_week"] = df["date_value"].dt.dayofweek
        df["month"] = df["date_value"].dt.month
        df["day"] = df["date_value"].dt.day
        
        # One-hot encoding pour le jour de la semaine
        for i in range(7):
            df[f"dow_{i}"] = (df["day_of_week"] == i).astype(int)
        
        # Remplacer les valeurs infinies ou NaN
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        return df
    
    def _generate_standard_predictions(
        self,
        model: BaseEstimator,
        data: pd.DataFrame,
        days: int
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Génère des prédictions standard à partir d'un modèle scikit-learn.
        
        Args:
            model: Modèle entraîné
            data: DataFrame contenant les caractéristiques
            days: Nombre de jours à prédire
            
        Returns:
            Liste de dictionnaires contenant les prédictions
        """
        # Récupérer la dernière date et les dernières valeurs
        last_date = data["date_value"].max()
        last_row = data.loc[data["date_value"] == last_date].iloc[0]
        last_total_cases = last_row.get("total_cases", 0)
        last_new_cases = last_row.get("new_cases", 0)
        
        # Préparer la liste pour stocker les prédictions
        predictions = []
        
        # Générer des prédictions pour chaque jour
        current_date = last_date
        current_total_cases = last_total_cases
        current_new_cases = last_new_cases
        current_features = last_row.copy()
        
        for i in range(days):
            # Avancer d'un jour
            current_date = current_date + timedelta(days=1)
            
            # Mettre à jour les caractéristiques temporelles
            current_features["day_of_week"] = current_date.dayofweek
            current_features["month"] = current_date.month
            current_features["day"] = current_date.day
            
            # One-hot encoding pour le jour de la semaine
            for j in range(7):
                current_features[f"dow_{j}"] = 1 if current_date.dayofweek == j else 0
            
            # Effectuer la prédiction
            prediction_input = pd.DataFrame([current_features])
            
            try:
                # Prédire les nouveaux cas
                predicted_new_cases = max(0, float(model.predict(prediction_input)[0]))
                
                # Calculer l'intervalle de confiance (estimation simple)
                confidence_factor = 0.2  # 20% d'incertitude
                lower_bound = max(0, predicted_new_cases * (1 - confidence_factor))
                upper_bound = predicted_new_cases * (1 + confidence_factor)
                
                # Mettre à jour les totaux
                current_total_cases += predicted_new_cases
                current_new_cases = predicted_new_cases
                
                # Mettre à jour les caractéristiques pour la prochaine itération
                current_features["new_cases"] = predicted_new_cases
                current_features["total_cases"] = current_total_cases
                
                if "new_cases_7d_avg" in current_features:
                    # Mise à jour approximative de la moyenne mobile
                    current_features["new_cases_7d_avg"] = (
                        current_features["new_cases_7d_avg"] * 0.85 + predicted_new_cases * 0.15
                    )
                
                if "new_cases_growth" in current_features and current_new_cases > 0 and last_new_cases > 0:
                    current_features["new_cases_growth"] = (current_new_cases - last_new_cases) / last_new_cases
                
                # Ajouter la prédiction à la liste
                predictions.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "new_cases": round(predicted_new_cases),
                    "total_cases": round(current_total_cases),
                    "lower_bound": round(lower_bound),
                    "upper_bound": round(upper_bound)
                })
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la prédiction pour le jour {i+1}: {e}")
                # Utiliser une estimation simple pour continuer
                predicted_new_cases = current_new_cases * 1.05  # +5%
                current_total_cases += predicted_new_cases
                
                predictions.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "new_cases": round(predicted_new_cases),
                    "total_cases": round(current_total_cases),
                    "lower_bound": round(predicted_new_cases * 0.8),
                    "upper_bound": round(predicted_new_cases * 1.2),
                    "estimation": True
                })
        
        return predictions
    
    def _generate_enhanced_predictions(
        self,
        model: Any,
        data: pd.DataFrame,
        days: int
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Génère des prédictions améliorées avec un modèle plus sophistiqué.
        
        Args:
            model: Modèle avancé (LSTM ou ensemble)
            data: DataFrame contenant les caractéristiques
            days: Nombre de jours à prédire
            
        Returns:
            Liste de dictionnaires contenant les prédictions
        """
        # Pour les modèles avancés, la logique dépend du type exact de modèle
        # Nous implémentons ici une approche générique qui sera adaptée selon le modèle
        
        try:
            # Récupérer la dernière date et les dernières valeurs
            last_date = data["date_value"].max()
            last_values = data.tail(14)  # Utiliser les 14 derniers jours pour les modèles séquentiels
            
            # Préparer les données d'entrée selon le format attendu par le modèle
            # (cela peut varier selon le type exact de modèle)
            if hasattr(model, "predict_sequence"):
                # Pour les modèles avec méthode personnalisée de prédiction séquentielle
                predictions_data = model.predict_sequence(last_values, days)
            elif hasattr(model, "predict") and "lstm" in str(model.__class__).lower():
                # Pour les modèles LSTM standard
                # Note: Ceci est une approximation, les modèles LSTM réels nécessitent
                # une préparation spécifique des données d'entrée
                X_sequence = self._prepare_sequence_data(last_values)
                raw_predictions = model.predict(X_sequence)
                predictions_data = self._process_lstm_predictions(raw_predictions, last_date, last_values)
            else:
                # Pour les autres modèles, utiliser l'approche standard avec itération
                return self._generate_standard_predictions(model, data, days)
            
            self.logger.info(f"Prédictions améliorées générées avec {len(predictions_data)} points")
            return predictions_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des prédictions améliorées: {e}")
            # En cas d'échec, utiliser la méthode standard
            self.logger.info("Repli sur la méthode de prédiction standard")
            return self._generate_standard_predictions(model, data, days)
    
    def _prepare_sequence_data(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prépare les données de séquence pour les modèles LSTM.
        
        Args:
            data: DataFrame contenant les dernières valeurs
            
        Returns:
            Array numpy formaté pour l'entrée LSTM
        """
        # Cette méthode dépend fortement du format exact attendu par le modèle LSTM
        # Voici une implémentation générique qui devra être adaptée
        
        # Sélectionner les colonnes pertinentes
        features = ["new_cases", "total_cases"]
        if "new_cases_7d_avg" in data.columns:
            features.append("new_cases_7d_avg")
        if "new_cases_growth" in data.columns:
            features.append("new_cases_growth")
        
        # Créer une matrice de caractéristiques
        X = data[features].values
        
        # Normaliser (si nécessaire)
        X = X / np.max(X, axis=0) if np.max(X) > 0 else X
        
        # Reformater pour LSTM: [samples, time steps, features]
        X_reshaped = X.reshape(1, X.shape[0], X.shape[1])
        
        return X_reshaped
    
    def _process_lstm_predictions(
        self,
        raw_predictions: np.ndarray,
        last_date: datetime,
        last_values: pd.DataFrame
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Traite les prédictions brutes du LSTM en format structuré.
        
        Args:
            raw_predictions: Prédictions brutes du modèle
            last_date: Dernière date des données historiques
            last_values: Dernières valeurs des données historiques
            
        Returns:
            Liste de dictionnaires contenant les prédictions formatées
        """
        # Cette méthode dépend du format exact des sorties du modèle LSTM
        # Voici une implémentation générique qui devra être adaptée
        
        predictions = []
        
        # Récupérer la dernière valeur de total_cases
        last_total = last_values["total_cases"].iloc[-1] if "total_cases" in last_values.columns else 0
        
        # Traiter chaque prédiction
        current_date = last_date
        current_total = last_total
        
        for i, pred in enumerate(raw_predictions[0]):
            # Avancer d'un jour
            current_date = current_date + timedelta(days=1)
            
            # Extraire la valeur prédite (supposons que c'est new_cases)
            predicted_value = max(0, float(pred[0]) if pred.shape else float(pred))
            
            # Mettre à jour le total
            current_total += predicted_value
            
            # Calculer l'intervalle de confiance
            confidence = 0.1 + (i * 0.01)  # L'incertitude augmente avec l'horizon de prédiction
            lower_bound = max(0, predicted_value * (1 - confidence))
            upper_bound = predicted_value * (1 + confidence)
            
            # Ajouter à la liste des prédictions
            predictions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "new_cases": round(predicted_value),
                "total_cases": round(current_total),
                "lower_bound": round(lower_bound),
                "upper_bound": round(upper_bound)
            })
        
        return predictions


# Instance globale du prédicteur
covid_predictor = COVIDPredictor()
