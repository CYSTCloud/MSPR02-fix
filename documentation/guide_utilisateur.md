# Guide Utilisateur - EPIVIZ 4.1

## Introduction

Bienvenue dans le guide utilisateur d'EPIVIZ 4.1, un système d'analyse prédictive des cas de pandémie COVID-19. Ce guide vous aidera à comprendre comment utiliser efficacement notre API pour accéder aux données historiques et obtenir des prédictions fiables sur l'évolution des cas.

![EPIVIZ Logo](https://via.placeholder.com/500x150?text=EPIVIZ+4.1)

## À qui s'adresse ce guide ?

Ce guide est destiné aux :
- Professionnels de la santé publique
- Chercheurs et épidémiologistes
- Développeurs d'applications et data scientists
- Décideurs et gestionnaires de crise

## Prérequis

Pour utiliser l'API EPIVIZ 4.1, vous aurez besoin de :
- Une connexion Internet
- Connaissances de base en API REST
- Un outil pour effectuer des requêtes HTTP (navigateur, Postman, curl, etc.)
- Python (optionnel, pour les exemples de code)

## Démarrage rapide

### Accès à l'API

L'API EPIVIZ 4.1 est accessible à l'adresse suivante :
```
http://localhost:8000
```

> **Note** : Si vous accédez à l'API depuis un autre serveur, remplacez "localhost" par l'adresse IP ou le nom de domaine correspondant.

### Exploration de l'API

Pour explorer l'API et ses fonctionnalités :
1. Ouvrez votre navigateur
2. Accédez à l'URL : `http://localhost:8000/docs`
3. Une interface interactive Swagger s'affichera, vous permettant de :
   - Consulter tous les endpoints disponibles
   - Tester les requêtes directement depuis le navigateur
   - Visualiser les modèles de données et les réponses

![Interface Swagger](https://via.placeholder.com/800x400?text=Interface+Swagger)

## Fonctionnalités principales

### 1. Obtenir la liste des pays disponibles

Pour récupérer la liste des pays pour lesquels des données sont disponibles :

**Endpoint** : `/api/countries`  
**Méthode** : GET

#### Exemple de requête :
```bash
curl -X GET http://localhost:8000/api/countries
```

#### Exemple de réponse :
```json
{
  "all_countries": ["Afghanistan", "Albania", ..., "Zimbabwe"],
  "countries_with_models": ["US", "Brazil", "United_Kingdom", ...],
  "count": 178,
  "count_with_models": 10
}
```

### 2. Consulter les données historiques

Pour accéder aux données historiques d'un pays spécifique :

**Endpoint** : `/api/historical/{country}`  
**Méthode** : GET  
**Paramètres** :
- `country` (obligatoire) : Nom du pays (ex: "US", "France", "Brazil")
- `start_date` (optionnel) : Date de début (format: YYYY-MM-DD)
- `end_date` (optionnel) : Date de fin (format: YYYY-MM-DD)

#### Exemple de requête :
```bash
curl -X GET "http://localhost:8000/api/historical/US?start_date=2020-03-01&end_date=2020-03-31"
```

#### Exemple de réponse :
```json
{
  "country": "US",
  "data": [
    {"date": "2020-03-01", "total_cases": 30, "total_deaths": 1, "new_cases": 0, "new_deaths": 0},
    {"date": "2020-03-02", "total_cases": 53, "total_deaths": 6, "new_cases": 23, "new_deaths": 5},
    // ... autres jours
  ],
  "count": 31,
  "date_range": {
    "min": "2020-03-01",
    "max": "2020-03-31"
  }
}
```

### 3. Obtenir des prédictions

Pour obtenir des prédictions sur l'évolution des cas pour un pays donné :

**Endpoint** : `/api/predict/{country}`  
**Méthode** : GET  
**Paramètres** :
- `country` (obligatoire) : Nom du pays
- `days` (optionnel) : Nombre de jours à prédire (défaut: 14, max: 30)
- `model_type` (optionnel) : Type de modèle à utiliser (défaut: xgboost)

#### Exemple de requête :
```bash
curl -X GET "http://localhost:8000/api/predict/US?days=7&model_type=xgboost"
```

#### Exemple de réponse :
```json
{
  "country": "US",
  "predictions": [
    {"date": "2020-04-08", "predicted_cases": 34570.65},
    {"date": "2020-04-09", "predicted_cases": 35672.12},
    // ... autres jours
  ],
  "model_used": "xgboost",
  "metrics": {
    "RMSE": 2789.45,
    "MAE": 2156.78,
    "R²": 0.89
  }
}
```

### 4. Comparer des pays

Pour comparer les données entre plusieurs pays :

**Endpoint** : `/api/compare`  
**Méthode** : POST  
**Corps de la requête** :
```json
{
  "countries": ["US", "Brazil", "India"],
  "start_date": "2020-03-01",
  "end_date": "2020-03-31",
  "metric": "total_cases"
}
```

#### Exemple de requête avec curl :
```bash
curl -X POST "http://localhost:8000/api/compare" \
     -H "Content-Type: application/json" \
     -d '{"countries":["US","Brazil","India"],"start_date":"2020-03-01","end_date":"2020-03-31","metric":"total_cases"}'
```

#### Exemple de réponse :
```json
{
  "comparison": [
    {
      "country": "US",
      "data": [/* ... données pour les USA ... */],
      "statistics": {
        "min": 30,
        "max": 188172,
        "mean": 64792.5,
        "total": 188172
      }
    },
    // ... autres pays
  ],
  "metric": "total_cases",
  "countries": ["US", "Brazil", "India"],
  "date_range": {
    "start": "2020-03-01",
    "end": "2020-03-31"
  }
}
```

### 5. Consulter les métriques des modèles

Pour évaluer les performances des différents modèles pour un pays donné :

**Endpoint** : `/api/models/{country}`  
**Méthode** : GET

#### Exemple de requête :
```bash
curl -X GET "http://localhost:8000/api/models/US"
```

#### Exemple de réponse :
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
    // ... autres modèles
  ],
  "best_models": {
    "by_rmse": "xgboost",
    "by_mae": "ridge_regression",
    "by_r2": "xgboost"
  }
}
```

## Exemples d'utilisation avec Python

### Installation des dépendances

```bash
pip install requests pandas matplotlib
```

### Exemple 1 : Récupérer et visualiser les données historiques

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Récupérer les données historiques pour les USA
response = requests.get("http://localhost:8000/api/historical/US?start_date=2020-01-01&end_date=2020-12-31")
data = response.json()

# Convertir en DataFrame
df = pd.DataFrame(data['data'])
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Visualiser les nouveaux cas
plt.figure(figsize=(12, 6))
plt.title("Évolution des nouveaux cas de COVID-19 aux USA (2020)")
plt.plot(df.index, df['new_cases'], color='blue')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("usa_covid_cases_2020.png")
plt.show()
```

![Exemple de graphique](https://via.placeholder.com/800x400?text=Graphique+COVID+USA+2020)

### Exemple 2 : Obtenir et comparer des prédictions

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Récupérer les prédictions pour différents modèles
models = ['linear_regression', 'ridge_regression', 'xgboost']
predictions = {}

for model in models:
    response = requests.get(f"http://localhost:8000/api/predict/US?days=14&model_type={model}")
    predictions[model] = response.json()

# Visualiser les prédictions
plt.figure(figsize=(12, 6))
plt.title("Prédictions de nouveaux cas de COVID-19 aux USA")

for model, data in predictions.items():
    dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in data['predictions']]
    values = [p['predicted_cases'] for p in data['predictions']]
    plt.plot(dates, values, label=f"{model} (RMSE: {data['metrics']['RMSE']:.2f})")

plt.grid(True, alpha=0.3)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("usa_covid_predictions.png")
plt.show()
```

![Exemple de comparaison de prédictions](https://via.placeholder.com/800x400?text=Comparaison+Prédictions)

### Exemple 3 : Comparer plusieurs pays

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

# Définir les pays et la période à comparer
payload = {
    "countries": ["US", "Brazil", "India", "France", "Germany"],
    "start_date": "2020-06-01",
    "end_date": "2020-06-30",
    "metric": "new_cases"
}

# Effectuer la requête
response = requests.post(
    "http://localhost:8000/api/compare",
    json=payload,
    headers={"Content-Type": "application/json"}
)
data = response.json()

# Visualiser la comparaison
plt.figure(figsize=(14, 8))
plt.title(f"Comparaison des {payload['metric']} entre pays (Juin 2020)")

for country_data in data['comparison']:
    country = country_data['country']
    df = pd.DataFrame(country_data['data'])
    df['date'] = pd.to_datetime(df['date'])
    plt.plot(df['date'], df['value'], label=f"{country} (max: {country_data['statistics']['max']})")

plt.grid(True, alpha=0.3)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("countries_comparison.png")
plt.show()
```

![Exemple de comparaison entre pays](https://via.placeholder.com/800x400?text=Comparaison+Pays)

## Bonnes pratiques et conseils

### Optimisation des requêtes
- Limitez la période de temps dans vos requêtes pour des réponses plus rapides
- Utilisez la pagination lorsqu'elle est disponible
- Mettez en cache les résultats fréquemment utilisés

### Interprétation des prédictions
- Les prédictions sont plus fiables pour un horizon court terme (7-14 jours)
- Tenez compte des métriques de performance (RMSE, MAE, R²) pour évaluer la fiabilité
- Comparez plusieurs modèles pour une meilleure évaluation
- N'oubliez pas que les prédictions sont des estimations statistiques et non des certitudes

### Visualisation des données
- Utilisez des échelles logarithmiques pour visualiser des tendances exponentielles
- Préférez les moyennes mobiles pour lisser les fluctuations quotidiennes
- Normalisez les données par population pour comparer des pays de tailles différentes

## Résolution des problèmes courants

### Erreur 404 : Ressource non trouvée
- Vérifiez l'orthographe du nom du pays
- Assurez-vous que le pays dispose de données ou de modèles entraînés
- Consultez la liste des pays disponibles via l'endpoint `/api/countries`

### Erreur 400 : Requête incorrecte
- Vérifiez le format des dates (YYYY-MM-DD)
- Assurez-vous que la date de début est antérieure à la date de fin
- Vérifiez que les métriques et les paramètres sont correctement orthographiés

### Erreur 500 : Erreur serveur
- Le serveur peut être surchargé, réessayez plus tard
- Vérifiez que l'API est en cours d'exécution
- Contactez l'administrateur si le problème persiste

## Ressources supplémentaires

- [Documentation technique complète de l'API](./api_documentation.md)
- [Documentation des modèles IA](./modeles_ia_documentation.md)
- [GitHub du projet](https://github.com/epiviz/epiviz4.1)
- [Données sources COVID-19](https://github.com/CSSEGISandData/COVID-19)

## Support et contact

Pour toute question ou assistance :
- Email : support@epiviz.org
- Forum d'entraide : [forum.epiviz.org](https://forum.epiviz.org)
- Tickets d'incident : [github.com/epiviz/epiviz4.1/issues](https://github.com/epiviz/epiviz4.1/issues)

---

© 2025 - EPIVIZ Project Team - Tous droits réservés
