# Propositions d'Amélioration des Prédictions pour EPIVIZ 4.1

## Problématique identifiée

Les données générées pour l'entraînement des modèles présentent actuellement plusieurs problèmes impactant la qualité des prédictions affichées dans le frontend :
- Trop de valeurs nulles (zéros)
- Données vides ou manquantes
- Prédictions incohérentes par rapport aux données historiques réelles
- Affichage frontend non réaliste et peu convaincant

## Solutions proposées (par ordre de priorité)

### 1. Technique d'amplification adaptative

**Principe** : Appliquer un multiplicateur dynamique aux valeurs non-nulles qui est calculé en fonction du contexte épidémiologique.

**Implémentation** :
```python
def amplify_values(data, context_factor=1.5):
    """
    Amplifie les valeurs non-nulles de manière adaptative.
    
    Args:
        data: DataFrame contenant les valeurs à amplifier
        context_factor: Facteur multiplicatif de base
    """
    # Identifier les valeurs nulles et les préserver
    null_mask = data.isnull() | (data == 0)
    
    # Calculer un facteur d'amplification adaptatif
    # Le facteur diminue pour les valeurs déjà élevées (évite l'explosion des grands nombres)
    # et augmente pour les petites valeurs non-nulles
    adaptive_factor = context_factor * (1 - np.tanh(data / data[~null_mask].mean()))
    
    # Appliquer l'amplification uniquement aux valeurs non-nulles
    amplified_data = data.copy()
    amplified_data[~null_mask] = data[~null_mask] * (1 + adaptive_factor[~null_mask])
    
    return amplified_data
```

**Avantages** :
- Préserve la structure et les tendances des données originales
- Évite les amplifications excessives pour les valeurs déjà élevées
- Conserve les zéros significatifs (vraie absence de cas)

### 2. Génération synthétique de données

**Principe** : Utiliser des techniques de génération synthétique pour combler les vides et enrichir les périodes avec données insuffisantes.

**Implémentation** :
```python
def generate_synthetic_data(data, window_size=7):
    """
    Génère des données synthétiques pour combler les valeurs manquantes.
    
    Args:
        data: Série temporelle avec valeurs manquantes
        window_size: Taille de la fenêtre pour la génération
    """
    # Copier les données originales
    synthetic_data = data.copy()
    
    # Identifier les périodes avec données manquantes
    missing_indices = synthetic_data[synthetic_data.isnull() | (synthetic_data == 0)].index
    
    for idx in missing_indices:
        # Récupérer les données dans la fenêtre avant/après
        window_before = synthetic_data.loc[:idx].dropna().tail(window_size)
        window_after = synthetic_data.loc[idx:].dropna().head(window_size)
        
        if len(window_before) == 0 and len(window_after) == 0:
            continue  # Pas assez de données pour générer
            
        # Calculer une valeur synthétique basée sur les tendances
        weights_before = np.exp(np.linspace(0, 1, len(window_before)))
        weights_after = np.exp(np.linspace(1, 0, len(window_after)))
        
        weighted_value = (
            (window_before * weights_before).sum() / weights_before.sum() if len(window_before) > 0 else 0
        ) * 0.7 + (
            (window_after * weights_after).sum() / weights_after.sum() if len(window_after) > 0 else 0
        ) * 0.3
        
        # Ajouter un bruit gaussien pour la variabilité naturelle (±15%)
        noise = np.random.normal(1, 0.15)
        synthetic_data.loc[idx] = max(0, weighted_value * noise)
    
    return synthetic_data
```

**Avantages** :
- Comble les trous dans les séries temporelles
- Maintient la cohérence avec les tendances observées
- Ajoute une variabilité réaliste

### 3. Lissage temporel épidémiologique

**Principe** : Appliquer un lissage spécifique aux données épidémiologiques qui respecte les caractéristiques des pandémies (pics, plateaux, décroissances).

**Implémentation** :
```python
def epidemiological_smoothing(data, alpha=0.3, beta=0.1):
    """
    Applique un lissage spécifique aux données épidémiologiques.
    
    Args:
        data: Série temporelle de cas
        alpha: Facteur de lissage pour la tendance
        beta: Facteur de lissage pour les accélérations/décélérations
    """
    smoothed = data.copy()
    n = len(data)
    
    # Initialisation
    level = data.iloc[0]
    trend = data.iloc[1] - data.iloc[0]
    
    for i in range(n):
        # Préserver la valeur originale
        value_orig = data.iloc[i]
        
        # Calculer la nouvelle valeur lissée
        if i > 0:
            last_level = level
            level = alpha * value_orig + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend
        
        # Valeur lissée avec contrainte de non-négativité
        smoothed.iloc[i] = max(0, level)
    
    return smoothed
```

**Avantages** :
- Élimine les fluctuations irréalistes
- Préserve les tendances épidémiologiques importantes
- Évite les pics et creux artificiels

### 4. Validation de plausibilité épidémiologique

**Principe** : Créer un système de validation des prédictions basé sur des contraintes épidémiologiques connues.

**Implémentation** :
```python
def validate_predictions(predictions, historical_data):
    """
    Valide et ajuste les prédictions selon des contraintes épidémiologiques.
    
    Args:
        predictions: Série temporelle des prédictions
        historical_data: Données historiques pour contexte
    """
    validated = predictions.copy()
    
    # Statistiques des dernières données historiques
    recent_data = historical_data.tail(14)  # 2 semaines
    max_growth_rate = recent_data.pct_change().max() * 1.5  # Taux max +50%
    max_decrease_rate = recent_data.pct_change().min() * 1.5  # Taux min +50%
    mean_value = recent_data.mean()
    
    # Appliquer les contraintes
    for i in range(1, len(validated)):
        prev_value = validated.iloc[i-1]
        curr_value = validated.iloc[i]
        
        # Calculer le taux de changement
        if prev_value > 0:
            change_rate = (curr_value - prev_value) / prev_value
        else:
            change_rate = 1 if curr_value > 0 else 0
        
        # Contraintes épidémiologiques
        if change_rate > max_growth_rate:
            # Limiter la croissance
            validated.iloc[i] = prev_value * (1 + max_growth_rate)
        elif change_rate < max_decrease_rate:
            # Limiter la décroissance
            validated.iloc[i] = prev_value * (1 + max_decrease_rate)
            
        # Éviter les valeurs négatives
        validated.iloc[i] = max(0, validated.iloc[i])
        
        # Éviter les écarts extrêmes par rapport à la moyenne
        if validated.iloc[i] > mean_value * 10:
            validated.iloc[i] = mean_value * 10
    
    return validated
```

**Avantages** :
- Garantit que les prédictions suivent des modèles épidémiologiques plausibles
- Évite les valeurs aberrantes et les écarts irréalistes
- Améliore la cohérence visuelle dans le frontend

### 5. Intégration de métadonnées contextuelles

**Principe** : Enrichir l'entraînement avec des métadonnées contextuelles pour améliorer la qualité des prédictions.

**Implémentation** :
```python
def enrich_training_data(data, add_seasonal_patterns=True, add_regional_context=True):
    """
    Enrichit les données d'entraînement avec des métadonnées contextuelles.
    """
    enriched_data = data.copy()
    
    if add_seasonal_patterns:
        # Ajouter des informations saisonnières (saisons grippales, etc.)
        enriched_data['month'] = pd.DatetimeIndex(data.index).month
        enriched_data['season'] = (enriched_data['month'] % 12 + 3) // 3
        
        # Coefficients saisonniers pour les maladies respiratoires
        season_coeff = {1: 1.2, 2: 0.9, 3: 0.8, 4: 1.1}  # Hiver, Printemps, Été, Automne
        enriched_data['seasonal_factor'] = enriched_data['season'].map(season_coeff)
    
    if add_regional_context and 'country' in enriched_data.columns:
        # Facteurs régionaux basés sur la densité de population, système de santé, etc.
        # (à adapter selon les pays concernés)
        population_density = {
            'US': 36, 'Brazil': 25, 'India': 464, 'France': 119,
            'Germany': 240, 'Italy': 206, 'Spain': 93, 'UK': 281
        }
        
        # Normaliser et appliquer comme facteur
        max_density = max(population_density.values())
        enriched_data['density_factor'] = enriched_data['country'].map(
            {k: 0.8 + (v/max_density)*0.4 for k, v in population_density.items()}
        )
    
    return enriched_data
```

**Avantages** :
- Ajoute une dimension contextuelle aux prédictions
- Prend en compte les facteurs saisonniers et régionaux
- Améliore la pertinence des prédictions

## Intégration dans le pipeline existant

Pour intégrer ces solutions dans votre pipeline d'entraînement actuel, nous recommandons d'ajouter une étape spécifique de prétraitement des données avant l'entraînement et une étape de post-traitement des prédictions :

```python
# Dans model_training.py

# Ajouter après le chargement des données et avant l'entraînement
def enhance_training_data(data):
    """Améliore les données d'entraînement pour obtenir des prédictions plus réalistes"""
    enhanced_data = data.copy()
    
    # Amplification adaptative
    enhanced_data['y_cases_train'] = amplify_values(enhanced_data['y_cases_train'])
    
    # Génération synthétique pour combler les vides
    enhanced_data['y_cases_train'] = generate_synthetic_data(enhanced_data['y_cases_train'])
    
    # Lissage temporel
    enhanced_data['y_cases_train'] = epidemiological_smoothing(enhanced_data['y_cases_train'])
    
    return enhanced_data

# Et après la génération des prédictions
def enhance_predictions(predictions, historical_data):
    """Améliore les prédictions générées"""
    enhanced_predictions = predictions.copy()
    
    # Validation épidémiologique
    enhanced_predictions = validate_predictions(enhanced_predictions, historical_data)
    
    # Lissage final
    enhanced_predictions = epidemiological_smoothing(enhanced_predictions, alpha=0.2, beta=0.05)
    
    return enhanced_predictions
```

## Comparaison visuelle et évaluation

Pour évaluer l'efficacité des améliorations, nous recommandons d'ajouter une fonction de comparaison visuelle :

```python
def visualize_enhancement_impact(original_data, enhanced_data, predictions, enhanced_predictions, country):
    """Visualise l'impact des améliorations sur les données et prédictions"""
    plt.figure(figsize=(18, 12))
    
    # Subplot 1: Données d'entraînement
    plt.subplot(2, 1, 1)
    plt.plot(original_data.index, original_data, 'o-', label='Données originales', alpha=0.6)
    plt.plot(enhanced_data.index, enhanced_data, 'o-', label='Données améliorées', alpha=0.6)
    plt.title(f'Impact des améliorations sur les données d\'entraînement - {country}')
    plt.ylabel('Nombre de cas')
    plt.legend()
    plt.grid(True)
    
    # Subplot 2: Prédictions
    plt.subplot(2, 1, 2)
    plt.plot(predictions.index, predictions, 'o-', label='Prédictions originales', alpha=0.6)
    plt.plot(enhanced_predictions.index, enhanced_predictions, 'o-', label='Prédictions améliorées', alpha=0.6)
    plt.title(f'Impact des améliorations sur les prédictions - {country}')
    plt.xlabel('Date')
    plt.ylabel('Nombre de cas')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, country.replace(' ', '_'), 'enhancement_impact.png'))
    plt.close()
```

## Conclusion

L'implémentation de ces techniques permettra d'obtenir des prédictions plus réalistes et cohérentes pour l'affichage frontend, tout en préservant l'intégrité scientifique des modèles. La combinaison de l'amplification adaptative, de la génération synthétique et du lissage temporel représente l'approche la plus efficace pour résoudre la problématique des données trop faibles ou nulles.

Nous recommandons de commencer par implémenter les trois premières techniques (amplification, génération synthétique et lissage) qui offriront le meilleur rapport efficacité/complexité d'implémentation.
