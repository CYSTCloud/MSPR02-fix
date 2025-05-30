# Liste des Livrables - EPIVIZ 4.1

## Introduction

Ce document récapitule l'ensemble des livrables produits dans le cadre du projet EPIVIZ 4.1. Il sert de guide pour l'assemblage final des documents, du code source, et des autres éléments à inclure dans la remise officielle.

## Structure des Livrables

### 1. Code Source

#### 1.1 Scripts d'Analyse et de Préparation des Données
- `feature_engineering.py` : Script de préparation des caractéristiques pour les modèles
- `data_exploration.py` : Script d'exploration et visualisation des données
- `generate_model_metrics.py` : Script de génération des métriques de comparaison des modèles

#### 1.2 Scripts d'Entraînement des Modèles
- `model_training.py` : Script principal d'entraînement des différents modèles

#### 1.3 API
- `/api/app.py` : Point d'entrée principal de l'API FastAPI
- `/api/config.py` : Configuration de l'API (host, port, chemins)
- `run_api.py` : Script de lancement de l'API

#### 1.4 Scripts de Test
- `test_api.py` : Tests complets de l'API
- `simple_test.py` : Tests simplifiés pour diagnostic rapide
- `test_models_endpoint.py` : Test spécifique pour l'endpoint des modèles

### 2. Données

#### 2.1 Données Brutes
- `data_to_train_covid19.csv` : Données brutes de COVID-19

#### 2.2 Données Prétraitées
- `/processed_data/` : Dossier contenant les données prétraitées par pays

#### 2.3 Données pour les Modèles
- `/model_data/` : Dossier contenant les données d'entraînement et de test par pays

### 3. Modèles Entraînés

- `/trained_models/` : Dossier contenant les modèles entraînés par pays
  - Sous-dossiers par pays (ex: `US/`, `Brazil/`, etc.)
  - Fichiers de modèles (`.pkl`)
  - Fichiers de comparaison des métriques (`models_comparison.csv`)
  - Visualisations des importances de caractéristiques (`.png`)

### 4. Documentation

#### 4.1 Documentation Technique
- `/documentation/api_documentation.md` : Documentation complète de l'API
- `/documentation/modeles_ia_documentation.md` : Documentation des modèles d'IA

#### 4.2 Documentation Utilisateur
- `/documentation/guide_utilisateur.md` : Guide d'utilisation pour les utilisateurs finaux

#### 4.3 Documentation de Gestion de Projet
- `/documentation/conduite_au_changement.md` : Rapport sur la conduite au changement
- `/documentation/verification_conformite_mspr.md` : Vérification de conformité avec la grille MSPR
- `/documentation/liste_livrables_finale.md` : Ce document (liste des livrables)

#### 4.4 Documentation de Développement
- `task_manager.md` : Suivi des tâches du projet
- `README.md` : Instructions générales d'installation et d'utilisation

## Checklist de Vérification

Avant la remise finale, vérifier que :

- [ ] Tous les fichiers de code sont présents et correctement commentés
- [ ] Les modèles entraînés sont disponibles pour tous les pays concernés
- [ ] Les fichiers de métriques des modèles sont générés pour tous les pays
- [ ] La documentation est complète et à jour
- [ ] Les tests passent avec succès
- [ ] Les dépendances sont clairement documentées (requirements.txt)
- [ ] L'API peut être lancée sans erreur
- [ ] Le rapport de conformité MSPR est à jour

## Procédure d'Assemblage

1. **Vérification du Code**
   - Exécuter tous les tests pour confirmer le bon fonctionnement
   - Vérifier la présence de tous les fichiers nécessaires

2. **Organisation des Dossiers**
   - S'assurer que la structure des dossiers est cohérente
   - Nettoyer les fichiers temporaires ou inutiles

3. **Création de l'Archive**
   - Créer une archive ZIP contenant tous les livrables
   - Structure recommandée pour l'archive :
     ```
     EPIVIZ_4.1/
     ├── api/
     ├── documentation/
     ├── model_data/
     ├── processed_data/
     ├── trained_models/
     ├── *.py (scripts à la racine)
     ├── requirements.txt
     └── README.md
     ```

4. **Vérification Finale**
   - Extraire l'archive dans un environnement propre
   - Tester l'installation et le fonctionnement selon les instructions du README
   - Vérifier que tous les documents sont accessibles et lisibles

## Instructions de Remise

- **Format** : Archive ZIP nommée `EPIVIZ_4.1_FINAL.zip`
- **Plateforme de remise** : [Plateforme de soumission de l'école]
- **Date limite** : [Date à préciser]
- **Contact en cas de problème** : [Email de contact]

## Conclusion

Cette liste des livrables fournit une vue d'ensemble complète de tous les éléments produits dans le cadre du projet EPIVIZ 4.1. Elle sert de guide pour l'assemblage final et la vérification avant remise officielle.

---

Document préparé par : Équipe Projet EPIVIZ 4.1  
Date : 30 Mai 2025  
Version : 1.0
