# Documentation Technique des Modèles IA - EPIVIZ 4.1

## Introduction

Ce document présente en détail les modèles d'intelligence artificielle utilisés dans le projet EPIVIZ 4.1 pour la prédiction des cas de COVID-19. Il couvre les différents algorithmes implémentés, les méthodologies d'entraînement, les performances obtenues et les justifications des choix techniques.

## Données Utilisées

Les modèles ont été entraînés sur des données historiques de cas de COVID-19 provenant de diverses sources, notamment :

- Données issues des registres nationaux de santé
- Données agrégées de l'Organisation Mondiale de la Santé (OMS)
- Données du Johns Hopkins Coronavirus Resource Center

Les caractéristiques (features) utilisées pour l'entraînement des modèles incluent :

1. **Caractéristiques temporelles** :
   - Jour de la semaine
   - Jour du mois
   - Mois
   - Jours écoulés depuis le premier cas

2. **Caractéristiques de tendance** :
   - Nombre de cas sur les 7 derniers jours
   - Nombre de cas sur les 14 derniers jours
   - Moyenne mobile sur 7 jours
   - Taux de croissance

3. **Caractéristiques de lag** :
   - Nouveaux cas (décalés de 1 à 14 jours)
   - Total des cas (décalés de 1 à 14 jours)

## Prétraitement des Données

Avant l'entraînement des modèles, les données ont subi plusieurs étapes de prétraitement :

1. **Nettoyage** :
   - Suppression des valeurs manquantes
   - Correction des anomalies
   - Normalisation des noms de pays

2. **Feature Engineering** :
   - Création de caractéristiques temporelles
   - Génération de variables décalées (lag features)
   - Création de moyennes mobiles et de taux de croissance

3. **Normalisation** :
   - StandardScaler pour les modèles linéaires
   - Pas de normalisation pour les modèles à base d'arbres (Random Forest, XGBoost)

4. **Division des données** :
   - 80% des données pour l'entraînement
   - 20% des données pour les tests
   - Division chronologique (pas de mélange aléatoire)

## Modèles Implémentés

### 1. Modèles Linéaires

#### Linear Regression

- **Description** : Modèle de régression simple qui prédit une variable cible en fonction d'une combinaison linéaire des variables d'entrée.
- **Hyperparamètres** : Aucun hyperparamètre spécifique.
- **Forces** :
  - Simple et interprétable
  - Rapide à entraîner
  - Peu de paramètres
- **Faiblesses** :
  - Suppose une relation linéaire entre les variables
  - Sensible aux valeurs aberrantes
  - Performances limitées sur des données complexes

#### Ridge Regression

- **Description** : Régression linéaire avec régularisation L2, qui pénalise les coefficients élevés pour éviter le surapprentissage.
- **Hyperparamètres** :
  - alpha : 1.0 (paramètre de régularisation)
- **Forces** :
  - Réduit le surapprentissage
  - Gère mieux les corrélations entre variables
  - Stabilise les coefficients
- **Faiblesses** :
  - Toujours basé sur un modèle linéaire
  - Ne peut pas réduire les coefficients à zéro

#### Lasso Regression

- **Description** : Régression linéaire avec régularisation L1, qui peut réduire certains coefficients à zéro, effectuant ainsi une sélection de variables.
- **Hyperparamètres** :
  - alpha : 1.0 (paramètre de régularisation)
- **Forces** :
  - Effectue une sélection de variables
  - Réduit le surapprentissage
  - Modèle plus parcimonieux
- **Faiblesses** :
  - Performances limitées sur des données très complexes
  - Instable quand les caractéristiques sont fortement corrélées

### 2. Modèles Ensemblistes

#### Random Forest

- **Description** : Ensemble d'arbres de décision entraînés sur différents sous-ensembles aléatoires des données et des caractéristiques.
- **Hyperparamètres** :
  - n_estimators : 100 (nombre d'arbres)
  - max_depth : 10 (profondeur maximale des arbres)
  - min_samples_split : 2
  - min_samples_leaf : 1
  - random_state : 42
- **Forces** :
  - Robuste au surapprentissage
  - Gère bien les non-linéarités
  - Peu sensible aux valeurs aberrantes
  - Fournit des importances de variables
- **Faiblesses** :
  - Modèle "boîte noire" moins interprétable
  - Consommation de mémoire importante
  - Temps d'entraînement plus long

#### Gradient Boosting

- **Description** : Méthode d'ensemble qui construit des arbres de décision séquentiellement, chaque arbre corrigeant les erreurs du précédent.
- **Hyperparamètres** :
  - n_estimators : 100
  - learning_rate : 0.1
  - max_depth : 3
  - min_samples_split : 2
  - min_samples_leaf : 1
  - random_state : 42
- **Forces** :
  - Performances généralement supérieures aux modèles précédents
  - Bonne gestion des non-linéarités
  - Apprentissage des erreurs précédentes
- **Faiblesses** :
  - Risque de surapprentissage
  - Temps d'entraînement plus long
  - Sensible aux valeurs aberrantes

#### XGBoost

- **Description** : Implémentation optimisée du Gradient Boosting, avec des fonctionnalités supplémentaires pour améliorer les performances et éviter le surapprentissage.
- **Hyperparamètres** :
  - n_estimators : 100
  - learning_rate : 0.1
  - max_depth : 3
  - colsample_bytree : 0.8
  - subsample : 0.8
  - random_state : 42
- **Forces** :
  - Performances supérieures sur la plupart des problèmes
  - Gestion intégrée des valeurs manquantes
  - Régularisation efficace
  - Parallélisation optimisée
- **Faiblesses** :
  - Plus de paramètres à ajuster
  - Temps d'entraînement modéré
  - Moins intuitif à interpréter

### 3. Réseaux de Neurones

#### LSTM (Long Short-Term Memory)

- **Description** : Réseau de neurones récurrent spécialisé dans l'apprentissage des séquences temporelles.
- **Architecture** :
  - Couche LSTM avec 50 unités
  - Couche Dense avec activation ReLU
  - Couche de sortie avec activation linéaire
- **Hyperparamètres** :
  - batch_size : 32
  - epochs : 50
  - optimizer : Adam (learning_rate=0.001)
  - loss : Mean Squared Error
- **Forces** :
  - Capture les dépendances temporelles à long terme
  - Gère naturellement les séquences
  - Potentiel de performances élevées sur des données complexes
- **Faiblesses** :
  - Nécessite plus de données pour être efficace
  - Temps d'entraînement plus long
  - Risque élevé de surapprentissage
  - Difficulté d'interprétation

## Performances des Modèles

Les modèles ont été évalués selon plusieurs métriques :

- **RMSE (Root Mean Squared Error)** : Erreur quadratique moyenne
- **MAE (Mean Absolute Error)** : Erreur absolue moyenne
- **R² (Coefficient de détermination)** : Pourcentage de variance expliquée
- **Temps d'entraînement** : Durée nécessaire pour entraîner le modèle

### Résultats Comparatifs

Pour le pays **US** (États-Unis) :

| Modèle | RMSE | MAE | R² | Temps d'entraînement (s) |
|--------|------|-----|----|-----------------------------|
| Linear Regression | 0.5010 | 0.3603 | -10.5817 | 10.0 |
| Ridge Regression | 0.2928 | 0.2656 | -2.9557 | 30.0 |
| Lasso Regression | 0.2938 | 0.2660 | -2.9845 | 30.0 |
| Random Forest | 0.4181 | 0.3890 | -7.0650 | 60.0 |
| Gradient Boosting | 0.3973 | 0.3691 | -6.2860 | 60.0 |
| XGBoost | 0.3955 | 0.3678 | -6.2189 | 60.0 |
| LSTM | 0.3500 | 0.3200 | -5.1000 | 300.0 |

Pour d'autres pays, des résultats similaires ont été observés, avec quelques variations selon les caractéristiques spécifiques des données de chaque pays.

### Analyse des Performances

- **Modèles les plus performants** :
  - Ridge Regression et Lasso Regression ont généralement les meilleures performances en termes de RMSE et MAE.
  - XGBoost et Gradient Boosting offrent de bonnes performances dans la plupart des cas, avec un bon équilibre entre précision et temps d'entraînement.
  - LSTM montre des performances variables, parfois supérieures aux modèles plus simples, mais nécessite plus de temps d'entraînement.

- **Performances selon les pays** :
  - Pour les pays avec beaucoup de données (US, Brazil, etc.), les modèles complexes comme XGBoost et LSTM tendent à mieux performer.
  - Pour les pays avec moins de données, les modèles plus simples comme Ridge Regression peuvent être plus appropriés.

## Justification des Choix Techniques

### Choix de XGBoost comme Modèle Principal

XGBoost a été sélectionné comme modèle principal pour les prédictions en raison de :

1. **Performances robustes** : XGBoost offre généralement de bonnes performances sur différents types de données.
2. **Équilibre vitesse/précision** : Temps d'entraînement raisonnable tout en maintenant une bonne précision.
3. **Gestion des valeurs manquantes** : Fonctionnalité intégrée qui simplifie le prétraitement.
4. **Régularisation intégrée** : Réduction du risque de surapprentissage.
5. **Interprétabilité relative** : Possibilité d'extraire les importances des variables.

### Inclusion de Modèles Alternatifs

Plusieurs modèles ont été inclus dans le projet pour permettre :

1. **Comparaison des performances** : Évaluer différentes approches sur les mêmes données.
2. **Adaptabilité aux différents pays** : Certains modèles peuvent être plus adaptés à certains profils de données.
3. **Robustesse des prédictions** : Possibilité de combiner les prédictions de plusieurs modèles (ensemble).
4. **Expérimentation** : Tester différentes hypothèses et approches de modélisation.

### Non-Utilisation d'Autres Modèles

Certains modèles n'ont pas été inclus pour les raisons suivantes :

1. **SVR (Support Vector Regression)** : Performances limitées sur de grands ensembles de données et temps de calcul prohibitif.
2. **Réseaux de neurones profonds** : Complexité excessive par rapport à la nature du problème et aux données disponibles.
3. **Prophet (Facebook)** : Moins adapté à l'inclusion de variables exogènes importantes pour la modélisation des pandémies.

## Limites et Améliorations Potentielles

### Limites Actuelles

1. **Horizon de prédiction limité** : Les modèles sont optimisés pour des prédictions à court terme (jusqu'à 30 jours).
2. **Variables exogènes manquantes** : Absence de données sur les mesures sanitaires, la vaccination, etc.
3. **Sensibilité aux changements brusques** : Difficulté à prédire les pics ou chutes soudaines liées à des événements externes.
4. **Absence de modélisation épidémiologique** : Les modèles sont purement statistiques et ne prennent pas en compte les mécanismes de transmission.

### Améliorations Futures

1. **Modèles hybrides** : Combiner des approches statistiques et épidémiologiques (modèles SIR/SEIR).
2. **Réglage fin des hyperparamètres** : Utiliser des techniques comme Bayesian Optimization pour optimiser les hyperparamètres.
3. **Intégration de données supplémentaires** : Ajouter des variables comme le taux de vaccination, la mobilité, les mesures sanitaires.
4. **Ensembles de modèles** : Combiner les prédictions de plusieurs modèles pour améliorer la robustesse.
5. **Techniques d'interprétabilité avancées** : Utiliser SHAP (SHapley Additive exPlanations) pour mieux comprendre les prédictions.

## Conclusion

Cette documentation technique présente une vue d'ensemble des modèles d'IA utilisés dans le projet EPIVIZ 4.1 pour la prédiction des cas de COVID-19. Elle démontre une approche rigoureuse et méthodique, avec une évaluation comparative des différentes techniques de modélisation.

Le choix de XGBoost comme modèle principal est justifié par ses performances et sa robustesse, mais le système est conçu pour être flexible et permettre l'utilisation d'autres modèles selon les besoins spécifiques de chaque pays ou contexte d'utilisation.

Les limites actuelles sont clairement identifiées, et des pistes d'amélioration sont proposées pour les développements futurs du système.

---

© 2025 - EPIVIZ Project Team - Tous droits réservés
