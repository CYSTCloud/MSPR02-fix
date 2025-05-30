"""
EPIVIZ 4.1 - Exploration et préparation des données
---------------------------------------------------
Ce script réalise l'exploration et la préparation des données COVID-19
pour l'entraînement des modèles prédictifs.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Configuration pour améliorer la lisibilité des graphiques
plt.style.use('seaborn-v0_8-whitegrid')
sns.set(font_scale=1.2)
plt.rcParams['figure.figsize'] = (14, 8)

# Chemins des fichiers
DATA_PATH = os.path.join(os.getcwd(), 'data_to_train_covid19.csv')
OUTPUT_PATH = os.path.join(os.getcwd(), 'processed_data')

# Création du dossier de sortie s'il n'existe pas
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def load_data(filepath):
    """Charge les données depuis un fichier CSV"""
    print(f"Chargement des données depuis {filepath}...")
    try:
        df = pd.read_csv(filepath)
        print(f"Données chargées avec succès. Dimensions: {df.shape}")
        return df
    except Exception as e:
        print(f"Erreur lors du chargement des données: {str(e)}")
        return None

def explore_data(df):
    """Réalise une exploration initiale des données"""
    print("\n=== EXPLORATION DES DONNÉES ===")
    
    # Informations générales
    print("\nAperçu des données:")
    print(df.head())
    
    print("\nTypes des colonnes:")
    print(df.dtypes)
    
    print("\nStatistiques descriptives:")
    print(df.describe())
    
    print("\nValeurs manquantes par colonne:")
    print(df.isnull().sum())
    
    # Conversion de la colonne date en format datetime
    df['date_value'] = pd.to_datetime(df['date_value'])
    
    # Liste des pays uniques
    countries = df['country'].unique()
    print(f"\nNombre de pays distincts: {len(countries)}")
    print(f"Premiers pays dans le jeu de données: {', '.join(countries[:10])}")
    
    # Plage temporelle
    date_range = df['date_value'].max() - df['date_value'].min()
    print(f"\nPlage temporelle: {df['date_value'].min().date()} à {df['date_value'].max().date()} ({date_range.days} jours)")
    
    # Statistiques par pays
    country_stats = df.groupby('country').agg({
        'total_cases': 'max',
        'total_deaths': 'max',
        'new_cases': 'sum',
        'new_deaths': 'sum'
    }).sort_values('total_cases', ascending=False)
    
    print("\nTop 10 pays par nombre total de cas:")
    print(country_stats.head(10))
    
    return df

def visualize_data(df):
    """Crée des visualisations pour mieux comprendre les données"""
    print("\n=== VISUALISATION DES DONNÉES ===")
    
    # Sélection des pays avec le plus grand nombre de cas
    top_countries = df.groupby('country')['total_cases'].max().sort_values(ascending=False).head(10).index
    
    # Evolution des cas totaux pour les pays les plus touchés
    plt.figure(figsize=(16, 10))
    for country in top_countries:
        country_data = df[df['country'] == country]
        plt.plot(country_data['date_value'], country_data['total_cases'], label=country)
    
    plt.title('Évolution des cas totaux de COVID-19 pour les 10 pays les plus touchés')
    plt.xlabel('Date')
    plt.ylabel('Nombre total de cas')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, 'total_cases_evolution.png'))
    plt.close()
    
    # Evolution des nouveaux cas pour les pays les plus touchés
    plt.figure(figsize=(16, 10))
    for country in top_countries:
        country_data = df[df['country'] == country]
        # Moyenne mobile sur 7 jours pour lisser les données
        country_data['new_cases_7d_avg'] = country_data['new_cases'].rolling(window=7).mean()
        plt.plot(country_data['date_value'], country_data['new_cases_7d_avg'], label=country)
    
    plt.title('Évolution des nouveaux cas quotidiens de COVID-19 (moyenne mobile 7 jours)')
    plt.xlabel('Date')
    plt.ylabel('Nouveaux cas (moyenne mobile 7 jours)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, 'new_cases_evolution.png'))
    plt.close()
    
    print("Visualisations enregistrées dans le dossier 'processed_data'")

def analyze_data_quality(df):
    """Analyse la qualité des données et identifie les problèmes potentiels"""
    print("\n=== ANALYSE DE LA QUALITÉ DES DONNÉES ===")
    
    # Vérification des valeurs négatives
    negative_cases = df[df['new_cases'] < 0]
    negative_deaths = df[df['new_deaths'] < 0]
    
    print(f"Nombre d'entrées avec des nouveaux cas négatifs: {len(negative_cases)}")
    if len(negative_cases) > 0:
        print(negative_cases.head())
    
    print(f"Nombre d'entrées avec des nouveaux décès négatifs: {len(negative_deaths)}")
    if len(negative_deaths) > 0:
        print(negative_deaths.head())
    
    # Vérification de la cohérence entre total_cases/total_deaths et new_cases/new_deaths
    inconsistencies = []
    for country in df['country'].unique():
        country_data = df[df['country'] == country].sort_values('date_value')
        
        # Vérifie si les totaux augmentent de façon cohérente avec les nouveaux cas/décès
        for i in range(1, len(country_data)):
            prev_total_cases = country_data.iloc[i-1]['total_cases']
            current_total_cases = country_data.iloc[i]['total_cases']
            new_cases = country_data.iloc[i]['new_cases']
            
            if abs((current_total_cases - prev_total_cases) - new_cases) > 1e-10 and not np.isnan(new_cases):
                inconsistencies.append({
                    'country': country,
                    'date': country_data.iloc[i]['date_value'],
                    'prev_total': prev_total_cases,
                    'current_total': current_total_cases,
                    'diff': current_total_cases - prev_total_cases,
                    'reported_new': new_cases
                })
                
            if len(inconsistencies) >= 10:  # Limite à 10 exemples
                break
        
        if len(inconsistencies) >= 10:
            break
    
    print(f"\nNombre d'incohérences détectées entre totaux et nouveaux cas: {len(inconsistencies)}")
    if inconsistencies:
        inconsistencies_df = pd.DataFrame(inconsistencies)
        print(inconsistencies_df.head())
    
    return df

def prepare_data_for_modeling(df):
    """Prépare les données pour la modélisation"""
    print("\n=== PRÉPARATION DES DONNÉES POUR LA MODÉLISATION ===")
    
    # Conversion de la date en datetime si ce n'est pas déjà fait
    if df['date_value'].dtype != 'datetime64[ns]':
        df['date_value'] = pd.to_datetime(df['date_value'])
    
    # Création de caractéristiques temporelles
    df['day'] = df['date_value'].dt.day
    df['month'] = df['date_value'].dt.month
    df['year'] = df['date_value'].dt.year
    df['day_of_week'] = df['date_value'].dt.dayofweek
    
    # Gestion des valeurs manquantes
    print("\nTraitement des valeurs manquantes...")
    for col in ['new_cases', 'new_deaths', 'total_cases', 'total_deaths']:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            print(f"  - Colonne {col}: {missing_count} valeurs manquantes")
            # Pour les valeurs manquantes dans new_cases et new_deaths, remplacer par 0
            if col in ['new_cases', 'new_deaths']:
                df[col] = df[col].fillna(0)
            # Pour les valeurs manquantes dans total_cases et total_deaths, utiliser la dernière valeur connue
            else:
                df[col] = df.groupby('country')[col].fillna(method='ffill')
                # S'il reste des valeurs manquantes (au début des séries), remplacer par 0
                df[col] = df[col].fillna(0)
    
    # Gestion des valeurs aberrantes ou négatives
    for col in ['new_cases', 'new_deaths']:
        # Remplacer les valeurs négatives par 0
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            print(f"  - Colonne {col}: {negative_count} valeurs négatives remplacées par 0")
            df[col] = df[col].clip(lower=0)
    
    # Vérification de la cohérence des totaux
    print("\nRecalcul des totaux pour assurer la cohérence...")
    # Faire une copie du DataFrame original pour la comparaison
    df_original = df.copy()
    
    # Recalculer les totaux à partir des nouveaux cas/décès
    for country in df['country'].unique():
        country_mask = df['country'] == country
        country_data = df[country_mask].sort_values('date_value')
        
        # Recalculer total_cases
        df.loc[country_mask, 'total_cases_recalc'] = country_data['new_cases'].cumsum()
        
        # Recalculer total_deaths
        df.loc[country_mask, 'total_deaths_recalc'] = country_data['new_deaths'].cumsum()
    
    # Comparer les totaux originaux et recalculés
    cases_diff = ((df['total_cases'] - df['total_cases_recalc']).abs() > 1).sum()
    deaths_diff = ((df['total_deaths'] - df['total_deaths_recalc']).abs() > 1).sum()
    
    print(f"Différences entre totaux originaux et recalculés:")
    print(f"  - Cas: {cases_diff} différences")
    print(f"  - Décès: {deaths_diff} différences")
    
    # Décider quelle version utiliser
    print("Utilisation des totaux recalculés pour assurer la cohérence")
    df['total_cases'] = df['total_cases_recalc']
    df['total_deaths'] = df['total_deaths_recalc']
    df = df.drop(['total_cases_recalc', 'total_deaths_recalc'], axis=1)
    
    # Enregistrer les données préparées
    print("\nEnregistrement des données préparées...")
    df.to_csv(os.path.join(OUTPUT_PATH, 'prepared_covid_data.csv'), index=False)
    print(f"Données préparées enregistrées dans {os.path.join(OUTPUT_PATH, 'prepared_covid_data.csv')}")
    
    return df

def main():
    # Chargement des données
    df = load_data(DATA_PATH)
    if df is None:
        return
    
    # Exploration des données
    df = explore_data(df)
    
    # Analyse de la qualité des données
    df = analyze_data_quality(df)
    
    # Visualisations
    visualize_data(df)
    
    # Préparation des données pour la modélisation
    df = prepare_data_for_modeling(df)
    
    print("\nExploration et préparation des données terminées avec succès!")

if __name__ == "__main__":
    main()
