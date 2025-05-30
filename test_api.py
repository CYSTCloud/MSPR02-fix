"""
EPIVIZ 4.1 - Tests des endpoints de l'API
-----------------------------------------
Ce script teste tous les endpoints de l'API EPIVIZ pour vérifier leur bon fonctionnement.
"""

import requests
import json
import time
import sys
import os
from pprint import pprint

# Configuration du test
API_BASE_URL = "http://localhost:8000"
TEST_COUNTRY = "US"  # Pays avec des modèles entraînés
TEST_COUNTRIES = ["US", "Brazil", "China"]  # Pays pour le test de comparaison

def print_separator():
    """Affiche une ligne de séparation pour améliorer la lisibilité"""
    print("\n" + "-"*50 + "\n")

def test_root_endpoint():
    """Teste l'endpoint racine de l'API"""
    print("Test de l'endpoint racine (/)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print("Réponse:")
            pprint(data)
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_countries_endpoint():
    """Teste l'endpoint de liste des pays"""
    print("Test de l'endpoint de liste des pays (/api/countries)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/countries")
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print(f"Nombre de pays: {data['count']}")
            print(f"Pays avec modèles: {data['count_with_models']}")
            
            # Afficher les 5 premiers pays
            print("Exemples de pays:")
            for country in data['all_countries'][:5]:
                print(f"  - {country}")
            
            # Vérifier si notre pays de test est disponible
            if TEST_COUNTRY in data['countries_with_models']:
                print(f"✅ Le pays de test '{TEST_COUNTRY}' est disponible avec des modèles")
            else:
                print(f"❌ Le pays de test '{TEST_COUNTRY}' n'est pas disponible avec des modèles")
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_predict_endpoint():
    """Teste l'endpoint de prédiction"""
    print(f"Test de l'endpoint de prédiction (/api/predict/{TEST_COUNTRY})")
    
    try:
        # Test avec les paramètres par défaut
        response = requests.get(f"{API_BASE_URL}/api/predict/{TEST_COUNTRY}")
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print(f"Pays: {data['country']}")
            print(f"Modèle utilisé: {data['model_used']}")
            
            # Afficher les métriques du modèle
            if 'metrics' in data and data['metrics']:
                print("Métriques du modèle:")
                for metric, value in data['metrics'].items():
                    print(f"  - {metric}: {value}")
            
            # Afficher les premières prédictions
            print("Prédictions:")
            for i, pred in enumerate(data['predictions'][:5]):
                print(f"  - {pred['date']}: {pred['predicted_cases']:.2f} cas")
            
            # Test avec des paramètres spécifiques
            print("\nTest avec des paramètres spécifiques (days=7, model_type=random_forest)")
            response = requests.get(f"{API_BASE_URL}/api/predict/{TEST_COUNTRY}?days=7&model_type=random_forest")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Statut: OK (200)")
                print(f"Modèle utilisé: {data['model_used']}")
                print(f"Nombre de prédictions: {len(data['predictions'])}")
            else:
                print(f"❌ Erreur: Statut {response.status_code}")
                print(f"Réponse: {response.text}")
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_historical_endpoint():
    """Teste l'endpoint de données historiques"""
    print(f"Test de l'endpoint de données historiques (/api/historical/{TEST_COUNTRY})")
    
    try:
        # Test avec les paramètres par défaut
        response = requests.get(f"{API_BASE_URL}/api/historical/{TEST_COUNTRY}")
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print(f"Pays: {data['country']}")
            print(f"Nombre d'enregistrements: {data['count']}")
            print(f"Plage de dates: {data['date_range']['min']} à {data['date_range']['max']}")
            
            # Afficher les premiers enregistrements
            print("Premiers enregistrements:")
            for i, record in enumerate(data['data'][:3]):
                print(f"  - {record['date']}: {record['total_cases']} cas, {record['total_deaths']} décès")
            
            # Test avec des paramètres de date
            print("\nTest avec des paramètres de date (start_date=2020-03-01, end_date=2020-03-31)")
            response = requests.get(f"{API_BASE_URL}/api/historical/{TEST_COUNTRY}?start_date=2020-03-01&end_date=2020-03-31")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Statut: OK (200)")
                print(f"Nombre d'enregistrements: {data['count']}")
                print(f"Plage de dates: {data['date_range']['min']} à {data['date_range']['max']}")
            else:
                print(f"❌ Erreur: Statut {response.status_code}")
                print(f"Réponse: {response.text}")
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_compare_endpoint():
    """Teste l'endpoint de comparaison entre pays"""
    print("Test de l'endpoint de comparaison entre pays (/api/compare)")
    
    try:
        # Préparer les données pour la requête POST
        payload = {
            "countries": TEST_COUNTRIES,
            "start_date": "2020-03-01",
            "end_date": "2020-03-31",
            "metric": "total_cases"
        }
        
        # Envoyer la requête POST
        response = requests.post(
            f"{API_BASE_URL}/api/compare",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print(f"Métrique: {data['metric']}")
            print(f"Pays comparés: {', '.join(data['countries'])}")
            
            # Afficher des statistiques pour chaque pays
            print("Statistiques par pays:")
            for country_data in data['comparison']:
                country = country_data['country']
                stats = country_data['statistics']
                print(f"  - {country}: Min={stats['min']}, Max={stats['max']}, Moyenne={stats['mean']:.2f}, Total={stats['total']}")
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_models_endpoint():
    """Teste l'endpoint de métriques des modèles"""
    print(f"Test de l'endpoint de métriques des modèles (/api/models/{TEST_COUNTRY})")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/models/{TEST_COUNTRY}")
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            print("✅ Statut: OK (200)")
            
            # Afficher le contenu de la réponse
            data = response.json()
            print(f"Pays: {data['country']}")
            
            # Afficher les métriques pour chaque modèle
            print("Métriques par modèle:")
            for model_data in data['models']:
                model_name = model_data['model_name']
                metrics = model_data['metrics']
                print(f"  - {model_name}:")
                print(f"    RMSE: {metrics['RMSE']:.2f}")
                print(f"    MAE: {metrics['MAE']:.2f}")
                print(f"    R²: {metrics['R²']:.4f}")
            
            # Afficher les meilleurs modèles
            print("Meilleurs modèles:")
            print(f"  - Par RMSE: {data['best_models']['by_rmse']}")
            print(f"  - Par MAE: {data['best_models']['by_mae']}")
            print(f"  - Par R²: {data['best_models']['by_r2']}")
            
            return True
        else:
            print(f"❌ Erreur: Statut {response.status_code}")
            print(f"Réponse: {response.text}")
            
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def run_api_tests():
    """Exécute tous les tests des endpoints de l'API"""
    print("=== TEST SIMPLIFIE DE L'API EPIVIZ 4.1 ===")
    
    # Vérifier que l'API est en cours d'exécution
    print("Vérification de la disponibilité de l'API...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Statut de la réponse: {response.status_code}")
        if response.status_code == 200:
            print("L'API est disponible")
        else:
            print(f"L'API répond avec le statut {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"Erreur de connexion: {str(e)}")
        print("L'API n'est pas disponible. Assurez-vous qu'elle est en cours d'exécution.")
        print(f"Commande: python run_api.py")
        return False
    
    # Test simplié des endpoints principaux
    endpoints = [
        "/api/countries",
        f"/api/predict/{TEST_COUNTRY}?days=5",
        f"/api/historical/{TEST_COUNTRY}?start_date=2020-03-01&end_date=2020-03-10",
        f"/api/models/{TEST_COUNTRY}"
    ]
    
    for endpoint in endpoints:
        print(f"\nTest de l'endpoint: {endpoint}")
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            print(f"Statut: {response.status_code}")
            if response.status_code == 200:
                print("Endpoint fonctionnel")
            else:
                print(f"Problème avec l'endpoint: {response.text[:200]}")
        except Exception as e:
            print(f"Erreur lors du test de {endpoint}: {str(e)}")
    
    # Test de l'endpoint POST /api/compare
    print("\nTest de l'endpoint POST: /api/compare")
    try:
        payload = {
            "countries": TEST_COUNTRIES[:2],  # Limiter à 2 pays pour simplifier
            "start_date": "2020-03-01",
            "end_date": "2020-03-10",
            "metric": "total_cases"
        }
        response = requests.post(f"{API_BASE_URL}/api/compare", json=payload)
        print(f"Statut: {response.status_code}")
        if response.status_code == 200:
            print("Endpoint fonctionnel")
        else:
            print(f"Problème avec l'endpoint /api/compare: {response.text[:200]}")
    except Exception as e:
        print(f"Erreur lors du test de /api/compare: {str(e)}")
    
    print("\nTests terminés.")
    return True

if __name__ == "__main__":
    # Vérifier si l'API est déjà en cours d'exécution
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print("API déjà en cours d'exécution, démarrage des tests...")
        run_api_tests()
    except requests.exceptions.ConnectionError:
        print("L'API n'est pas en cours d'exécution.")
        print("Vous devez d'abord démarrer l'API dans un terminal séparé avec la commande:")
        print("python run_api.py")
        sys.exit(1)
