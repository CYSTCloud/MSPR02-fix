"""
Routes API pour EPIVIZ 4.1
--------------------------
Définit tous les endpoints API pour l'accès aux données historiques,
prédictions et métadonnées.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from ..core.logging_config import get_logger, trace_logs
from ..data.access.manager import data_manager
from ..models.loaders.registry import model_registry
from ..models.predictors.covid_predictor import covid_predictor

# Créer le routeur API
router = APIRouter()

# Logger pour ce module
logger = get_logger("epiviz_api.routes")


# Modèles de données Pydantic pour la validation et la documentation
class CountryInfo(BaseModel):
    """Informations sur un pays disponible."""
    
    name: str = Field(..., description="Nom du pays")
    has_enhanced_model: bool = Field(False, description="Si un modèle amélioré est disponible")
    available_models: List[str] = Field(default_factory=list, description="Types de modèles disponibles")
    data_quality: str = Field("standard", description="Qualité des données disponibles")


class HistoricalDataParams(BaseModel):
    """Paramètres pour les requêtes de données historiques."""
    
    country: str = Field(..., description="Pays pour lequel récupérer les données")
    start_date: Optional[str] = Field(None, description="Date de début (format: YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Date de fin (format: YYYY-MM-DD)")
    metrics: Optional[List[str]] = Field(
        default_factory=lambda: ["total_cases", "new_cases", "total_deaths", "new_deaths"],
        description="Métriques à inclure dans les données"
    )


class PredictionParams(BaseModel):
    """Paramètres pour les requêtes de prédictions."""
    
    country: str = Field(..., description="Pays pour lequel générer des prédictions")
    days: int = Field(14, description="Nombre de jours à prédire", ge=1, le=60)
    model_type: str = Field("xgboost", description="Type de modèle à utiliser")
    use_enhanced: bool = Field(False, description="Utiliser le pipeline de prédiction amélioré")


class PredictionPoint(BaseModel):
    """Point de données de prédiction individuel."""
    
    date: str = Field(..., description="Date de la prédiction (format: YYYY-MM-DD)")
    new_cases: int = Field(..., description="Nouveaux cas prédits")
    total_cases: int = Field(..., description="Total des cas prédits")
    lower_bound: int = Field(..., description="Borne inférieure de l'intervalle de confiance")
    upper_bound: int = Field(..., description="Borne supérieure de l'intervalle de confiance")
    estimation: bool = Field(False, description="Si cette prédiction est une estimation approximative")


class PredictionResponse(BaseModel):
    """Réponse contenant des prédictions."""
    
    country: str = Field(..., description="Pays pour lequel les prédictions ont été générées")
    predictions: List[PredictionPoint] = Field(..., description="Liste des points de prédiction")
    model_used: str = Field(..., description="Type de modèle utilisé pour les prédictions")
    prediction_days: int = Field(..., description="Nombre de jours prédits")
    generated_at: str = Field(..., description="Horodatage de génération des prédictions")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Métriques de qualité du modèle")


# Routes pour les métadonnées
@router.get("/countries", response_model=List[CountryInfo], tags=["Metadata"])
async def get_available_countries():
    """
    Récupère la liste des pays disponibles avec leurs métadonnées.
    """
    try:
        # Récupérer la liste des pays disponibles
        countries = data_manager.get_available_countries()
        
        # Récupérer les pays avec modèles améliorés
        enhanced_countries = model_registry.get_enhanced_countries()
        
        # Construire la réponse
        result = []
        for country in countries:
            # Vérifier les modèles disponibles
            available_models = []
            try:
                available_models = model_registry.get_available_model_types(country)
            except:
                pass
            
            # Déterminer la qualité des données
            data_quality = "enhanced" if country in enhanced_countries else "standard"
            
            result.append(CountryInfo(
                name=country,
                has_enhanced_model=country in enhanced_countries,
                available_models=available_models,
                data_quality=data_quality
            ))
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la liste des pays: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la liste des pays: {str(e)}"
        )


@router.get("/models/{country}", tags=["Metadata"])
async def get_available_models(country: str = Path(..., description="Pays pour lequel récupérer les modèles")):
    """
    Récupère les types de modèles disponibles pour un pays spécifique.
    """
    try:
        model_types = model_registry.get_available_model_types(country)
        return {
            "country": country,
            "models": model_types,
            "has_enhanced_model": country in model_registry.get_enhanced_countries()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles pour {country}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Aucun modèle trouvé pour {country}: {str(e)}"
        )


# Routes pour les données historiques
@router.get("/historical/{country}", tags=["Historical Data"])
@trace_logs
async def get_historical_data(
    country: str = Path(..., description="Pays pour lequel récupérer les données"),
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    metrics: Optional[str] = Query(None, description="Métriques à inclure (séparées par des virgules)")
):
    """
    Récupère les données historiques COVID-19 pour un pays spécifique.
    
    - **country**: Pays pour lequel récupérer les données
    - **start_date**: Date de début optionnelle (format: YYYY-MM-DD)
    - **end_date**: Date de fin optionnelle (format: YYYY-MM-DD)
    - **metrics**: Liste de métriques à inclure, séparées par des virgules
    """
    try:
        # Traiter les métriques si spécifiées
        metrics_list = None
        if metrics:
            metrics_list = [m.strip() for m in metrics.split(",")]
        
        # Récupérer les données
        df = data_manager.get_historical_data(
            country=country,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics_list
        )
        
        # Convertir en format JSON
        data = df.to_dict(orient="records")
        
        # Convertir les dates en chaînes pour la sérialisation JSON
        for item in data:
            if "date_value" in item and hasattr(item["date_value"], "strftime"):
                item["date"] = item["date_value"].strftime("%Y-%m-%d")
                del item["date_value"]
        
        return {
            "country": country,
            "data": data,
            "total_records": len(data),
            "start_date": data[0]["date"] if data else None,
            "end_date": data[-1]["date"] if data else None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données historiques pour {country}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Erreur lors de la récupération des données pour {country}: {str(e)}"
        )


@router.get("/compare", tags=["Historical Data"])
@trace_logs
async def compare_countries(
    countries: str = Query(..., description="Liste de pays séparés par des virgules"),
    metric: str = Query("total_cases", description="Métrique à comparer"),
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)")
):
    """
    Compare une métrique spécifique entre plusieurs pays.
    
    - **countries**: Liste de pays séparés par des virgules
    - **metric**: Métrique à comparer (par défaut: total_cases)
    - **start_date**: Date de début optionnelle
    - **end_date**: Date de fin optionnelle
    """
    try:
        # Traiter la liste des pays
        country_list = [c.strip() for c in countries.split(",")]
        
        # Récupérer les données
        df = data_manager.get_multi_country_data(
            countries=country_list,
            start_date=start_date,
            end_date=end_date,
            metric=metric
        )
        
        # Formater les données pour la réponse
        result = {}
        for country in country_list:
            country_data = df[df["country"] == country]
            if not country_data.empty:
                data_points = []
                for _, row in country_data.iterrows():
                    date_str = row["date_value"].strftime("%Y-%m-%d") if hasattr(row["date_value"], "strftime") else str(row["date_value"])
                    data_points.append({
                        "date": date_str,
                        metric: float(row[metric]) if metric in row else None
                    })
                result[country] = data_points
        
        return {
            "metric": metric,
            "countries": country_list,
            "data": result,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison des pays: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la comparaison des pays: {str(e)}"
        )


# Routes pour les prédictions
@router.get("/predict/{country}", response_model=PredictionResponse, tags=["Predictions"])
@trace_logs
async def predict_cases(
    country: str = Path(..., description="Pays pour lequel générer des prédictions"),
    days: int = Query(14, description="Nombre de jours à prédire", ge=1, le=60),
    model_type: str = Query("xgboost", description="Type de modèle à utiliser"),
    use_enhanced: bool = Query(False, description="Utiliser le pipeline de prédiction amélioré")
):
    """
    Génère des prédictions de cas COVID-19 pour un pays spécifique.
    
    - **country**: Pays pour lequel générer des prédictions
    - **days**: Nombre de jours à prédire (défaut: 14, max: 60)
    - **model_type**: Type de modèle à utiliser (défaut: xgboost)
    - **use_enhanced**: Utiliser le pipeline de prédiction amélioré (défaut: false)
    """
    try:
        # Générer les prédictions
        prediction_result = covid_predictor.predict(
            country=country,
            days=days,
            model_type=model_type,
            use_enhanced=use_enhanced
        )
        
        return prediction_result
    except Exception as e:
        logger.error(f"Erreur lors de la génération des prédictions pour {country}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des prédictions pour {country}: {str(e)}"
        )


@router.get("/latest", tags=["Historical Data"])
@trace_logs
async def get_latest_data(countries: Optional[str] = Query(None, description="Liste de pays séparés par des virgules")):
    """
    Récupère les données les plus récentes pour tous les pays ou une liste spécifique.
    
    - **countries**: Liste optionnelle de pays séparés par des virgules
    """
    try:
        # Traiter la liste des pays si spécifiée
        country_list = None
        if countries:
            country_list = [c.strip() for c in countries.split(",")]
        
        # Récupérer les données
        df = data_manager.get_latest_data(countries=country_list)
        
        # Convertir en format JSON
        data = df.to_dict(orient="records")
        
        # Convertir les dates en chaînes pour la sérialisation JSON
        for item in data:
            if "date_value" in item and hasattr(item["date_value"], "strftime"):
                item["date"] = item["date_value"].strftime("%Y-%m-%d")
                del item["date_value"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "countries": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des dernières données: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des dernières données: {str(e)}"
        )
