"""
EPIVIZ 4.1 - Feature Engineering et préparation des jeux de données
------------------------------------------------------------------
Ce script réalise le feature engineering et la préparation des jeux de données
pour l'entraînement des modèles prédictifs par pays.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib

# Configuration pour améliorer la lisibilité des graphiques
plt.style.use('seaborn-v0_8-whitegrid')
sns.set(font_scale=1.2)
plt.rcParams['figure.figsize'] = (14, 8)

# Chemins des fichiers
INPUT_PATH = os.path.join(os.getcwd(), 'processed_data', 'prepared_covid_data.csv')
OUTPUT_PATH = os.path.join(os.getcwd(), 'model_data')

# Création du dossier de sortie s'il n'existe pas
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def load_prepared_data(filepath):
    """Charge les données préparées depuis un fichier CSV"""
    print(f"Chargement des données préparées depuis {filepath}...")
    try:
        df = pd.read_csv(filepath)
        df['date_value'] = pd.to_datetime(df['date_value'])
        print(f"Données chargées avec succès. Dimensions: {df.shape}")
        return df
    except Exception as e:
        print(f"Erreur lors du chargement des données: {str(e)}")
        return None

def create_time_features(df):
    """Crée des caractéristiques temporelles avancées"""
    print("\n=== CRÉATION DES CARACTÉRISTIQUES TEMPORELLES ===")
    
    # Vérifier si les caractéristiques de base existent déjà
    time_features = ['day', 'month', 'year', 'day_of_week']
    missing_features = [feat for feat in time_features if feat not in df.columns]
    
    if missing_features:
        print(f"Création des caractéristiques temporelles manquantes: {', '.join(missing_features)}")
        if 'day' in missing_features:
            df['day'] = df['date_value'].dt.day
        if 'month' in missing_features:
            df['month'] = df['date_value'].dt.month
        if 'year' in missing_features:
            df['year'] = df['date_value'].dt.year
        if 'day_of_week' in missing_features:
            df['day_of_week'] = df['date_value'].dt.dayofweek
    
    # Création de caractéristiques temporelles avancées
    print("Création de caractéristiques temporelles avancées...")
    
    # Jour de l'année (1-366)
    df['day_of_year'] = df['date_value'].dt.dayofyear
    
    # Semaine de l'année (1-53)
    df['week_of_year'] = df['date_value'].dt.isocalendar().week
    
    # Trimestre (1-4)
    df['quarter'] = df['date_value'].dt.quarter
    
    # Est-ce un jour de week-end? (0=Non, 1=Oui)
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Créer des variables cycliques pour les caractéristiques périodiques
    # Cela permet de mieux capturer la nature cyclique du temps
    print("Création de variables cycliques pour les caractéristiques périodiques...")
    
    # Jour du mois (transformé en coordonnées circulaires)
    df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
    df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
    
    # Mois de l'année
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Jour de la semaine
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    print(f"Caractéristiques temporelles créées: {', '.join([col for col in df.columns if col not in ['date_value', 'country', 'total_cases', 'total_deaths', 'new_cases', 'new_deaths', 'id_pandemic']])}")
    
    return df

def create_lag_features(df, lag_days=[1, 3, 7, 14], target_cols=['new_cases', 'new_deaths']):
    """Crée des caractéristiques de décalage (lag features) pour chaque pays"""
    print("\n=== CRÉATION DES CARACTÉRISTIQUES DE DÉCALAGE ===")
    
    all_countries = df['country'].unique()
    print(f"Création de caractéristiques de décalage pour {len(all_countries)} pays...")
    
    for target_col in target_cols:
        for lag in lag_days:
            col_name = f'{target_col}_lag_{lag}'
            print(f"  - Création de {col_name}")
            df[col_name] = np.nan
            
            for country in all_countries:
                country_mask = df['country'] == country
                df.loc[country_mask, col_name] = df.loc[country_mask, target_col].shift(lag)
    
    # Remplir les valeurs NaN créées par le décalage avec 0
    for col in df.columns:
        if '_lag_' in col:
            df[col] = df[col].fillna(0)
    
    return df

def create_rolling_features(df, windows=[3, 7, 14], target_cols=['new_cases', 'new_deaths']):
    """Crée des caractéristiques de moyenne mobile (rolling features) pour chaque pays"""
    print("\n=== CRÉATION DES CARACTÉRISTIQUES DE MOYENNE MOBILE ===")
    
    all_countries = df['country'].unique()
    print(f"Création de caractéristiques de moyenne mobile pour {len(all_countries)} pays...")
    
    for target_col in target_cols:
        for window in windows:
            # Moyenne mobile
            mean_col_name = f'{target_col}_rolling_mean_{window}'
            print(f"  - Création de {mean_col_name}")
            df[mean_col_name] = np.nan
            
            # Écart-type mobile
            std_col_name = f'{target_col}_rolling_std_{window}'
            print(f"  - Création de {std_col_name}")
            df[std_col_name] = np.nan
            
            for country in all_countries:
                country_mask = df['country'] == country
                country_data = df.loc[country_mask, [target_col]].copy()
                
                # Calculer la moyenne mobile
                rolling_mean = country_data[target_col].rolling(window=window, min_periods=1).mean()
                df.loc[country_mask, mean_col_name] = rolling_mean
                
                # Calculer l'écart-type mobile
                rolling_std = country_data[target_col].rolling(window=window, min_periods=1).std()
                df.loc[country_mask, std_col_name] = rolling_std.fillna(0)  # Remplacer NaN par 0
    
    return df

def create_growth_rate_features(df, target_cols=['new_cases', 'new_deaths']):
    """Crée des caractéristiques de taux de croissance pour chaque pays"""
    print("\n=== CRÉATION DES CARACTÉRISTIQUES DE TAUX DE CROISSANCE ===")
    
    all_countries = df['country'].unique()
    print(f"Création des taux de croissance pour {len(all_countries)} pays...")
    
    for target_col in target_cols:
        growth_col_name = f'{target_col}_growth_rate'
        print(f"  - Création de {growth_col_name}")
        df[growth_col_name] = np.nan
        
        for country in all_countries:
            country_mask = df['country'] == country
            df_country = df.loc[country_mask].copy().sort_values('date_value')
            
            # Calculer le taux de croissance
            previous_values = df_country[target_col].shift(1)
            
            # Éviter division par zéro
            mask = (previous_values != 0) & (~previous_values.isna())
            growth_rates = np.zeros(len(df_country))
            
            if mask.any():
                growth_rates[mask] = (df_country[target_col][mask] - previous_values[mask]) / previous_values[mask]
            
            df.loc[country_mask, growth_col_name] = growth_rates
    
    # Remplacer les valeurs infinies et NaN
    for col in df.columns:
        if '_growth_rate' in col:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].fillna(0)
    
    return df

def normalize_features(df, exclude_cols=['date_value', 'country', 'id_pandemic']):
    """Normalise les caractéristiques numériques entre 0 et 1"""
    print("\n=== NORMALISATION DES CARACTÉRISTIQUES ===")
    
    # Colonnes à normaliser
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    cols_to_normalize = [col for col in numeric_cols if col not in exclude_cols]
    
    print(f"Normalisation de {len(cols_to_normalize)} caractéristiques...")
    
    # Créer et ajuster le scaler
    scaler = MinMaxScaler()
    df[cols_to_normalize] = scaler.fit_transform(df[cols_to_normalize])
    
    # Sauvegarder le scaler pour une utilisation ultérieure
    scaler_path = os.path.join(OUTPUT_PATH, 'feature_scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"Scaler sauvegardé dans {scaler_path}")
    
    return df, cols_to_normalize

def prepare_datasets_by_country(df, top_countries=10, forecast_horizon=14, test_size=0.2):
    """Prépare les jeux de données d'entraînement et de test pour les pays les plus touchés"""
    print(f"\n=== PRÉPARATION DES JEUX DE DONNÉES PAR PAYS (HORIZON DE PRÉVISION: {forecast_horizon} JOURS) ===")
    
    # Identifier les pays les plus touchés
    top_countries_by_cases = df.groupby('country')['total_cases'].max().sort_values(ascending=False).head(top_countries).index.tolist()
    print(f"Préparation des jeux de données pour les {len(top_countries_by_cases)} pays les plus touchés:")
    print(', '.join(top_countries_by_cases))
    
    datasets = {}
    feature_cols = [col for col in df.columns if col not in ['date_value', 'country', 'id_pandemic', 'total_cases', 'total_deaths', 'new_cases', 'new_deaths']]
    
    for country in top_countries_by_cases:
        print(f"\nPréparation des données pour {country}...")
        
        # Filtrer les données pour le pays
        country_data = df[df['country'] == country].sort_values('date_value').copy()
        
        # Créer la variable cible (cas dans les prochains jours)
        country_data['target_cases'] = country_data['new_cases'].shift(-forecast_horizon)
        country_data['target_deaths'] = country_data['new_deaths'].shift(-forecast_horizon)
        
        # Supprimer les lignes avec des valeurs cibles manquantes
        country_data = country_data.dropna(subset=['target_cases', 'target_deaths'])
        
        if len(country_data) == 0:
            print(f"  Avertissement: Pas assez de données pour {country}. Ignoré.")
            continue
        
        # Diviser en caractéristiques et cibles
        X = country_data[feature_cols]
        y_cases = country_data['target_cases']
        y_deaths = country_data['target_deaths']
        
        # Diviser en ensembles d'entraînement et de test (basé sur le temps)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_cases_train = y_cases.iloc[:split_idx]
        y_cases_test = y_cases.iloc[split_idx:]
        y_deaths_train = y_deaths.iloc[:split_idx]
        y_deaths_test = y_deaths.iloc[split_idx:]
        
        # Dates correspondantes pour référence
        train_dates = country_data['date_value'].iloc[:split_idx]
        test_dates = country_data['date_value'].iloc[split_idx:]
        
        print(f"  Ensemble d'entraînement: {len(X_train)} échantillons ({train_dates.min().date()} à {train_dates.max().date()})")
        print(f"  Ensemble de test: {len(X_test)} échantillons ({test_dates.min().date()} à {test_dates.max().date()})")
        
        # Stocker les jeux de données
        datasets[country] = {
            'X_train': X_train,
            'X_test': X_test,
            'y_cases_train': y_cases_train,
            'y_cases_test': y_cases_test,
            'y_deaths_train': y_deaths_train,
            'y_deaths_test': y_deaths_test,
            'train_dates': train_dates,
            'test_dates': test_dates,
            'feature_names': feature_cols
        }
        
        # Sauvegarder les jeux de données
        country_folder = os.path.join(OUTPUT_PATH, country.replace(' ', '_'))
        if not os.path.exists(country_folder):
            os.makedirs(country_folder)
        
        joblib.dump(datasets[country], os.path.join(country_folder, 'train_test_data.pkl'))
        print(f"  Données sauvegardées dans {country_folder}")
    
    # Sauvegarder la liste des pays traités
    with open(os.path.join(OUTPUT_PATH, 'processed_countries.txt'), 'w') as f:
        for country in datasets.keys():
            f.write(f"{country}\n")
    
    return datasets

def main():
    print("Démarrage du processus de feature engineering...")
    print(f"Chemin des données d'entrée: {INPUT_PATH}")
    
    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(INPUT_PATH):
        print(f"ERREUR: Le fichier {INPUT_PATH} n'existe pas!")
        return
    
    # Chargement des données préparées
    try:
        df = load_prepared_data(INPUT_PATH)
        if df is None:
            print("ERREUR: Impossible de charger les données préparées.")
            return
    except Exception as e:
        print(f"ERREUR lors du chargement des données: {str(e)}")
        return
    
    # Création des caractéristiques temporelles
    df = create_time_features(df)
    
    # Création des caractéristiques de décalage
    df = create_lag_features(df)
    
    # Création des caractéristiques de moyenne mobile
    df = create_rolling_features(df)
    
    # Création des caractéristiques de taux de croissance
    df = create_growth_rate_features(df)
    
    # Normalisation des caractéristiques
    df, normalized_cols = normalize_features(df)
    
    # Sauvegarde des données avec les caractéristiques
    feature_data_path = os.path.join(OUTPUT_PATH, 'covid_features_data.csv')
    df.to_csv(feature_data_path, index=False)
    print(f"\nDonnées avec caractéristiques sauvegardées dans {feature_data_path}")
    
    # Préparation des jeux de données par pays
    datasets = prepare_datasets_by_country(df)
    
    print("\nFeature engineering et préparation des jeux de données terminés avec succès!")

if __name__ == "__main__":
    main()
