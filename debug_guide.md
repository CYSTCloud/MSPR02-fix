# Guide de débogage EPIVIZ 4.1

## Problèmes identifiés et solutions

### 1. Problèmes CORS persistants

**Symptômes:**
```
Access to XMLHttpRequest at 'http://127.0.0.1:8088/api/historical/France' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Cause fondamentale:**
Le problème n'est pas dans la configuration CORS de FastAPI, mais dans la façon dont le serveur est lancé et comment il gère les réponses d'erreur. Les en-têtes CORS ne sont pas correctement ajoutés aux réponses d'erreur (500).

**Solution:**
1. Arrêtez tous les serveurs en cours d'exécution
2. Modifiez le fichier `api/app.py` pour utiliser la configuration CORS la plus simple possible
3. Implémentez des gestionnaires d'exceptions globaux avec CORS
4. Redémarrez le serveur avec `--host` défini correctement

```python
# Dans app.py - Configuration CORS la plus simple
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# CORS doit être le premier middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestionnaire d'exception global pour ajouter des en-têtes CORS même aux erreurs
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={"Access-Control-Allow-Origin": "*"}
    )
```

Lancer le serveur avec:
```
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8088
```

### 2. Erreurs 500 dans les endpoints API

**Symptômes:**
```
GET http://127.0.0.1:8088/api/historical/France net::ERR_FAILED 500 (Internal Server Error)
```

**Cause fondamentale:**
La fonction `load_data()` échoue lors de l'accès aux fichiers de données. Les chemins de fichiers sont incorrects ou les fichiers n'existent pas.

**Solution:**
1. Vérifiez l'existence des fichiers de données:
   - `data_to_train_covid19.csv`
   - `processed_data/prepared_covid_data.csv`

2. Si les fichiers n'existent pas, utilisez un générateur de données robuste:

```python
def load_data():
    """Charge les données historiques ou génère des données simulées si nécessaires"""
    try:
        if os.path.exists(PROCESSED_DATA_PATH):
            logger.info(f"Chargement des données préparées depuis {PROCESSED_DATA_PATH}")
            data = pd.read_csv(PROCESSED_DATA_PATH)
        elif os.path.exists(DATA_PATH):
            logger.info(f"Chargement des données brutes depuis {DATA_PATH}")
            data = pd.read_csv(DATA_PATH)
        else:
            logger.warning("Aucun fichier de données trouvé. Génération de données simulées.")
            return generate_sample_data()
            
        # Uniformiser les noms de colonnes (date_value -> date)
        if 'date_value' in data.columns and 'date' not in data.columns:
            data = data.rename(columns={'date_value': 'date'})
            
        # Conversion de la date en datetime
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
        
        return data
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {str(e)}")
        logger.warning("Génération de données simulées suite à une erreur.")
        return generate_sample_data()
```

### 3. Pays inconnus (Cuba n'est pas dans la liste)

**Symptômes:**
```
Pas de modèle amélioré disponible pour Cuba. Essayez US, Brazil ou France.
```

**Cause fondamentale:**
Le pays "Cuba" n'est pas inclus dans la liste des pays disponibles dans l'API, mais il est présent dans le frontend.

**Solution:**
1. Assurez-vous que les pays disponibles sont synchronisés entre le frontend et le backend
2. Ajoutez Cuba à la liste des pays disponibles dans l'API

```python
# Ajouter Cuba à la liste des pays
COUNTRIES = ["France", "US", "Brazil", "Afghanistan", "China", "Italy", "Spain", "Germany", "Cuba", "United Kingdom", "India"]
```

## Diagnostic complet du projet

### Structure des fichiers à vérifier

```
EPIVIZ 4.1/
├── api/
│   ├── app.py - Problèmes CORS et gestion des erreurs
│   └── enhanced_prediction.py - Problèmes avec le chargement des modèles
├── data_to_train_covid19.csv - Peut-être manquant
├── processed_data/
│   └── prepared_covid_data.csv - Peut-être manquant
└── frontend/
    └── src/
        ├── services/
        │   └── api.js - Problèmes avec les URL et la gestion des erreurs
        └── pages/
            └── Predictions.jsx - Problèmes avec les paramètres de requête
```

### Comment tester l'API indépendamment du frontend

Utilisez des outils comme curl ou Postman pour tester l'API sans passer par le frontend:

```bash
# Tester l'endpoint des pays
curl -X GET http://127.0.0.1:8088/api/countries

# Tester l'endpoint historique
curl -X GET http://127.0.0.1:8088/api/historical/France

# Tester l'endpoint de prédiction
curl -X GET http://127.0.0.1:8088/api/predict/enhanced/France?days=30&model_type=enhanced
```

## Synthèse des actions à entreprendre

1. **Arrêtez tous les serveurs** actuellement en cours d'exécution
2. **Corrigez la configuration CORS** dans `app.py` en utilisant le code fourni ci-dessus
3. **Implémentez une gestion robuste des données** qui fonctionne même sans fichiers
4. **Ajoutez des gestionnaires d'exceptions globaux** pour garantir que toutes les réponses incluent les en-têtes CORS
5. **Synchronisez les listes de pays** entre le frontend et le backend
6. **Redémarrez le serveur** avec les paramètres corrects
7. **Testez l'API indépendamment** avant d'essayer avec le frontend

Si vous suivez ces étapes méthodiquement, vous devriez pouvoir résoudre définitivement les problèmes que vous rencontrez.
