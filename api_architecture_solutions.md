# Architecture Avancée d'API pour EPIVIZ 4.1
*Document technique détaillant les solutions architecturales pour l'API de prédiction épidémiologique*

## Table des matières
1. [Architecture Générale](#architecture-générale)
2. [Gestion des Données](#gestion-des-données)
3. [Intégration des Modèles d'IA](#intégration-des-modèles-dia)
4. [Protocoles de Communication](#protocoles-de-communication)
5. [Stratégies de Traitement des Erreurs](#stratégies-de-traitement-des-erreurs)
6. [Optimisation des Performances](#optimisation-des-performances)
7. [Journalisation et Monitoring](#journalisation-et-monitoring)
8. [Plan d'Implémentation](#plan-dimplémentation)

## Architecture Générale

### Analyse Comparative des Frameworks

| Framework | Forces | Limitations | Adaptation à EPIVIZ 4.1 |
|-----------|--------|-------------|-------------------------|
| **FastAPI** | Asynchrone, haute performance, documentation automatique | Écosystème plus récent | ★★★★★ - Optimal pour données volumineuses/temps réel |
| **Flask** | Léger, flexible, large écosystème | Synchrone par défaut | ★★★★☆ - Bon pour prototypage rapide |
| **Django REST** | Robuste, complet, ORM puissant | Plus lourd, courbe d'apprentissage | ★★★☆☆ - Trop complexe pour notre cas d'usage |
| **Express.js** | Haute performance JS, non-bloquant | Nécessite pont Python-JS | ★★☆☆☆ - Complexité d'intégration avec modèles Python |

### Architecture Recommandée: FastAPI avec Structure Modulaire Multicouche

```
api/
├── core/
│   ├── config.py            # Configuration centralisée et paramètres
│   ├── exceptions.py        # Gestionnaires d'exceptions personnalisés
│   └── logging_config.py    # Configuration avancée des logs
├── data/
│   ├── access/              # Couche d'accès aux données
│   ├── adapters/            # Adaptateurs pour sources multiples
│   ├── processors/          # Transformations et nettoyage
│   └── validators/          # Validation structurelle
├── models/
│   ├── loaders/             # Chargeurs dynamiques de modèles
│   ├── predictors/          # Prédicteurs par type de modèle
│   ├── evaluators/          # Évaluation et métriques
│   └── fallbacks/           # Stratégies de repli
├── routes/
│   ├── historical.py        # Endpoints données historiques
│   ├── predictions.py       # Endpoints prédictions
│   ├── metrics.py           # Endpoints métriques
│   └── comparison.py        # Endpoints comparaison
├── services/                # Orchestration des opérations
├── utils/                   # Utilitaires transversaux
├── main.py                  # Point d'entrée
└── middlewares.py           # Middlewares personnalisés
```

## Gestion des Données

### Système de Chargement de Données Multi-niveaux

Mise en place d'un système hiérarchique de chargement qui maintient la sophistication de l'architecture actuelle:

1. **Couche d'Accès Abstraite** 
   - Interface unifiée masquant l'hétérogénéité des sources
   - Adaptateurs spécifiques par source

2. **Hiérarchie de Chargement**:
   ```python
   class DataLoadingStrategy:
       def __init__(self, strategies=None):
           self.strategies = strategies or [
               EnhancedDataLoader(priority=100),
               ProcessedDataLoader(priority=90),
               RawDataLoader(priority=80),
               SimulatedDataGenerator(priority=70)
           ]
       
       def load_data(self, context):
           # Tentera chaque stratégie par ordre de priorité
           for strategy in sorted(self.strategies, key=lambda s: s.priority, reverse=True):
               try:
                   if strategy.can_handle(context):
                       data = strategy.load(context)
                       if self._validate_data(data):
                           return self._post_process(data)
               except Exception as e:
                   # Journaliser mais continuer avec stratégie suivante
                   logger.error(f"Échec {strategy.__class__.__name__}: {e}")
           
           # Stratégie de dernier recours - simulation
           return SimulatedDataGenerator().generate(context)
   ```

3. **Validation Structurelle Avancée**
   - Vérification dynamique de schéma
   - Détection intelligente des colonnes manquantes
   - Réparation automatique des données structurellement incorrectes

4. **Adaptateurs Spécialisés**
   - Adaptateur pour fichiers enhanced_data/*.csv
   - Adaptateur pour données historiques
   - Adaptateur pour données de modèle
   - Générateur de données simulées avancé

## Intégration des Modèles d'IA

### Système de Chargement Dynamique des Modèles

```python
class ModelRegistry:
    def __init__(self):
        self.registry = {}
        self.fallback_generators = {}
        self._discover_models()
    
    def _discover_models(self):
        """Découvre et enregistre automatiquement tous les modèles disponibles."""
        for country_dir in os.listdir(MODELS_PATH):
            country_path = os.path.join(MODELS_PATH, country_dir)
            if os.path.isdir(country_path):
                self.registry[country_dir] = {}
                for model_file in os.listdir(country_path):
                    if model_file.endswith('.pkl'):
                        model_type = model_file.split('.')[0]
                        self.registry[country_dir][model_type] = os.path.join(country_path, model_file)
    
    def get_model(self, country, model_type="xgboost"):
        """Récupère un modèle avec stratégie de repli sophistiquée."""
        try:
            if country in self.registry and model_type in self.registry[country]:
                model_path = self.registry[country][model_type]
                return self._load_model(model_path, model_type)
            
            # Stratégies de repli sophistiquées
            if model_type == "enhanced" and "lstm" in self.registry.get(country, {}):
                return self._load_model(self.registry[country]["lstm"], "lstm")
            
            if model_type == "xgboost" and "gradient_boosting" in self.registry.get(country, {}):
                return self._load_model(self.registry[country]["gradient_boosting"], "gradient_boosting")
            
            # Génération d'un modèle de repli approprié
            return self._generate_fallback_model(country, model_type)
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle {model_type} pour {country}: {e}")
            return self._generate_fallback_model(country, model_type)
```

### Stratégies Avancées de Prédiction

1. **Gestion des Contextes de Prédiction**
   - Support pour différents horizons temporels
   - Incorporation de facteurs externes (vaccination, restrictions)
   - Mécanismes d'extrapolation sophistiqués

2. **Système d'Ensemble de Prédicteurs**
   - Combinaison pondérée des prédictions de plusieurs modèles
   - Méta-prédicteur sélectionnant le meilleur modèle selon le contexte
   - Réduction de variance par techniques d'ensemble

3. **Traitement Post-prédiction**
   - Lissage des prédictions pour cohérence temporelle
   - Calibration de probabilité pour les incertitudes
   - Validation des contraintes épidémiologiques

## Protocoles de Communication

### Configuration CORS Optimisée

```python
# Configuration sophistiquée et sécurisée de CORS
cors_middleware = CORSMiddleware(
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://epiviz-production.domain.com"
    ],
    allow_origin_regex=r"https://epiviz-.*\.domain\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Authorization", "Content-Type", "Accept", "Origin", 
        "User-Agent", "DNT", "Cache-Control", "X-Mx-ReqToken", 
        "Keep-Alive", "X-Requested-With", "If-Modified-Since",
        "X-CSRF-Token", "X-Custom-Header"
    ],
    expose_headers=[
        "Content-Length", "X-Pagination", "X-RateLimit-Limit",
        "X-RateLimit-Remaining", "X-RateLimit-Reset"
    ],
    max_age=600,  # 10 minutes
)
```

### Architecture d'Endpoints

Structure d'API RESTful hiérarchique avec support pour versionnement:

```
/api/v1/
├── historical/
│   ├── {country}                       # Données historiques par pays
│   ├── {country}/between/{start}/{end} # Données par intervalle
│   └── compare                         # Comparaison entre pays
├── models/
│   ├── list                            # Liste des modèles disponibles
│   ├── {country}/metrics               # Métriques par pays
│   └── compare                         # Comparaison des modèles
└── predict/
    ├── {country}                       # Prédictions standard
    ├── enhanced/{country}              # Prédictions améliorées
    └── scenarios                       # Prédictions par scénario
```

## Stratégies de Traitement des Erreurs

### Gestionnaires d'Exceptions Multiniveaux

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire sophistiqué pour les exceptions HTTP."""
    logger.error(f"[HTTPException] {exc.status_code} at {request.url}: {exc.detail}")
    
    # Contexte étendu pour le diagnostic
    context = {
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url),
        "method": request.method,
        "client_ip": request.client.host,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "error_type": "http_exception",
        "error_code": exc.status_code,
        "error_detail": exc.detail
    }
    
    # Journalisation structurée pour analyse ultérieure
    logger.error("Exception détaillée", extra={"context": context})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": context["timestamp"],
            "path": context["path"],
            "status": "error",
            "error_code": exc.status_code,
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Gestionnaire pour toutes les exceptions non gérées."""
    # Code détaillé de traitement des exceptions génériques
    # ...
```

### Middleware de Récupération et Stabilité

```python
@app.middleware("http")
async def stability_middleware(request: Request, call_next):
    """Middleware assurant la stabilité de l'API même en cas d'erreur."""
    # Générer un ID de requête unique pour traçabilité
    request.state.request_id = str(uuid.uuid4())
    
    try:
        # Tentative normale de traitement
        response = await call_next(request)
        return response
    except Exception as e:
        # Capture de toutes les exceptions non gérées
        logger.critical(
            f"Exception non gérée dans le middleware: {str(e)}",
            exc_info=True,
            extra={"request_id": request.state.request_id}
        )
        
        # Réponse dégradée mais fonctionnelle
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erreur interne du serveur",
                "status": "error",
                "request_id": request.state.request_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
```

## Optimisation des Performances

### Stratégies de Mise en Cache

1. **Cache Hiérarchique Multi-niveaux**
   - Cache en mémoire pour requêtes fréquentes (données historiques populaires)
   - Cache Redis pour données partagées entre instances
   - Cache de modèles pour éviter rechargements coûteux

```python
class HierarchicalCache:
    """Système de cache hiérarchique optimisé pour les données épidémiologiques."""
    
    def __init__(self):
        # Cache en mémoire - rapide mais limité
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes
        
        # Cache Redis pour données partagées
        self.redis_cache = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Cache de fichiers pour données volumineuses
        self.file_cache_dir = os.path.join(tempfile.gettempdir(), "epiviz_cache")
        os.makedirs(self.file_cache_dir, exist_ok=True)
    
    async def get(self, key, level="auto"):
        """Récupère une donnée du cache avec stratégie intelligente."""
        # Logique sophistiquée de récupération adaptative selon niveau
```

### Optimisations de Requêtes

1. **Récupération Partielle et Pagination Avancée**
   ```python
   @app.get("/api/historical/{country}")
   async def get_historical_data(
       country: str,
       start_date: Optional[str] = None,
       end_date: Optional[str] = None,
       page: int = Query(1, ge=1),
       page_size: int = Query(100, ge=1, le=1000),
       fields: str = Query("date,total_cases,new_cases,total_deaths,new_deaths")
   ):
       """Récupération optimisée des données historiques avec support de pagination et champs sélectifs."""
       # Chargement optimisé uniquement des données nécessaires
       data = await data_service.get_historical(
           country=country,
           start_date=start_date,
           end_date=end_date,
           fields=fields.split(",")
       )
       
       # Pagination sophistiquée
       total_items = len(data)
       total_pages = math.ceil(total_items / page_size)
       start_idx = (page - 1) * page_size
       end_idx = start_idx + page_size
       paginated_data = data[start_idx:end_idx]
       
       # Métadonnées de pagination pour le client
       return {
           "country": country,
           "data": paginated_data,
           "pagination": {
               "page": page,
               "page_size": page_size,
               "total_items": total_items,
               "total_pages": total_pages,
               "has_next": page < total_pages,
               "has_prev": page > 1
           },
           "fields": fields.split(",")
       }
   ```

## Journalisation et Monitoring

### Configuration de Journalisation Avancée

```python
def setup_logging(log_level=logging.INFO):
    """Configure un système de journalisation sophistiqué."""
    # Configuration de base
    logging.basicConfig(level=log_level)
    
    # Formatter avancé avec contexte
    formatter = logging.Formatter(
        '%(asctime)s - %(process)d - %(thread)d - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler pour fichier rotatif
    file_handler = RotatingFileHandler(
        filename="api_logs.log",
        maxBytes=10_000_000,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Handler pour erreurs critiques (notification)
    critical_handler = logging.StreamHandler()
    critical_handler.setLevel(logging.ERROR)
    critical_handler.setFormatter(formatter)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(critical_handler)
    
    # Configuration spécifique pour nos modules
    api_logger = logging.getLogger("epiviz_api")
    api_logger.setLevel(log_level)
    
    # Désactiver propagation pour certains loggers bruyants
    logging.getLogger("uvicorn.access").propagate = False
```

### Intégration de Métriques

```python
# Middleware pour collecter des métriques de performance
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collecte des métriques sophistiquées sur les performances de l'API."""
    # Enregistrer l'heure de début
    start_time = time.time()
    
    # Extraire des informations sur la requête
    path = request.url.path
    method = request.method
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer la durée et enregistrer les métriques
    duration = time.time() - start_time
    status_code = response.status_code
    
    # Enregistrer dans des métriques structurées
    REQUESTS_COUNT.labels(
        method=method,
        path=path,
        status=status_code
    ).inc()
    
    REQUESTS_DURATION.labels(
        method=method,
        path=path,
        status=status_code
    ).observe(duration)
    
    # Ajouter des en-têtes de diagnostic
    response.headers["X-Response-Time"] = str(duration)
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
    
    return response
```

## Plan d'Implémentation

### Séquence de Migration

1. **Phase 1 : Architecture Fondationnelle (Semaine 1)**
   - Mise en place de la structure de modules
   - Configuration de l'environnement et dépendances
   - Implémentation du système de journalisation

2. **Phase 2 : Couche Données (Semaine 2)**
   - Développement des adaptateurs de données
   - Implémentation du système de chargement hiérarchique
   - Tests unitaires pour la validation des données

3. **Phase 3 : Intégration des Modèles (Semaine 2-3)**
   - Mise en place du registre de modèles
   - Développement des prédicteurs sophistiqués
   - Implémentation des stratégies de repli

4. **Phase 4 : API et Endpoints (Semaine 3-4)**
   - Développement des routes RESTful
   - Configuration CORS et middlewares
   - Tests d'intégration

5. **Phase 5 : Optimisation et Monitoring (Semaine 4)**
   - Implémentation du système de cache
   - Mise en place des métriques
   - Tests de charge et optimisations finales

### Stratégie de Test

Approche de test multicouche:

1. **Tests Unitaires** - Validation des composants individuels
2. **Tests d'Intégration** - Validation des interactions entre composants
3. **Tests de Bout en Bout** - Validation des scénarios utilisateur complets
4. **Tests de Charge** - Validation des performances sous charge

### Considérations de Déploiement

1. **Stratégie de Conteneurisation**
   - Images Docker optimisées
   - Déploiement Kubernetes pour haute disponibilité

2. **Configuration CI/CD**
   - Intégration et déploiement continus
   - Tests automatisés à chaque commit

3. **Monitoring en Production**
   - Intégration avec Prometheus/Grafana
   - Alertes sur métriques critiques
