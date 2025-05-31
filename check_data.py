import os
import sys

# Ensure print statements are displayed correctly
sys.stdout.reconfigure(encoding='utf-8')

print("=== SCRIPT DE VÉRIFICATION DE L'ENVIRONNEMENT DE DONNÉES ===")

# 1. Define BASE_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Répertoire de base du projet (BASE_DIR): {BASE_DIR}")

# 2. Define all relevant path variables
DATA_PATH_ROOT = os.path.join(BASE_DIR, 'data_to_train_covid19.csv')
DATA_PATH_DATA_DIR = os.path.join(BASE_DIR, 'data', 'data_to_train_covid19.csv')
MODELS_PATH = os.path.join(BASE_DIR, 'trained_models')
PROCESSED_DATA_PATH_DIR = os.path.join(BASE_DIR, 'processed_data')
PROCESSED_DATA_FILE = os.path.join(PROCESSED_DATA_PATH_DIR, 'prepared_covid_data.csv')
MODEL_DATA_PATH_DIR = os.path.join(BASE_DIR, 'model_data')
ENHANCED_DATA_PATH_DIR = os.path.join(BASE_DIR, 'enhanced_data')

issues_found = []

print("\n--- Vérification des répertoires ---")
# 3. Create a list of required directories
required_directories = [
    MODELS_PATH,
    PROCESSED_DATA_PATH_DIR,
    MODEL_DATA_PATH_DIR,
    ENHANCED_DATA_PATH_DIR
]

# 4. Iterate through the required directories
for dir_path in required_directories:
    dir_name = os.path.basename(dir_path)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"[OK] Répertoire '{dir_name}' trouvé à: {dir_path}")
    else:
        message = f"[MANQUANT] Répertoire '{dir_name}' non trouvé à: {dir_path}"
        print(message)
        issues_found.append(message)
        print(f"  -> Suggestion: Créez ce répertoire ou exécutez les scripts de traitement de données appropriés (ex: data_processing.py, model_training.py).")

print("\n--- Vérification des fichiers de données principaux ---")
# 5. Specifically check for the main data file
main_data_found = False
main_data_location = ""
if os.path.exists(DATA_PATH_ROOT) and os.path.isfile(DATA_PATH_ROOT):
    main_data_found = True
    main_data_location = DATA_PATH_ROOT
    print(f"[OK] Fichier de données principal 'data_to_train_covid19.csv' trouvé à: {DATA_PATH_ROOT}")
elif os.path.exists(DATA_PATH_DATA_DIR) and os.path.isfile(DATA_PATH_DATA_DIR):
    main_data_found = True
    main_data_location = DATA_PATH_DATA_DIR
    print(f"[OK] Fichier de données principal 'data_to_train_covid19.csv' trouvé dans le sous-répertoire 'data' à: {DATA_PATH_DATA_DIR}")
else:
    message = "[MANQUANT] Fichier de données principal 'data_to_train_covid19.csv' non trouvé."
    print(message)
    print(f"  Chemins vérifiés: {DATA_PATH_ROOT} ET {DATA_PATH_DATA_DIR}")
    issues_found.append(message)
    print(f"  -> Suggestion: Assurez-vous que 'data_to_train_covid19.csv' est présent à la racine du projet ou dans un sous-répertoire 'data'.")

# 6. Specifically check for PROCESSED_DATA_FILE
print("\n--- Vérification du fichier de données traitées ---")
if os.path.exists(PROCESSED_DATA_FILE) and os.path.isfile(PROCESSED_DATA_FILE):
    file_size = os.path.getsize(PROCESSED_DATA_FILE)
    print(f"[OK] Fichier de données traitées 'prepared_covid_data.csv' trouvé à: {PROCESSED_DATA_FILE}")
    print(f"  Taille du fichier: {file_size} octets ({file_size / (1024*1024):.2f} MB)")
    if file_size == 0:
        message = f"[AVERTISSEMENT] Le fichier de données traitées '{PROCESSED_DATA_FILE}' est vide (0 octets)."
        print(message)
        issues_found.append(message)
        print(f"  -> Suggestion: Vérifiez le script 'data_processing.py' pour vous assurer qu'il génère correctement les données.")

else:
    message = f"[MANQUANT] Fichier de données traitées 'prepared_covid_data.csv' non trouvé à: {PROCESSED_DATA_FILE}"
    print(message)
    issues_found.append(message)
    print(f"  -> Suggestion: Exécutez le script 'data_processing.py' pour générer ce fichier.")

# 7. List contents of key directories if they exist
print("\n--- Contenu des répertoires de modèles et de données spécifiques ---")

def list_directory_contents(dir_path, dir_desc):
    dir_name = os.path.basename(dir_path)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"Contenu du répertoire '{dir_name}' ({dir_desc}) à {dir_path}:")
        contents = os.listdir(dir_path)
        if contents:
            for item in contents:
                print(f"  - {item}")
            if not any(item.endswith(('.pkl', '.h5', '.keras', '.csv', '.json')) for item in contents): # Check for typical model/data files
                 print(f"  (Note: Aucun fichier de modèle ou de données commun détecté directement dans ce répertoire.)")
        else:
            print(f"  Le répertoire '{dir_name}' est vide.")
    else:
        # This case is already handled by the directory check, but we can add a note here if needed
        print(f"Répertoire '{dir_name}' ({dir_desc}) non trouvé ou n'est pas un répertoire.")


list_directory_contents(MODELS_PATH, "modèles entraînés")
list_directory_contents(MODEL_DATA_PATH_DIR, "données spécifiques aux modèles")
list_directory_contents(ENHANCED_DATA_PATH_DIR, "données améliorées")


# 8. & 9. Print summary and exit
print("\n--- RÉSUMÉ DE LA VÉRIFICATION ---")
if issues_found:
    print("[ERREUR] Des problèmes ont été détectés dans l'environnement de données:")
    for issue in issues_found:
        print(f"  - {issue}")
    print("\nSuggestions générales:")
    print("  - Assurez-vous d'avoir téléchargé toutes les données nécessaires.")
    print("  - Exécutez les scripts de prétraitement des données (ex: 'data_processing.py').")
    print("  - Exécutez les scripts d'entraînement des modèles (ex: 'model_training.py').")
    print("Veuillez corriger les problèmes listés ci-dessus.")
    sys.exit(1)
else:
    print("[SUCCÈS] L'environnement de données semble être correctement configuré!")
    print("  - Tous les répertoires requis sont présents.")
    print("  - Le fichier de données principal et le fichier de données traitées ont été trouvés (vérifiez la taille et le contenu si nécessaire).")
    print("  - Le contenu des répertoires de modèles a été listé (vérifiez la présence des fichiers attendus).")
    sys.exit(0)
