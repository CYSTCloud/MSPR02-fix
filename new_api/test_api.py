"""
Script de test pour vérifier les fonctionnalités de base de l'API EPIVIZ 4.1
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api_test")

# Vérifier que les dossiers requis existent
def check_directories():
    logger.info("Vérification des répertoires nécessaires...")
    
    # Vérifier le répertoire de données
    from core.config import Paths
    
    required_dirs = [
        Paths.ROOT_DIR,
        Paths.DATA_DIR, 
        Paths.MODELS_DIR
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            logger.warning(f"Le répertoire {dir_path} n'existe pas. Certaines fonctionnalités pourraient ne pas fonctionner.")
        else:
            logger.info(f"Répertoire {dir_path} trouvé.")
    
    # Vérifier si des fichiers de données existent
    data_files = list(Path(Paths.DATA_DIR).glob("*.csv"))
    if data_files:
        logger.info(f"Fichiers de données trouvés: {len(data_files)}")
        for file in data_files[:3]:  # Afficher jusqu'à 3 fichiers
            logger.info(f"  - {file.name}")
        if len(data_files) > 3:
            logger.info(f"  - ... et {len(data_files) - 3} autres")
    else:
        logger.warning("Aucun fichier de données CSV trouvé.")
    
    # Vérifier si des modèles existent
    model_files = []
    if Paths.MODELS_DIR.exists():
        model_files = list(Path(Paths.MODELS_DIR).glob("**/*.pkl"))
    
    if model_files:
        logger.info(f"Fichiers de modèle trouvés: {len(model_files)}")
        for file in model_files[:3]:  # Afficher jusqu'à 3 fichiers
            logger.info(f"  - {file.relative_to(Paths.MODELS_DIR)}")
        if len(model_files) > 3:
            logger.info(f"  - ... et {len(model_files) - 3} autres")
    else:
        logger.warning("Aucun fichier de modèle trouvé.")

# Tester le chargement des adaptateurs de données
def test_data_adapters():
    logger.info("Test des adaptateurs de données...")
    
    try:
        from data.adapters.enhanced_data import EnhancedDataAdapter
        from data.adapters.raw_data import RawDataAdapter
        from data.adapters.base import DataContext
        
        # Tester l'adaptateur de données améliorées
        enhanced_adapter = EnhancedDataAdapter()
        logger.info(f"Adaptateur de données améliorées initialisé: {enhanced_adapter.name}")
        
        # Tester l'adaptateur de données brutes
        raw_adapter = RawDataAdapter()
        logger.info(f"Adaptateur de données brutes initialisé: {raw_adapter.name}")
        
        # Créer un contexte minimal pour tester can_handle
        context = DataContext(required_columns=["country", "date_value"])
        
        logger.info(f"Adaptateur amélioré peut gérer le contexte: {enhanced_adapter.can_handle(context)}")
        logger.info(f"Adaptateur brut peut gérer le contexte: {raw_adapter.can_handle(context)}")
        
        logger.info("Test des adaptateurs de données réussi.")
    except Exception as e:
        logger.error(f"Erreur lors du test des adaptateurs de données: {e}")

# Tester le gestionnaire d'accès aux données
def test_data_manager():
    logger.info("Test du gestionnaire d'accès aux données...")
    
    try:
        from data.access.manager import data_manager
        
        # Obtenir la liste des pays disponibles
        countries = data_manager.get_available_countries()
        
        if countries:
            logger.info(f"Pays disponibles: {len(countries)}")
            logger.info(f"Exemples: {', '.join(countries[:5])} ...")
            
            # Tester avec un pays spécifique
            test_country = countries[0]
            logger.info(f"Test de récupération de données pour {test_country}...")
            
            try:
                data = data_manager.get_historical_data(country=test_country)
                logger.info(f"Données récupérées pour {test_country}: {len(data)} lignes")
                if not data.empty:
                    logger.info(f"Colonnes disponibles: {', '.join(data.columns)}")
                    logger.info(f"Plage de dates: {data['date_value'].min()} à {data['date_value'].max()}")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des données pour {test_country}: {e}")
        else:
            logger.warning("Aucun pays disponible dans les données.")
    except Exception as e:
        logger.error(f"Erreur lors du test du gestionnaire d'accès aux données: {e}")

# Tester le registre de modèles
def test_model_registry():
    logger.info("Test du registre de modèles...")
    
    try:
        from models.loaders.registry import model_registry
        
        # Obtenir la liste des pays avec modèles
        countries = model_registry.get_available_countries()
        
        if countries:
            logger.info(f"Pays avec modèles: {len(countries)}")
            logger.info(f"Exemples: {', '.join(countries[:5])} ...")
            
            # Tester avec un pays spécifique
            if countries:
                test_country = countries[0]
                logger.info(f"Test de récupération de modèles pour {test_country}...")
                
                try:
                    model_types = model_registry.get_available_model_types(test_country)
                    logger.info(f"Types de modèles disponibles pour {test_country}: {', '.join(model_types)}")
                    
                    if model_types:
                        test_model_type = model_types[0]
                        logger.info(f"Test de chargement du modèle {test_model_type} pour {test_country}...")
                        
                        try:
                            model = model_registry.get_model(test_country, test_model_type)
                            logger.info(f"Modèle {test_model_type} pour {test_country} chargé avec succès")
                        except Exception as e:
                            logger.error(f"Erreur lors du chargement du modèle {test_model_type} pour {test_country}: {e}")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des types de modèles pour {test_country}: {e}")
        else:
            logger.warning("Aucun pays avec modèles disponible.")
            
        # Tester les pays avec modèles améliorés
        enhanced_countries = model_registry.get_enhanced_countries()
        if enhanced_countries:
            logger.info(f"Pays avec modèles améliorés: {len(enhanced_countries)}")
            logger.info(f"Exemples: {', '.join(enhanced_countries[:5])} ...")
        else:
            logger.warning("Aucun pays avec modèles améliorés disponible.")
    except Exception as e:
        logger.error(f"Erreur lors du test du registre de modèles: {e}")

# Fonction principale
def main():
    logger.info("Démarrage des tests de l'API EPIVIZ 4.1")
    
    # Ajouter le répertoire courant au path
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        # Vérifier les répertoires
        check_directories()
        
        # Tester les adaptateurs de données
        test_data_adapters()
        
        # Tester le gestionnaire d'accès aux données
        test_data_manager()
        
        # Tester le registre de modèles
        test_model_registry()
        
        logger.info("Tests terminés avec succès")
    except Exception as e:
        logger.error(f"Erreur lors des tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
