"""
EPIVIZ 4.1 - Script de préparation de l'archive finale
------------------------------------------------------
Ce script prépare une archive ZIP contenant tous les livrables du projet
EPIVIZ 4.1, organisés selon la structure recommandée dans la documentation.
"""

import os
import zipfile
import shutil
import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
ARCHIVE_NAME = "EPIVIZ_4.1_FINAL.zip"

# Liste des dossiers à inclure
FOLDERS_TO_INCLUDE = [
    "api",
    "documentation",
    "model_data",
    "processed_data",
    "trained_models"
]

# Liste des fichiers Python à la racine à inclure
ROOT_PY_FILES = [
    "feature_engineering.py",
    "model_training.py",
    "run_api.py",
    "test_api.py",
    "simple_test.py",
    "test_models_endpoint.py",
    "generate_model_metrics.py",
]

# Autres fichiers importants
OTHER_FILES = [
    "README.md",
    "task_manager.md",
    "requirements.txt",
]

def create_requirements_txt():
    """Crée un fichier requirements.txt si nécessaire"""
    req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
    
    if not os.path.exists(req_path):
        print("Création du fichier requirements.txt...")
        
        with open(req_path, 'w') as f:
            f.write("""# EPIVIZ 4.1 - Dépendances
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.2
pandas>=1.3.3
numpy>=1.21.2
scikit-learn>=0.24.2
xgboost>=1.4.2
tensorflow>=2.6.0
matplotlib>=3.4.3
seaborn>=0.11.2
joblib>=1.0.1
requests>=2.26.0
python-multipart>=0.0.5
aiofiles>=0.7.0
""")
        print("✅ requirements.txt créé avec succès.")
    else:
        print("✅ requirements.txt existe déjà.")
    
    return req_path

def create_readme_if_missing():
    """Crée un fichier README.md si nécessaire"""
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    
    if not os.path.exists(readme_path):
        print("Création du fichier README.md...")
        
        with open(readme_path, 'w') as f:
            f.write("""# EPIVIZ 4.1

## API de prédiction des cas de COVID-19

EPIVIZ 4.1 est une API permettant de prédire l'évolution des cas de COVID-19 pour différents pays, basée sur des modèles de machine learning entraînés sur des données historiques.

## Installation

1. Clonez ce dépôt
2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

## Utilisation

### Lancement de l'API

```
python run_api.py
```

L'API sera accessible à l'adresse http://127.0.0.1:8000

### Documentation interactive

La documentation interactive de l'API est disponible à l'adresse :
http://127.0.0.1:8000/docs

### Endpoints principaux

- `/api/countries` : Liste des pays disponibles
- `/api/predict/{country}` : Prédiction des cas pour un pays
- `/api/historical/{country}` : Données historiques pour un pays
- `/api/compare` : Comparaison entre pays
- `/api/models/{country}` : Métriques des modèles pour un pays

## Documentation

La documentation complète du projet est disponible dans le dossier `documentation/` :

- `api_documentation.md` : Documentation technique de l'API
- `modeles_ia_documentation.md` : Documentation des modèles IA
- `guide_utilisateur.md` : Guide utilisateur
- `conduite_au_changement.md` : Rapport sur la conduite au changement

## Tests

Pour tester l'API, exécutez :

```
python test_api.py
```

Pour un test simplifié :

```
python simple_test.py
```

## Licence

© 2025 - EPIVIZ Project Team - Tous droits réservés
""")
        print("✅ README.md créé avec succès.")
    else:
        print("✅ README.md existe déjà.")
    
    return readme_path

def prepare_archive():
    """Prépare l'archive ZIP avec tous les livrables"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(OUTPUT_DIR, f"{timestamp}_{ARCHIVE_NAME}")
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Préparation de l'archive ZIP : {archive_path}")
    
    # Créer les fichiers manquants si nécessaire
    req_path = create_requirements_txt()
    readme_path = create_readme_if_missing()
    
    # Créer l'archive ZIP
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter les dossiers
        for folder in FOLDERS_TO_INCLUDE:
            folder_path = os.path.join(PROJECT_ROOT, folder)
            if os.path.exists(folder_path):
                print(f"Ajout du dossier : {folder}")
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, PROJECT_ROOT)
                        zipf.write(file_path, arcname)
            else:
                print(f"⚠️ Dossier non trouvé : {folder}")
        
        # Ajouter les fichiers Python à la racine
        for py_file in ROOT_PY_FILES:
            file_path = os.path.join(PROJECT_ROOT, py_file)
            if os.path.exists(file_path):
                print(f"Ajout du fichier : {py_file}")
                zipf.write(file_path, py_file)
            else:
                print(f"⚠️ Fichier non trouvé : {py_file}")
        
        # Ajouter les autres fichiers importants
        for other_file in OTHER_FILES:
            file_path = os.path.join(PROJECT_ROOT, other_file)
            if os.path.exists(file_path):
                print(f"Ajout du fichier : {other_file}")
                zipf.write(file_path, other_file)
            else:
                print(f"⚠️ Fichier non trouvé : {other_file}")
    
    print(f"\n✅ Archive créée avec succès : {archive_path}")
    print(f"Taille de l'archive : {os.path.getsize(archive_path) / (1024*1024):.2f} Mo")
    
    return archive_path

def verify_archive(archive_path):
    """Vérifie le contenu de l'archive créée"""
    print("\nVérification du contenu de l'archive :")
    
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        files = zipf.namelist()
        
        # Vérifier les dossiers principaux
        for folder in FOLDERS_TO_INCLUDE:
            if any(f.startswith(folder+'/') for f in files):
                print(f"✅ Dossier {folder} présent")
            else:
                print(f"❌ Dossier {folder} manquant")
        
        # Vérifier les fichiers Python à la racine
        for py_file in ROOT_PY_FILES:
            if py_file in files:
                print(f"✅ Fichier {py_file} présent")
            else:
                print(f"❌ Fichier {py_file} manquant")
        
        # Vérifier les autres fichiers importants
        for other_file in OTHER_FILES:
            if other_file in files:
                print(f"✅ Fichier {other_file} présent")
            else:
                print(f"❌ Fichier {other_file} manquant")
        
        # Afficher le nombre total de fichiers
        print(f"\nNombre total de fichiers dans l'archive : {len(files)}")

def main():
    """Fonction principale"""
    print("=== PRÉPARATION DE L'ARCHIVE FINALE - EPIVIZ 4.1 ===\n")
    
    # Préparer l'archive
    archive_path = prepare_archive()
    
    # Vérifier l'archive
    verify_archive(archive_path)
    
    print("\n=== PRÉPARATION TERMINÉE ===")
    print(f"L'archive est prête à être soumise : {archive_path}")

if __name__ == "__main__":
    main()
