"""
Script simple pour vérifier l'état des données préparées
"""
import os
import sys

# Forcer l'affichage des prints
sys.stdout.reconfigure(encoding='utf-8')

print("=== VÉRIFICATION DES DONNÉES ===")

# Vérifier le dossier processed_data
processed_data_path = os.path.join(os.getcwd(), 'processed_data')
print(f"Dossier processed_data existe: {os.path.exists(processed_data_path)}")

if os.path.exists(processed_data_path):
    files = os.listdir(processed_data_path)
    print(f"Fichiers dans processed_data: {files}")
    
    # Vérifier le fichier CSV
    csv_path = os.path.join(processed_data_path, 'prepared_covid_data.csv')
    if os.path.exists(csv_path):
        print(f"Fichier CSV existe: {os.path.exists(csv_path)}")
        print(f"Taille du fichier: {os.path.getsize(csv_path)} octets")
        
        # Essayer de lire les premières lignes
        try:
            with open(csv_path, 'r') as f:
                print("Premières lignes du fichier:")
                for i, line in enumerate(f):
                    if i < 5:  # Afficher les 5 premières lignes
                        print(f"  {line.strip()}")
                    else:
                        break
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {str(e)}")
    else:
        print("Le fichier CSV n'existe pas!")

# Vérifier le dossier model_data
model_data_path = os.path.join(os.getcwd(), 'model_data')
print(f"\nDossier model_data existe: {os.path.exists(model_data_path)}")

if os.path.exists(model_data_path):
    files = os.listdir(model_data_path)
    print(f"Fichiers dans model_data: {files}")
else:
    print("Le dossier model_data n'existe pas ou est vide!")

print("\n=== FIN DE LA VÉRIFICATION ===")
