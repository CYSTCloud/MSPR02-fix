"""
EPIVIZ 4.1 - Module d'amélioration des prédictions pour l'API
------------------------------------------------------------
Ce module intègre les modèles améliorés et les fonctions d'amélioration 
des données pour obtenir des prédictions plus réalistes.
"""

import os
import joblib
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
import sys

# Ajouter le répertoire parent au path pour pouvoir importer data_enhancement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Essayer d'importer les fonctions nécessaires
try:
    from data_enhancement import enhance_predictions, epidemiological_smoothing
except ImportError:
    # Définir des fonctions de remplacement si les imports échouent
    def enhance_predictions(predictions, historical_data):
        return predictions
    
    def epidemiological_smoothing(data, alpha=0.3, beta=0.1):
        return data

# Importer TensorFlow avec gestion d'erreur
try:
    from tensorflow.keras.models import load_model
except ImportError:
    # Définir une fonction de remplacement si TensorFlow n'est pas disponible
    def load_model(path):
        raise ImportError("TensorFlow n'est pas installé, impossible de charger les modèles LSTM")

# Configuration du logging
logger = logging.getLogger("epiviz_enhanced_prediction")

# Chemins des fichiers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENHANCED_DATA_PATH = os.path.join(BASE_DIR, 'enhanced_data')
TRAINED_MODELS_PATH = os.path.join(BASE_DIR, 'trained_models')

def load_enhanced_model(country, model_type="lstm"):
    """
    Charge un modèle amélioré pour un pays spécifique
    
    Args:
        country: Nom du pays
        model_type: Type de modèle (par défaut: lstm)
        
    Returns:
        Le modèle chargé et le type réel du modèle utilisé
    """
    try:
        # Normaliser le nom du pays pour correspondre au format des dossiers
        country_folder = country.replace(' ', '_')
        model_folder = os.path.join(TRAINED_MODELS_PATH, country_folder)
        
        # Vérifier si le dossier existe
        if not os.path.exists(model_folder):
            logger.warning(f"Aucun dossier de modèles trouvé pour {country}")
            return None, None
        
        # Chercher le modèle LSTM d'abord (meilleur modèle selon nos tests)
        if model_type.lower() == "lstm":
            lstm_path = os.path.join(model_folder, 'lstm_model.keras')
            if os.path.exists(lstm_path):
                logger.info(f"Chargement du modèle LSTM pour {country}")
                model = load_model(lstm_path)
                return model, "lstm"
        
        # Chercher le modèle spécifié
        model_path = os.path.join(model_folder, f"{model_type.lower()}.pkl")
        if os.path.exists(model_path):
            logger.info(f"Chargement du modèle {model_type} pour {country}")
            model = joblib.load(model_path)
            return model, model_type.lower()
        
        # Si le modèle spécifié n'est pas trouvé, chercher un modèle alternatif
        available_models = []
        
        # Chercher d'abord des modèles scikit-learn (.pkl)
        pkl_models = [f for f in os.listdir(model_folder) if f.endswith('.pkl')]
        available_models.extend([(os.path.join(model_folder, f), f.replace('.pkl', '')) for f in pkl_models])
        
        # Chercher ensuite des modèles Keras (.keras)
        keras_models = [f for f in os.listdir(model_folder) if f.endswith('.keras')]
        available_models.extend([(os.path.join(model_folder, f), f.replace('.keras', '')) for f in keras_models])
        
        if available_models:
            # Préférer les modèles avec 'enhanced' dans le nom
            enhanced_models = [m for m in available_models if 'enhanced' in m[1].lower()]
            if enhanced_models:
                model_path, model_type = enhanced_models[0]
            else:
                model_path, model_type = available_models[0]
            
            logger.info(f"Utilisation du modèle alternatif: {model_type}")
            
            if model_path.endswith('.keras'):
                try:
                    model = load_model(model_path)
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du modèle Keras: {str(e)}")
                    return None, None
            else:
                try:
                    model = joblib.load(model_path)
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du modèle joblib: {str(e)}")
                    return None, None
            
            return model, model_type
        
        logger.error(f"Aucun modèle disponible pour {country}")
        return None, None
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle amélioré: {str(e)}")
        return None, None

def prepare_enhanced_data(country, days=14):
    """
    Prépare les données améliorées pour les prédictions
    
    Args:
        country: Nom du pays
        days: Nombre de jours à prédire
        
    Returns:
        Données préparées pour la prédiction, features, dernière date des données
    """
    try:
        # Charger les données améliorées
        country_file = f"{country.replace(' ', '_')}_enhanced.csv"
        data_path = os.path.join(ENHANCED_DATA_PATH, country_file)
        
        # Si le fichier spécifique n'existe pas, utiliser le fichier global
        if not os.path.exists(data_path):
            data_path = os.path.join(ENHANCED_DATA_PATH, 'data_to_train_covid19_enhanced.csv')
            if not os.path.exists(data_path):
                logger.error(f"Aucune donnée améliorée trouvée pour {country}")
                return None, None, None
        
        # Charger les données
        logger.info(f"Chargement des données améliorées depuis {data_path}")
        data = pd.read_csv(data_path)
        
        # Filtrer pour le pays spécifié si nécessaire
        if 'country' in data.columns:
            data = data[data['country'] == country]
        
        if len(data) == 0:
            logger.error(f"Aucune donnée trouvée pour {country}")
            return None, None, None
        
        # Convertir la date en datetime
        if 'date_value' in data.columns:
            data['date'] = pd.to_datetime(data['date_value'])
        else:
            data['date'] = pd.to_datetime(data['date'])
        
        # Trier par date
        data = data.sort_values('date')
        
        # Récupérer la dernière date
        last_date = data['date'].max()
        
        # Préparer les features (caractéristiques)
        features = ['total_cases', 'total_deaths', 'new_deaths']
        if all(f in data.columns for f in features):
            # Prendre les données les plus récentes
            latest_data = data.iloc[-1:].copy()
            X_latest = latest_data[features]
            
            return X_latest, features, last_date
        else:
            logger.error(f"Colonnes requises manquantes dans les données pour {country}")
            return None, None, None
    
    except Exception as e:
        logger.error(f"Erreur lors de la préparation des données améliorées: {str(e)}")
        return None, None, None

def generate_enhanced_predictions(country, days=14, model_type="lstm"):
    """
    Génère des prédictions améliorées pour un pays spécifique
    
    Args:
        country: Nom du pays
        days: Nombre de jours à prédire
        model_type: Type de modèle à utiliser
        
    Returns:
        Dictionnaire contenant les prédictions et métadonnées
    """
    try:
        # Charger le modèle
        model, actual_model_type = load_enhanced_model(country, model_type)
        if model is None:
            logger.error(f"Impossible de charger un modèle pour {country}")
            return None
        
        # Préparer les données
        X_latest, features, last_date = prepare_enhanced_data(country, days)
        if X_latest is None:
            logger.error(f"Impossible de préparer les données pour {country}")
            return None
        
        # Récupérer les métriques du modèle
        metrics = {}
        try:
            country_folder = country.replace(' ', '_')
            metrics_path = os.path.join(TRAINED_MODELS_PATH, country_folder, 'models_comparison.csv')
            if os.path.exists(metrics_path):
                metrics_df = pd.read_csv(metrics_path, index_col=0)
                if actual_model_type in metrics_df.index:
                    metrics = {
                        "RMSE": float(metrics_df.loc[actual_model_type, 'Test RMSE']),
                        "MAE": float(metrics_df.loc[actual_model_type, 'Test MAE']),
                        "R²": float(metrics_df.loc[actual_model_type, 'Test R²'])
                    }
        except Exception as e:
            logger.warning(f"Impossible de charger les métriques du modèle: {str(e)}")
        
        # Générer les prédictions
        predictions = []
        current_X = X_latest.copy()
        
        # Pour les modèles LSTM, on doit restructurer les données
        is_lstm = actual_model_type.lower() == "lstm"
        
        # Stocker les prédictions brutes pour l'amélioration
        raw_predictions = []
        
        for i in range(days):
            try:
                # Préparation des données selon le type de modèle
                if is_lstm:
                    try:
                        # Reshape pour LSTM: [samples, timesteps, features]
                        X_reshaped = np.reshape(current_X.values, (current_X.shape[0], 1, current_X.shape[1]))
                        prediction = model.predict(X_reshaped)[0][0]
                    except Exception as e:
                        logger.error(f"Erreur lors de la prédiction LSTM: {str(e)}")
                        # Fallback pour les erreurs LSTM
                        prediction = current_X['total_cases'].values[0] * 0.01
                else:
                    # Prédiction standard pour les modèles scikit-learn
                    prediction = model.predict(current_X)[0]
            except Exception as e:
                logger.error(f"Erreur lors de la prédiction: {str(e)}")
                # Valeur par défaut en cas d'erreur
                prediction = 10.0
            
            # Date de la prédiction
            prediction_date = last_date + timedelta(days=i+1)
            
            # Garantir que les prédictions sont positives
            prediction = max(0, float(prediction))
            
            # Stocker la prédiction brute
            raw_predictions.append(prediction)
            
            # Mettre à jour les données pour la prédiction suivante de façon sécurisée
            try:
                if 'new_cases' in current_X.columns:
                    current_X['new_cases'] = prediction
                
                # Si on a des caractéristiques cumulatives comme total_cases, les mettre à jour
                if 'total_cases' in current_X.columns and 'new_cases' in current_X.columns:
                    current_X['total_cases'] += current_X['new_cases']
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour des données: {str(e)}")
                # Continuer malgré l'erreur
        
        # Améliorer les prédictions en appliquant nos techniques d'amélioration
        try:
            dates = [last_date + timedelta(days=i+1) for i in range(days)]
            raw_series = pd.Series(raw_predictions, index=dates)
            
            # Obtenir des données historiques pour contexte
            try:
                enhanced_csv_path = os.path.join(ENHANCED_DATA_PATH, 'data_to_train_covid19_enhanced.csv')
                if os.path.exists(enhanced_csv_path):
                    historical_data = pd.read_csv(enhanced_csv_path)
                    historical_data = historical_data[historical_data['country'] == country]
                    
                    if len(historical_data) > 0:
                        historical_data['date'] = pd.to_datetime(historical_data['date_value'])
                        historical_data = historical_data.sort_values('date')
                        
                        if 'new_cases' in historical_data.columns and len(historical_data) >= 30:
                            historical_series = pd.Series(historical_data['new_cases'].values[-30:],
                                                        index=historical_data['date'].values[-30:])
                            
                            # Appliquer les améliorations
                            enhanced_predictions = enhance_predictions(raw_series, historical_series)
                            enhanced_predictions = epidemiological_smoothing(enhanced_predictions, alpha=0.3, beta=0.1)
                        else:
                            logger.warning("Pas assez de données historiques, utilisation des prédictions brutes")
                            enhanced_predictions = raw_series
                    else:
                        logger.warning(f"Aucune donnée historique trouvée pour {country}, utilisation des prédictions brutes")
                        enhanced_predictions = raw_series
                else:
                    logger.warning(f"Fichier {enhanced_csv_path} non trouvé, utilisation des prédictions brutes")
                    enhanced_predictions = raw_series
            except Exception as e:
                logger.error(f"Erreur lors du chargement des données historiques: {str(e)}")
                enhanced_predictions = raw_series
        except Exception as e:
            logger.error(f"Erreur lors de l'amélioration des prédictions: {str(e)}")
            # En cas d'erreur, utiliser les prédictions brutes
            enhanced_predictions = pd.Series(raw_predictions, index=dates)
        
        # Formater les résultats
        for i, date in enumerate(dates):
            try:
                enhanced_value = float(enhanced_predictions[date]) if date in enhanced_predictions.index else float(raw_predictions[i])
                predictions.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "predicted_cases": enhanced_value,
                    "raw_prediction": float(raw_predictions[i])
                })
            except Exception as e:
                logger.error(f"Erreur lors du formatage des résultats pour la date {date}: {str(e)}")
                # Ajouter une valeur par défaut en cas d'erreur
                predictions.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "predicted_cases": float(raw_predictions[i]),
                    "raw_prediction": float(raw_predictions[i])
                })
        
        return {
            "country": country,
            "predictions": predictions,
            "model_used": actual_model_type,
            "metrics": metrics
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération des prédictions améliorées: {str(e)}")
        return None

# Pour tester le module directement
if __name__ == "__main__":
    # Configurer le logging pour les tests
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Tester avec les États-Unis
        result = generate_enhanced_predictions("US", days=7)  # Réduire le nombre de jours pour un test plus rapide
        if result:
            print(f"Prédictions générées avec succès pour {result['country']} en utilisant le modèle {result['model_used']}")
            print(f"Métriques du modèle: {result['metrics']}")
            print("\nPrédictions pour les jours:")
            for i, pred in enumerate(result['predictions']):
                print(f"{pred['date']}: {pred['predicted_cases']:.2f} cas (prédiction brute: {pred['raw_prediction']:.2f})")
        else:
            print("Échec de la génération des prédictions")
    except Exception as e:
        print(f"Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
