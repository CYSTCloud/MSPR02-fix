"""
EPIVIZ 4.1 - Entraînement et évaluation des modèles
---------------------------------------------------
Ce script entraîne différents modèles de machine learning pour la prédiction
des cas de COVID-19 et compare leurs performances.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

# Importer le module d'amélioration des données
import data_enhancement

# Modèles
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Évaluation
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from math import sqrt

# Configuration pour les graphiques
plt.style.use('seaborn-v0_8-whitegrid')
sns.set(font_scale=1.2)
plt.rcParams['figure.figsize'] = (14, 8)

# Chemins des fichiers
# Utiliser les données améliorées au lieu des données originales
INPUT_PATH = os.path.join(os.getcwd(), 'enhanced_data')
OUTPUT_PATH = os.path.join(os.getcwd(), 'trained_models')

# Chemin vers le fichier CSV amélioré
ENHANCED_CSV = os.path.join(os.getcwd(), 'enhanced_data', 'data_to_train_covid19_enhanced.csv')

# Création du dossier de sortie s'il n'existe pas
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def load_country_data(country, enhance_data=True):
    """Charge les données d'entraînement et de test pour un pays spécifique"""
    print(f"\nChargement des données pour {country}...")
    
    country_folder = os.path.join(INPUT_PATH, country.replace(' ', '_'))
    data_path = os.path.join(country_folder, 'train_test_data.pkl')
    
    try:
        data = joblib.load(data_path)
        print(f"Données chargées avec succès. Ensemble d'entraînement: {data['X_train'].shape}, Ensemble de test: {data['X_test'].shape}")
        
        # Améliorer les données si demandé
        if enhance_data:
            print("\nAmélioration des données d'entraînement et de test...")
            data = data_enhancement.enhance_training_data(data)
            print("Amélioration des données terminée avec succès!")
            
            # Sauvegarder les données améliorées
            enhanced_data_path = os.path.join(country_folder, 'enhanced_train_test_data.pkl')
            joblib.dump(data, enhanced_data_path)
            print(f"Données améliorées sauvegardées dans {enhanced_data_path}")
        
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des données: {str(e)}")
        return None

def train_linear_models(data, country):
    """Entraîne et évalue les modèles linéaires (Régression linéaire, Ridge, Lasso)"""
    print("\n=== ENTRAÎNEMENT DES MODÈLES LINÉAIRES ===")
    
    # Initialisation des modèles
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=0.1)
    }
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\nEntraînement du modèle {model_name}...")
        
        # Entraînement
        start_time = time.time()
        model.fit(data['X_train'], data['y_cases_train'])
        training_time = time.time() - start_time
        
        # Prédictions
        y_train_pred = model.predict(data['X_train'])
        y_test_pred = model.predict(data['X_test'])
        
        # Évaluation
        train_rmse = sqrt(mean_squared_error(data['y_cases_train'], y_train_pred))
        test_rmse = sqrt(mean_squared_error(data['y_cases_test'], y_test_pred))
        train_mae = mean_absolute_error(data['y_cases_train'], y_train_pred)
        test_mae = mean_absolute_error(data['y_cases_test'], y_test_pred)
        train_r2 = r2_score(data['y_cases_train'], y_train_pred)
        test_r2 = r2_score(data['y_cases_test'], y_test_pred)
        
        print(f"  Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}")
        print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        print(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        print(f"  Temps d'entraînement: {training_time:.2f} secondes")
        
        # Sauvegarde du modèle
        model_folder = os.path.join(OUTPUT_PATH, country.replace(' ', '_'))
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        
        model_path = os.path.join(model_folder, f"{model_name.replace(' ', '_').lower()}.pkl")
        joblib.dump(model, model_path)
        print(f"  Modèle sauvegardé dans {model_path}")
        
        # Stockage des résultats
        results[model_name] = {
            'model': model,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'training_time': training_time,
            'predictions': {
                'train': y_train_pred,
                'test': y_test_pred
            }
        }
    
    return results

def train_ensemble_models(data, country):
    """Entraîne et évalue les modèles d'ensemble (Random Forest, Gradient Boosting, XGBoost)"""
    print("\n=== ENTRAÎNEMENT DES MODÈLES D'ENSEMBLE ===")
    
    # Initialisation des modèles
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\nEntraînement du modèle {model_name}...")
        
        # Entraînement
        start_time = time.time()
        model.fit(data['X_train'], data['y_cases_train'])
        training_time = time.time() - start_time
        
        # Prédictions
        y_train_pred = model.predict(data['X_train'])
        y_test_pred = model.predict(data['X_test'])
        
        # Évaluation
        train_rmse = sqrt(mean_squared_error(data['y_cases_train'], y_train_pred))
        test_rmse = sqrt(mean_squared_error(data['y_cases_test'], y_test_pred))
        train_mae = mean_absolute_error(data['y_cases_train'], y_train_pred)
        test_mae = mean_absolute_error(data['y_cases_test'], y_test_pred)
        train_r2 = r2_score(data['y_cases_train'], y_train_pred)
        test_r2 = r2_score(data['y_cases_test'], y_test_pred)
        
        print(f"  Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}")
        print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        print(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        print(f"  Temps d'entraînement: {training_time:.2f} secondes")
        
        # Importance des caractéristiques (si disponible)
        if hasattr(model, 'feature_importances_'):
            feature_imp = pd.Series(model.feature_importances_, index=data['feature_names']).sort_values(ascending=False)
            print("\n  Importance des 10 principales caractéristiques:")
            print(feature_imp.head(10))
            
            # Visualisation de l'importance des caractéristiques
            plt.figure(figsize=(12, 8))
            feature_imp.head(15).plot(kind='barh')
            plt.title(f'Importance des caractéristiques - {model_name}')
            plt.xlabel('Importance')
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), f"{model_name.replace(' ', '_').lower()}_feature_importance.png"))
            plt.close()
        
        # Sauvegarde du modèle
        model_folder = os.path.join(OUTPUT_PATH, country.replace(' ', '_'))
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        
        model_path = os.path.join(model_folder, f"{model_name.replace(' ', '_').lower()}.pkl")
        joblib.dump(model, model_path)
        print(f"  Modèle sauvegardé dans {model_path}")
        
        # Stockage des résultats
        results[model_name] = {
            'model': model,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'training_time': training_time,
            'predictions': {
                'train': y_train_pred,
                'test': y_test_pred
            }
        }
    
    return results

def prepare_lstm_data(data):
    """Prépare les données pour l'entraînement d'un modèle LSTM"""
    # Reshape des données pour LSTM [samples, time steps, features]
    X_train = np.reshape(data['X_train'].values, (data['X_train'].shape[0], 1, data['X_train'].shape[1]))
    X_test = np.reshape(data['X_test'].values, (data['X_test'].shape[0], 1, data['X_test'].shape[1]))
    
    return X_train, X_test

def train_lstm_model(data, country):
    """Entraîne et évalue un modèle LSTM pour les séries temporelles"""
    print("\n=== ENTRAÎNEMENT DU MODÈLE LSTM ===")
    
    # Préparation des données
    X_train, X_test = prepare_lstm_data(data)
    
    # Nombre de caractéristiques
    n_features = data['X_train'].shape[1]
    
    # Construction du modèle LSTM
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(1, n_features), return_sequences=True),
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    
    # Compilation du modèle
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    
    # Early stopping pour éviter le surapprentissage
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    print("Entraînement du modèle LSTM...")
    
    # Entraînement
    start_time = time.time()
    history = model.fit(
        X_train, data['y_cases_train'],
        epochs=100,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop],
        verbose=0
    )
    training_time = time.time() - start_time
    
    # Prédictions
    y_train_pred = model.predict(X_train).flatten()
    y_test_pred = model.predict(X_test).flatten()
    
    # Évaluation
    train_rmse = sqrt(mean_squared_error(data['y_cases_train'], y_train_pred))
    test_rmse = sqrt(mean_squared_error(data['y_cases_test'], y_test_pred))
    train_mae = mean_absolute_error(data['y_cases_train'], y_train_pred)
    test_mae = mean_absolute_error(data['y_cases_test'], y_test_pred)
    train_r2 = r2_score(data['y_cases_train'], y_train_pred)
    test_r2 = r2_score(data['y_cases_test'], y_test_pred)
    
    print(f"  Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}")
    print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
    print(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
    print(f"  Temps d'entraînement: {training_time:.2f} secondes")
    
    # Visualisation de la courbe d'apprentissage
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Courbe d\'apprentissage - LSTM')
    plt.xlabel('Epochs')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'lstm_learning_curve.png'))
    plt.close()
    
    # Sauvegarde du modèle
    model_folder = os.path.join(OUTPUT_PATH, country.replace(' ', '_'))
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)
    
    model_path = os.path.join(model_folder, 'lstm_model.keras')
    model.save(model_path)
    print(f"  Modèle sauvegardé dans {model_path}")
    
    # Sauvegarde du scaler
    scaler_path = os.path.join(model_folder, 'lstm_scaler.pkl')
    # Pour les nouveaux entraînements, il faudrait enregistrer le scaler ici
    
    # Stockage des résultats
    results = {
        'LSTM': {
            'model': model,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'training_time': training_time,
            'predictions': {
                'train': y_train_pred,
                'test': y_test_pred
            },
            'history': history.history
        }
    }
    
    return results

def compare_models(linear_results, ensemble_results, lstm_results):
    """Compare les performances des différents modèles"""
    print("\n=== COMPARAISON DES MODÈLES ===")
    
    # Fusionner les résultats
    all_results = {}
    all_results.update(linear_results)
    all_results.update(ensemble_results)
    all_results.update(lstm_results)
    
    # Créer un DataFrame pour la comparaison
    comparison = pd.DataFrame({
        'Train RMSE': [results['train_rmse'] for model, results in all_results.items()],
        'Test RMSE': [results['test_rmse'] for model, results in all_results.items()],
        'Train MAE': [results['train_mae'] for model, results in all_results.items()],
        'Test MAE': [results['test_mae'] for model, results in all_results.items()],
        'Train R²': [results['train_r2'] for model, results in all_results.items()],
        'Test R²': [results['test_r2'] for model, results in all_results.items()],
        'Training Time (s)': [results['training_time'] for model, results in all_results.items()]
    }, index=all_results.keys())
    
    print("\nComparaison des performances des modèles:")
    print(comparison)
    
    # Identifier le meilleur modèle selon différents critères
    best_rmse_model = comparison.loc[comparison['Test RMSE'].idxmin()]
    best_mae_model = comparison.loc[comparison['Test MAE'].idxmin()]
    best_r2_model = comparison.loc[comparison['Test R²'].idxmax()]
    
    print("\nMeilleur modèle selon RMSE:")
    print(f"  {comparison['Test RMSE'].idxmin()} - Test RMSE: {best_rmse_model['Test RMSE']:.2f}")
    
    print("\nMeilleur modèle selon MAE:")
    print(f"  {comparison['Test MAE'].idxmin()} - Test MAE: {best_mae_model['Test MAE']:.2f}")
    
    print("\nMeilleur modèle selon R²:")
    print(f"  {comparison['Test R²'].idxmax()} - Test R²: {best_r2_model['Test R²']:.4f}")
    
    return comparison

def visualize_predictions(data, linear_results, ensemble_results, lstm_results, country, enhance_predictions=True):
    """Visualise les prédictions des meilleurs modèles sur l'ensemble de test"""
    print("\n=== VISUALISATION DES PRÉDICTIONS ===")
    
    # Sélectionner les meilleurs modèles de chaque catégorie
    best_linear = min(linear_results.items(), key=lambda x: x[1]['test_rmse'])
    best_ensemble = min(ensemble_results.items(), key=lambda x: x[1]['test_rmse'])
    best_lstm = list(lstm_results.items())[0]  # Il n'y a qu'un seul modèle LSTM
    
    best_models = {
        f"Meilleur modèle linéaire ({best_linear[0]})": best_linear[1],
        f"Meilleur modèle d'ensemble ({best_ensemble[0]})": best_ensemble[1],
        "LSTM": best_lstm[1]
    }
    
    # Dates de test
    test_dates = data['test_dates']
    
    # Créer un dictionnaire pour stocker toutes les prédictions
    all_predictions = {}
    
    # Ajouter les prédictions originales
    for model_name, results in best_models.items():
        all_predictions[model_name] = results['predictions']['test']
    
    # Améliorer les prédictions si demandé
    if enhance_predictions:
        print("\nAmélioration des prédictions...")
        
        # Convertir les données de test en série temporelle pour l'amélioration
        historical_series = pd.Series(data['y_cases_test'], index=test_dates)
        
        # Améliorer les prédictions de chaque modèle
        # Créer une copie des clés pour éviter l'erreur de modification pendant l'itération
        model_names = list(all_predictions.keys())
        
        # Créer un dictionnaire pour stocker les prédictions améliorées
        enhanced_predictions = {}
        
        for model_name in model_names:
            preds = all_predictions[model_name]
            print(f"  Amélioration des prédictions du modèle {model_name}...")
            pred_series = pd.Series(preds, index=test_dates)
            enhanced_preds = data_enhancement.enhance_predictions(pred_series, historical_series)
            enhanced_predictions[f"{model_name} (amélioré)"] = enhanced_preds.values
        
        # Ajouter les prédictions améliorées au dictionnaire original
        all_predictions.update(enhanced_predictions)
    
    # Sauvegarder toutes les prédictions
    predictions_path = os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'predictions.pkl')
    joblib.dump(all_predictions, predictions_path)
    print(f"Prédictions sauvegardées dans {predictions_path}")
    
    # Visualiser les prédictions originales
    plt.figure(figsize=(16, 10))
    
    # Valeurs réelles
    plt.plot(test_dates, data['y_cases_test'], 'o-', label='Valeurs réelles', alpha=0.7)
    
    # Prédictions des meilleurs modèles (originales uniquement)
    for model_name, results in best_models.items():
        plt.plot(test_dates, results['predictions']['test'], 'o-', label=f"{model_name} (RMSE: {results['test_rmse']:.2f})", alpha=0.7)
    
    plt.title(f'Comparaison des prédictions originales - {country}')
    plt.xlabel('Date')
    plt.ylabel('Nouveaux cas')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'predictions_comparison.png'))
    plt.close()
    
    print(f"Visualisation des prédictions originales sauvegardée dans {os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'predictions_comparison.png')}")
    
    # Si les prédictions ont été améliorées, les visualiser également
    if enhance_predictions:
        plt.figure(figsize=(16, 10))
        
        # Valeurs réelles
        plt.plot(test_dates, data['y_cases_test'], 'o-', label='Valeurs réelles', alpha=0.7)
        
        # Prédictions améliorées uniquement
        for model_name, preds in all_predictions.items():
            if "amélioré" in model_name:
                plt.plot(test_dates, preds, 'o-', label=model_name, alpha=0.7)
        
        plt.title(f'Comparaison des prédictions améliorées - {country}')
        plt.xlabel('Date')
        plt.ylabel('Nouveaux cas')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'enhanced_predictions_comparison.png'))
        plt.close()
        
        print(f"Visualisation des prédictions améliorées sauvegardée dans {os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'enhanced_predictions_comparison.png')}")
        
        # Visualisation comparative originales vs améliorées pour le meilleur modèle
        plt.figure(figsize=(16, 10))
        
        # Valeurs réelles
        plt.plot(test_dates, data['y_cases_test'], 'o-', label='Valeurs réelles', alpha=0.7)
        
        # Meilleur modèle global (selon RMSE)
        best_model_name = min([m for m in best_models.keys()], key=lambda x: best_models[x]['test_rmse'])
        plt.plot(test_dates, all_predictions[best_model_name], 'o-', label=f"{best_model_name} (original)", alpha=0.7)
        plt.plot(test_dates, all_predictions[f"{best_model_name} (amélioré)"], 'o-', label=f"{best_model_name} (amélioré)", alpha=0.7)
        
        plt.title(f'Impact de l\'amélioration sur les prédictions - {country}')
        plt.xlabel('Date')
        plt.ylabel('Nouveaux cas')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'original_vs_enhanced_predictions.png'))
        plt.close()
        
        print(f"Visualisation comparative sauvegardée dans {os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'original_vs_enhanced_predictions.png')}")
    
    # Sauvegarder la comparaison des modèles
    comparison_path = os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'models_comparison.csv')
    
    # Fusionner les résultats
    all_results = {}
    all_results.update(linear_results)
    all_results.update(ensemble_results)
    all_results.update(lstm_results)
    
    # Créer un DataFrame pour la comparaison
    comparison = pd.DataFrame({
        'Train RMSE': [results['train_rmse'] for model, results in all_results.items()],
        'Test RMSE': [results['test_rmse'] for model, results in all_results.items()],
        'Train MAE': [results['train_mae'] for model, results in all_results.items()],
        'Test MAE': [results['test_mae'] for model, results in all_results.items()],
        'Train R²': [results['train_r2'] for model, results in all_results.items()],
        'Test R²': [results['test_r2'] for model, results in all_results.items()],
        'Training Time (s)': [results['training_time'] for model, results in all_results.items()]
    }, index=all_results.keys())
    
    comparison.to_csv(comparison_path)
    print(f"Comparaison des modèles sauvegardée dans {comparison_path}")

def prepare_data_from_csv(csv_file, countries=None):
    """Prépare les données d'entraînement à partir du fichier CSV amélioré"""
    print(f"\nPréparation des données à partir de {csv_file}...")
    
    try:
        # Charger le fichier CSV
        data = pd.read_csv(csv_file)
        print(f"Fichier CSV chargé avec succès. {len(data)} entrées.")
        
        # Si aucun pays spécifié, utiliser tous les pays disponibles
        if countries is None:
            countries = data['country'].unique().tolist()
            print(f"Aucun pays spécifié, utilisation de tous les pays disponibles ({len(countries)}).")
        else:
            # Filtrer pour ne garder que les pays disponibles dans le CSV
            available_countries = data['country'].unique().tolist()
            countries = [c for c in countries if c in available_countries]
            print(f"Pays disponibles filtrés : {len(countries)}.")
        
        return data, countries
        
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV: {str(e)}")
        return None, None

def main(enhance_data=True, enhance_predictions=True, use_enhanced_csv=True):
    print("Démarrage de l'entraînement des modèles...")
    print(f"Amélioration des données: {'Activée' if enhance_data else 'Désactivée'}")
    print(f"Amélioration des prédictions: {'Activée' if enhance_predictions else 'Désactivée'}")
    print(f"Utilisation du CSV amélioré: {'Activée' if use_enhanced_csv else 'Désactivée'}")
    
    # Vérifier si nous utilisons le CSV amélioré
    if use_enhanced_csv:
        if not os.path.exists(ENHANCED_CSV):
            print(f"ERREUR: Le fichier {ENHANCED_CSV} n'existe pas!")
            print("Exécutez d'abord enhance_source_data.py pour générer les données améliorées.")
            return
            
        # Préparer les données à partir du CSV amélioré
        csv_data, countries = prepare_data_from_csv(ENHANCED_CSV)
        if csv_data is None:
            return
    else:
        # Méthode originale: vérifier que le dossier d'entrée existe
        if not os.path.exists(INPUT_PATH):
            print(f"ERREUR: Le dossier {INPUT_PATH} n'existe pas!")
            return
        
        # Charger la liste des pays traités
        countries_file = os.path.join(INPUT_PATH, 'processed_countries.txt')
        
        if os.path.exists(countries_file):
            with open(countries_file, 'r') as f:
                countries = [line.strip() for line in f.readlines()]
        else:
            print(f"ERREUR: Le fichier {countries_file} n'existe pas!")
            # Fallback sur les dossiers présents
            countries = [d for d in os.listdir(INPUT_PATH) if os.path.isdir(os.path.join(INPUT_PATH, d))]
            countries = [c.replace('_', ' ') for c in countries]
    
    print(f"Pays à traiter: {', '.join(countries)}")
    
    # Pour chaque pays
    for country in countries:
        print(f"\n{'='*50}")
        print(f"TRAITEMENT DE {country.upper()}")
        print(f"{'='*50}")
        
        if use_enhanced_csv and 'csv_data' in locals():
            # Préparer les données directement à partir du CSV amélioré
            print(f"Préparation des données pour {country} à partir du CSV amélioré...")
            
            # Filtrer les données pour ce pays
            country_data = csv_data[csv_data['country'] == country].copy()
            
            if len(country_data) == 0:
                print(f"Aucune donnée trouvée pour {country} dans le CSV amélioré.")
                continue
                
            # Convertir les dates en datetime
            country_data['date'] = pd.to_datetime(country_data['date_value'])
            
            # Trier par date
            country_data = country_data.sort_values('date')
            
            # Diviser en ensembles d'entraînement et de test (80% / 20%)
            train_size = int(len(country_data) * 0.8)
            train_data = country_data.iloc[:train_size]
            test_data = country_data.iloc[train_size:]
            
            # Préparer les features et les cibles
            features = ['total_cases', 'total_deaths', 'new_deaths']
            X_train = train_data[features]
            y_cases_train = train_data['new_cases']
            
            X_test = test_data[features]
            y_cases_test = test_data['new_cases']
            
            # Créer un dictionnaire avec toutes les données nécessaires
            data = {
                'X_train': X_train,
                'y_cases_train': y_cases_train,
                'X_test': X_test,
                'y_cases_test': y_cases_test,
                'train_dates': train_data['date'].values,
                'test_dates': test_data['date'].values,
                'feature_names': features
            }
            
            print(f"Données préparées avec succès. Ensemble d'entraînement: {X_train.shape}, Ensemble de test: {X_test.shape}")
        else:
            # Méthode originale: charger les données depuis les fichiers
            data = load_country_data(country, enhance_data=enhance_data)
            if data is None:
                continue
        
        # Entraîner les modèles linéaires
        linear_results = train_linear_models(data, country)
        
        # Entraîner les modèles d'ensemble
        ensemble_results = train_ensemble_models(data, country)
        
        # Entraîner le modèle LSTM
        lstm_results = train_lstm_model(data, country)
        
        # Comparer les modèles
        comparison = compare_models(linear_results, ensemble_results, lstm_results)
        
        # Visualiser les prédictions avec option d'amélioration
        visualize_predictions(data, linear_results, ensemble_results, lstm_results, country, enhance_predictions=enhance_predictions)
        
        print(f"\nTraitement de {country} terminé avec succès!")
    
    print("\nEntraînement des modèles terminé avec succès!")
    print("\nLes données et prédictions améliorées sont prêtes à être utilisées dans le frontend!")
    
    # Créer un fichier de log pour indiquer que les améliorations ont été appliquées
    if enhance_data or enhance_predictions:
        log_path = os.path.join(OUTPUT_PATH, 'enhancements_applied.txt')
        with open(log_path, 'w') as f:
            f.write(f"Améliorations appliquées le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Amélioration des données: {'Oui' if enhance_data else 'Non'}\n")
            f.write(f"Amélioration des prédictions: {'Oui' if enhance_predictions else 'Non'}\n")
        print(f"Log des améliorations sauvegardé dans {log_path}")
        
        # Créer un résumé des améliorations pour chaque pays
        enhancement_summary = {}
        for country in countries:
            country_folder = os.path.join(OUTPUT_PATH, country.replace(' ', '_'))
            if os.path.exists(os.path.join(country_folder, 'original_vs_enhanced_predictions.png')):
                enhancement_summary[country] = {
                    'enhanced_data': enhance_data,
                    'enhanced_predictions': enhance_predictions,
                    'visual_comparison': os.path.join(country_folder, 'original_vs_enhanced_predictions.png')
                }
        
        # Sauvegarder le résumé des améliorations
        summary_path = os.path.join(OUTPUT_PATH, 'enhancement_summary.pkl')
        joblib.dump(enhancement_summary, summary_path)
        print(f"Résumé des améliorations sauvegardé dans {summary_path}")

# Par défaut, utiliser le CSV amélioré et activer les améliorations lors de l'exécution directe du script
if __name__ == "__main__":
    main(enhance_data=True, enhance_predictions=True, use_enhanced_csv=True)
