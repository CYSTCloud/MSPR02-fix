"""
EPIVIZ 4.1 - Configuration de l'API
----------------------------------
Ce fichier contient les paramètres de configuration pour l'API EPIVIZ.
"""

import os

# Répertoire de base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chemins des fichiers et dossiers
DATA_PATH = os.path.join(BASE_DIR, 'data_to_train_covid19.csv')
MODELS_PATH = os.path.join(BASE_DIR, 'trained_models')
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'processed_data', 'prepared_covid_data.csv')
MODEL_DATA_PATH = os.path.join(BASE_DIR, 'model_data')
LOGS_PATH = os.path.join(BASE_DIR, 'logs')

# Créer le dossier de logs s'il n'existe pas
if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH)

# Configuration de l'API
API_HOST = "127.0.0.1"
API_PORT = 8000
API_DEBUG = True

# Configuration des CORS
CORS_ORIGINS = ["*"]  # En production, limitez cette liste aux domaines autorisés
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
