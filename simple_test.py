"""
Test simple de l'API EPIVIZ pour diagnostiquer les problèmes
"""
import requests
import sys

# Configuration
API_URL = "http://127.0.0.1:8000"

def test_endpoint(url, method="GET", data=None):
    """Teste un endpoint spécifique et affiche le résultat"""
    print(f"\nTest de {method} {url}")
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Statut: {response.status_code}")
        if response.status_code == 200:
            print("Succès!")
            try:
                # Afficher juste les clés pour éviter une sortie trop longue
                keys = list(response.json().keys())
                print(f"Clés dans la réponse: {keys}")
                return True
            except:
                print("Impossible de décoder la réponse JSON")
                return False
        else:
            print(f"Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def main():
    """Fonction principale exécutant les tests simples"""
    print("=== TEST SIMPLE DE L'API EPIVIZ ===")
    
    # Test de l'endpoint racine
    success = test_endpoint(f"{API_URL}/")
    
    # Test de l'endpoint countries
    success = test_endpoint(f"{API_URL}/api/countries") and success
    
    # Test de l'endpoint de prédiction pour les USA
    success = test_endpoint(f"{API_URL}/api/predict/US?days=5") and success
    
    # Test de l'endpoint d'historique pour les USA
    success = test_endpoint(f"{API_URL}/api/historical/US?start_date=2020-03-01&end_date=2020-03-10") and success
    
    # Test de l'endpoint de comparaison (POST)
    data = {
        "countries": ["US", "Brazil"],
        "start_date": "2020-03-01",
        "end_date": "2020-03-10",
        "metric": "total_cases"
    }
    success = test_endpoint(f"{API_URL}/api/compare", method="POST", data=data) and success
    
    # Test de l'endpoint des métriques de modèles
    success = test_endpoint(f"{API_URL}/api/models/US") and success
    
    # Résultat global
    print("\n=== RÉSULTAT ===")
    if success:
        print("Tous les tests ont réussi!")
    else:
        print("Certains tests ont échoué.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
