"""
Script pour créer le répertoire de données améliorées s'il n'existe pas
"""

import os
import shutil

# Chemin du répertoire principal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin du répertoire de données améliorées
ENHANCED_DATA_PATH = os.path.join(BASE_DIR, 'enhanced_data')

def create_enhanced_data_directory():
    """
    Crée le répertoire de données améliorées s'il n'existe pas
    et copie les données améliorées si elles existent
    """
    # Créer le répertoire s'il n'existe pas
    if not os.path.exists(ENHANCED_DATA_PATH):
        print(f"Création du répertoire pour les données améliorées: {ENHANCED_DATA_PATH}")
        os.makedirs(ENHANCED_DATA_PATH)
    else:
        print(f"Le répertoire pour les données améliorées existe déjà: {ENHANCED_DATA_PATH}")
    
    # Vérifier si le fichier de données améliorées existe
    enhanced_csv = os.path.join(BASE_DIR, 'data_to_train_covid19_enhanced.csv')
    if os.path.exists(enhanced_csv):
        # Copier le fichier dans le répertoire des données améliorées
        target_path = os.path.join(ENHANCED_DATA_PATH, 'data_to_train_covid19_enhanced.csv')
        if not os.path.exists(target_path):
            print(f"Copie de {enhanced_csv} vers {target_path}")
            shutil.copy2(enhanced_csv, target_path)
        else:
            print(f"Le fichier {target_path} existe déjà")
    else:
        print(f"Le fichier de données améliorées {enhanced_csv} n'existe pas encore")
        print("Exécutez enhance_source_data.py pour générer les données améliorées")

if __name__ == "__main__":
    create_enhanced_data_directory()
