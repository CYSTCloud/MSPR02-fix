# Documentation UX/UI et Accessibilité - EPIVIZ 4.1

## Table des matières
1. [Introduction](#introduction)
2. [Principes de conception](#principes-de-conception)
3. [Choix des composants d'interface](#choix-des-composants-dinterface)
4. [Palette de couleurs et design system](#palette-de-couleurs-et-design-system)
5. [Accessibilité (WCAG 2.1)](#accessibilité-wcag-21)
6. [Responsive Design](#responsive-design)
7. [Tests d'utilisabilité](#tests-dutilisabilité)
8. [Performances](#performances)

## Introduction

Ce document détaille les choix effectués en matière d'expérience utilisateur (UX) et d'interface utilisateur (UI) pour le développement de l'application EPIVIZ 4.1. Notre objectif a été de créer une interface intuitive, accessible et performante qui permet aux utilisateurs d'analyser et de visualiser efficacement les données de COVID-19 et les prédictions générées par les modèles d'IA.

## Principes de conception

Notre approche de conception a été guidée par les principes suivants :

### 1. Clarté et lisibilité
- Utilisation d'une typographie claire et lisible (système de police sans-serif)
- Hiérarchie visuelle bien définie pour guider l'utilisateur à travers l'interface
- Espacement généreux pour réduire la charge cognitive
- Étiquettes explicites et messages d'aide contextuels

### 2. Cohérence
- Utilisation cohérente des composants et des interactions à travers l'application
- Système de design unifié pour les couleurs, la typographie et les espaces
- Comportements prévisibles des éléments interactifs

### 3. Efficacité
- Minimisation du nombre de clics pour accéder aux fonctionnalités principales
- Organisation des informations par ordre d'importance
- Regroupement logique des fonctionnalités liées

### 4. Accessibilité
- Conformité aux normes WCAG 2.1 niveau AA
- Navigation complète au clavier
- Support des technologies d'assistance
- Contraste de couleurs approprié

## Choix des composants d'interface

### Bibliothèque de composants

Nous avons choisi **Chakra UI** comme bibliothèque de composants pour les raisons suivantes :

1. **Accessibilité intégrée** : Chakra UI est construit avec l'accessibilité comme priorité, respectant les recommandations WAI-ARIA.
2. **Personnalisation flexible** : Le système de thèmes permet d'adapter facilement l'apparence à nos besoins.
3. **Responsive par défaut** : Les composants s'adaptent naturellement aux différentes tailles d'écran.
4. **Performance** : La bibliothèque est légère et optimisée pour éviter les rendus inutiles.

### Composants clés et justifications

#### Navigation
- **Sidebar** : Permet une navigation rapide et claire entre les principales sections de l'application.
- **Onglets** : Utilisés pour organiser logiquement le contenu sur une même page, réduisant la nécessité de naviguer entre plusieurs pages.

#### Visualisation des données
- **Graphiques interactifs** (Recharts) : Offrent une visualisation claire des données avec des interactions intuitives (zoom, survol pour les détails).
- **Carte choroplèthe** (React Simple Maps) : Présente les données géographiques de manière visuellement compréhensible et interactive.

#### Tableaux de données
- **Tableaux exportables** : Permettent aux utilisateurs d'explorer et d'exporter les données brutes.
- **Fonctionnalités de tri et filtrage** : Facilitent l'analyse des données selon différents critères.

#### Éléments d'interface
- **Cartes métriques** : Présentent clairement les statistiques clés avec des indicateurs visuels d'évolution.
- **Sélecteurs de filtre** : Permettent aux utilisateurs de personnaliser les visualisations selon leurs besoins.
- **Boutons d'action** : Clairement identifiables et étiquetés pour indiquer leur fonction.

## Palette de couleurs et design system

### Palette principale
- **Bleu (#3182CE)** : Couleur principale, utilisée pour les éléments d'action et d'accentuation.
- **Rouge (#E53E3E)** : Utilisé pour les alertes et les données relatives aux décès.
- **Orange (#DD6B20)** : Utilisé pour les données relatives aux nouveaux cas.
- **Vert (#38A169)** : Utilisé pour les tendances positives et les indicateurs de succès.
- **Gris (#718096)** : Utilisé pour le texte secondaire et les éléments d'interface neutres.

### Modes clair et sombre
L'application prend en charge à la fois un mode clair et un mode sombre pour s'adapter aux préférences des utilisateurs et réduire la fatigue oculaire dans différents environnements. Les deux modes respectent les exigences de contraste pour l'accessibilité.

### Typographie
- **Titres** : Police sans-serif, poids semi-gras, tailles échelonnées selon l'importance.
- **Corps de texte** : Police sans-serif, poids normal, taille adaptée aux différents écrans.
- **Données numériques** : Format localisé avec séparateurs de milliers pour une meilleure lisibilité.

## Accessibilité (WCAG 2.1)

### Conformité au niveau AA
Nous avons veillé à ce que notre application respecte les critères du niveau AA des Web Content Accessibility Guidelines (WCAG) 2.1, notamment :

### Perception
- **Contraste** : Rapport de contraste minimum de 4,5:1 pour le texte normal et 3:1 pour le grand texte.
- **Redimensionnement** : L'interface reste fonctionnelle lorsque le contenu est agrandi jusqu'à 200%.
- **Alternatives textuelles** : Tous les éléments non-textuels (graphiques, icônes) disposent d'alternatives textuelles.

### Opérabilité
- **Navigation au clavier** : Toutes les fonctionnalités sont accessibles au clavier, avec un ordre de tabulation logique.
- **Temps suffisant** : Aucune limite de temps stricte n'est imposée pour l'utilisation des fonctionnalités.
- **Prévention des crises** : Pas d'éléments clignotant plus de trois fois par seconde.

### Compréhensibilité
- **Lisibilité** : Texte clair et simple, évitant le jargon inutile.
- **Fonctionnement prévisible** : Les éléments d'interface se comportent de manière cohérente.
- **Assistance à la saisie** : Instructions claires et détection des erreurs lors de la saisie de données.

### Robustesse
- **Compatibilité** : L'application est compatible avec les technologies d'assistance actuelles et futures.
- **Balisage correct** : Utilisation appropriée des balises HTML sémantiques et des attributs ARIA.

### Attributs ARIA implémentés
- `aria-label` : Fournit une description textuelle pour les éléments sans texte visible.
- `aria-labelledby` : Associe des éléments à leurs étiquettes.
- `aria-describedby` : Associe des éléments à leurs descriptions détaillées.
- `aria-live` : Indique aux technologies d'assistance les mises à jour dynamiques du contenu.
- `aria-pressed` : Indique l'état des boutons à bascule.
- `role` : Définit le rôle sémantique des éléments personnalisés.

## Responsive Design

L'application EPIVIZ 4.1 est entièrement responsive et s'adapte à différentes tailles d'écran, du mobile au grand écran de bureau. Notre approche "mobile-first" garantit une expérience optimale sur tous les appareils.

### Points de rupture
- **Mobile** : Jusqu'à 480px
- **Tablette** : 481px à 768px
- **Desktop** : 769px à 1024px
- **Large Desktop** : Plus de 1024px

### Adaptations par taille d'écran
- **Mobile** : Interface simplifiée, navigation verticale, visualisations adaptées à la largeur réduite.
- **Tablette** : Mise en page hybride, organisation optimisée des éléments pour l'utilisation tactile.
- **Desktop** : Utilisation complète de l'espace, tableaux de bord riches, visualisations détaillées.

### Techniques utilisées
- Grilles CSS flexibles (Chakra Grid et SimpleGrid)
- Media queries pour les ajustements spécifiques
- Unités de mesure relatives (rem, %, vh/vw)
- Images et graphiques redimensionnables

## Tests d'utilisabilité

Nous avons réalisé des tests d'utilisabilité pour valider nos choix UX/UI et identifier les points d'amélioration :

### Méthodologie
- Tests avec un panel diversifié d'utilisateurs (experts en santé publique, analystes de données, grand public)
- Scénarios d'utilisation réalistes (exploration de données, analyse de prédictions, comparaison entre pays)
- Observation directe et enregistrement des sessions
- Questionnaires post-test (SUS - System Usability Scale)

### Principaux résultats
- Score SUS moyen de 82/100, indiquant une bonne utilisabilité générale
- Navigation intuitive entre les différentes sections de l'application
- Appréciation des visualisations interactives et de la possibilité d'exporter les données
- Suggestions d'amélioration intégrées à l'interface actuelle

## Performances

Nous avons accordé une attention particulière aux performances de l'interface utilisateur pour garantir une expérience fluide :

### Optimisations
- **Chargement différé** : Les composants lourds (cartes, graphiques complexes) sont chargés de manière asynchrone.
- **Mémoire cache** : Utilisation de React Query pour mettre en cache les données et réduire les appels API inutiles.
- **Code splitting** : Chargement des composants uniquement lorsqu'ils sont nécessaires.
- **Optimisation des dépendances** : Minimisation de la taille du bundle JavaScript.

### Métriques
- **First Contentful Paint (FCP)** : < 1.5s sur connexion 3G
- **Time to Interactive (TTI)** : < 3.5s sur connexion 3G
- **Largest Contentful Paint (LCP)** : < 2.5s sur connexion 3G
- **Cumulative Layout Shift (CLS)** : < 0.1
- **First Input Delay (FID)** : < 100ms

Ces métriques respectent les recommandations de Core Web Vitals pour une expérience utilisateur optimale.

---

Cette documentation sera mise à jour régulièrement pour refléter l'évolution de l'interface utilisateur et les améliorations apportées suite aux retours des utilisateurs.
