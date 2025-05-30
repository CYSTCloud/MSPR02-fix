"""
Test spécifique de l'endpoint /api/models/US
"""
import requests
import json

# URL de l'API
API_URL = "http://127.0.0.1:8000"

# Test de l'endpoint des métriques des modèles
response = requests.get(f"{API_URL}/api/models/US")

print(f"Statut de la réponse: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("Réponse de l'endpoint /api/models/US:")
    print(f"Pays: {data['country']}")
    
    # Afficher les modèles disponibles et leurs métriques
    print("\nModèles disponibles:")
    for model in data['models']:
        print(f"- {model['model_name']}:")
        for metric_name, metric_value in model['metrics'].items():
            print(f"  {metric_name}: {metric_value}")
    
    # Afficher les meilleurs modèles
    print("\nMeilleurs modèles:")
    for metric, model_name in data['best_models'].items():
        print(f"- Meilleur modèle selon {metric}: {model_name}")
else:
    print(f"Erreur: {response.text}")
