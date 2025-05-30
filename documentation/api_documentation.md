# Documentation Technique de l'API EPIVIZ 4.1

## Introduction

L'API EPIVIZ 4.1 est une interface programmatique REST qui permet d'accéder aux données historiques de pandémies (COVID-19) et d'obtenir des prédictions sur l'évolution des cas à partir de modèles de machine learning entraînés. Cette API a été développée dans le cadre du projet EPIVIZ pour l'Organisation Mondiale de la Santé (OMS).

## Architecture Technique

L'API EPIVIZ est développée avec les technologies suivantes :

- **Framework** : FastAPI (Python)
- **Validation des données** : Pydantic
- **Documentation interactive** : OpenAPI (Swagger)
- **Modèles de prédiction** : scikit-learn, XGBoost
- **Traitement des données** : pandas, numpy

L'architecture de l'API est organisée de la manière suivante :

```
/api/
  ├── app.py           # Point d'entrée principal de l'API
  └── config.py        # Configuration de l'API
/trained_models/       # Modèles entraînés par pays
/model_data/           # Données préparées pour les modèles
/processed_data/       # Données prétraitées
/documentation/        # Documentation technique
```

## Démarrage de l'API

L'API peut être démarrée avec la commande suivante :

```bash
python run_api.py
```

Par défaut, l'API est accessible à l'adresse http://127.0.0.1:8000 ou http://localhost:8000.

## Endpoints Disponibles

### Endpoint Racine

- **URL** : `/`
- **Méthode** : GET
- **Description** : Point d'entrée principal qui fournit des informations générales sur l'API.
- **Réponse** :
  ```json
  {
    "message": "Bienvenue sur l'API EPIVIZ 4.1",
    "description": "API pour la prédiction des cas de COVID-19 et l'accès aux données historiques",
    "endpoints": {
      "/api/countries": "Liste des pays disponibles",
      "/api/predict/{country}?days=14&model_type=xgboost": "Prédiction des cas pour un pays",
      "/api/historical/{country}?start_date=2020-01-01&end_date=2020-12-31": "Données historiques pour un pays",
      "/api/compare": "Comparaison entre pays",
      "/api/models/{country}": "Métriques des modèles disponibles pour un pays"
    },
    "documentation": "/docs"
  }
  ```

### Liste des Pays

- **URL** : `/api/countries`
- **Méthode** : GET
- **Description** : Retourne la liste de tous les pays disponibles dans les données, ainsi que ceux pour lesquels des modèles ont été entraînés.
- **Réponse** :
  ```json
  {
    "all_countries": ["Afghanistan", "Albania", ..., "Zimbabwe"],
    "countries_with_models": ["US", "Brazil", "United_Kingdom", ...],
    "count": 178,
    "count_with_models": 10
  }
  ```

### Prédiction des Cas

- **URL** : `/api/predict/{country}`
- **Méthode** : GET
- **Description** : Prédit le nombre de nouveaux cas de COVID-19 pour un pays spécifique sur une période donnée.
- **Paramètres** :
  - `country` (chemin) : Nom du pays pour lequel faire la prédiction
  - `days` (query, optionnel) : Nombre de jours à prédire (défaut: 14, max: 30)
  - `model_type` (query, optionnel) : Type de modèle à utiliser (défaut: xgboost)
    - Valeurs possibles : linear_regression, ridge_regression, lasso_regression, random_forest, gradient_boosting, xgboost, lstm
- **Réponse** :
  ```json
  {
    "country": "US",
    "predictions": [
      {"date": "2020-04-08", "predicted_cases": 34570.65},
      {"date": "2020-04-09", "predicted_cases": 35672.12},
      ...
    ],
    "model_used": "xgboost",
    "metrics": {
      "RMSE": 2789.45,
      "MAE": 2156.78,
      "R²": 0.89
    }
  }
  ```
- **Codes de statut** :
  - 200 : Succès
  - 404 : Pays ou modèle non trouvé
  - 500 : Erreur interne du serveur

### Données Historiques

- **URL** : `/api/historical/{country}`
- **Méthode** : GET
- **Description** : Récupère les données historiques pour un pays spécifique sur une période donnée.
- **Paramètres** :
  - `country` (chemin) : Nom du pays pour lequel récupérer les données
  - `start_date` (query, optionnel) : Date de début (format: YYYY-MM-DD)
  - `end_date` (query, optionnel) : Date de fin (format: YYYY-MM-DD)
- **Réponse** :
  ```json
  {
    "country": "US",
    "data": [
      {"date": "2020-01-22", "total_cases": 1, "total_deaths": 0, "new_cases": 1, "new_deaths": 0},
      {"date": "2020-01-23", "total_cases": 1, "total_deaths": 0, "new_cases": 0, "new_deaths": 0},
      ...
    ],
    "count": 365,
    "date_range": {
      "min": "2020-01-22",
      "max": "2021-01-21"
    }
  }
  ```
- **Codes de statut** :
  - 200 : Succès
  - 404 : Pays non trouvé
  - 400 : Format de date invalide
  - 500 : Erreur interne du serveur

### Comparaison entre Pays

- **URL** : `/api/compare`
- **Méthode** : POST
- **Description** : Compare les données entre plusieurs pays sur une période donnée.
- **Corps de la requête** :
  ```json
  {
    "countries": ["US", "Brazil", "India"],
    "start_date": "2020-03-01",
    "end_date": "2020-03-31",
    "metric": "total_cases"
  }
  ```
- **Paramètres** :
  - `countries` (corps) : Liste des pays à comparer
  - `start_date` (corps, optionnel) : Date de début (format: YYYY-MM-DD)
  - `end_date` (corps, optionnel) : Date de fin (format: YYYY-MM-DD)
  - `metric` (corps) : Métrique à comparer (total_cases, total_deaths, new_cases, new_deaths)
- **Réponse** :
  ```json
  {
    "comparison": [
      {
        "country": "US",
        "data": [
          {"date": "2020-03-01", "value": 30},
          {"date": "2020-03-02", "value": 53},
          ...
        ],
        "count": 31,
        "metric": "total_cases",
        "statistics": {
          "min": 30,
          "max": 188172,
          "mean": 64792.5,
          "total": 188172
        }
      },
      ...
    ],
    "metric": "total_cases",
    "countries": ["US", "Brazil", "India"],
    "date_range": {
      "start": "2020-03-01",
      "end": "2020-03-31"
    }
  }
  ```
- **Codes de statut** :
  - 200 : Succès
  - 400 : Requête invalide
  - 500 : Erreur interne du serveur

### Métriques des Modèles

- **URL** : `/api/models/{country}`
- **Méthode** : GET
- **Description** : Récupère les métriques des modèles disponibles pour un pays spécifique.
- **Paramètres** :
  - `country` (chemin) : Nom du pays pour lequel récupérer les métriques
- **Réponse** :
  ```json
  {
    "country": "US",
    "models": [
      {
        "model_name": "linear_regression",
        "metrics": {
          "RMSE": 2789.45,
          "MAE": 2156.78,
          "R²": 0.89,
          "Training Time": 10.5
        }
      },
      ...
    ],
    "best_models": {
      "by_rmse": "xgboost",
      "by_mae": "ridge_regression",
      "by_r2": "xgboost"
    }
  }
  ```
- **Codes de statut** :
  - 200 : Succès
  - 404 : Pays ou métriques non trouvés
  - 500 : Erreur interne du serveur

## Documentation OpenAPI (Swagger)

Une documentation interactive complète de l'API est disponible à l'adresse `/docs` (http://localhost:8000/docs). Cette documentation permet de :

- Explorer tous les endpoints disponibles
- Voir les modèles de données attendus et retournés
- Tester les endpoints directement depuis l'interface
- Comprendre les codes de statut possibles

## Exemples d'Utilisation

### Exemple 1 : Obtenir la Liste des Pays

```python
import requests

response = requests.get("http://localhost:8000/api/countries")
data = response.json()

print(f"Nombre de pays disponibles : {data['count']}")
print(f"Pays avec des modèles entraînés : {', '.join(data['countries_with_models'])}")
```

### Exemple 2 : Obtenir des Prédictions pour les USA

```python
import requests

response = requests.get("http://localhost:8000/api/predict/US?days=7&model_type=xgboost")
data = response.json()

print(f"Prédictions pour {data['country']} avec le modèle {data['model_used']} :")
for prediction in data['predictions']:
    print(f"  - {prediction['date']} : {prediction['predicted_cases']:.2f} nouveaux cas")
```

### Exemple 3 : Comparer les Cas Totaux entre Plusieurs Pays

```python
import requests
import json

payload = {
    "countries": ["US", "Brazil", "India"],
    "start_date": "2020-03-01",
    "end_date": "2020-03-31",
    "metric": "total_cases"
}

response = requests.post(
    "http://localhost:8000/api/compare",
    json=payload,
    headers={"Content-Type": "application/json"}
)
data = response.json()

for country_data in data['comparison']:
    country = country_data['country']
    total = country_data['statistics']['total']
    print(f"{country} : {total} cas totaux au 31 mars 2020")
```

## Gestion des Erreurs

L'API utilise les codes de statut HTTP standard pour indiquer le résultat des requêtes :

- **2xx** : Succès
  - 200 OK : La requête a réussi
- **4xx** : Erreur client
  - 400 Bad Request : La requête est invalide ou mal formée
  - 404 Not Found : La ressource demandée n'existe pas
  - 422 Unprocessable Entity : Erreur de validation des données
- **5xx** : Erreur serveur
  - 500 Internal Server Error : Erreur interne du serveur

Les réponses d'erreur contiennent un corps JSON avec des détails sur l'erreur :

```json
{
  "detail": "Aucun modèle trouvé pour France"
}
```

## Considérations de Sécurité et Performance

### Sécurité

- L'API est configurée pour accepter les requêtes CORS (Cross-Origin Resource Sharing)
- En production, il est recommandé de limiter les origines autorisées dans la configuration CORS
- Aucune authentification n'est actuellement implémentée, ce qui convient pour un environnement de développement local

### Performance

- Les modèles sont chargés en mémoire lors de la première utilisation
- Les prédictions sont calculées à la demande
- Pour les déploiements à grande échelle, il est recommandé de mettre en place un système de mise en cache pour les réponses fréquemment demandées

## Conclusion

L'API EPIVIZ 4.1 fournit une interface complète pour accéder aux données historiques de pandémies et obtenir des prédictions basées sur des modèles de machine learning. Elle est conçue pour être facile à utiliser, bien documentée et extensible.

Pour toute question ou problème, veuillez consulter la documentation ou contacter l'équipe de développement.
