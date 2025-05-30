# EPIVIZ 4.1

## API de pr�diction des cas de COVID-19

EPIVIZ 4.1 est une API permettant de pr�dire l'�volution des cas de COVID-19 pour diff�rents pays, bas�e sur des mod�les de machine learning entra�n�s sur des donn�es historiques.

## Installation

1. Clonez ce d�p�t
2. Installez les d�pendances :
   ```
   pip install -r requirements.txt
   ```

## Utilisation

### Lancement de l'API

```
python run_api.py
```

L'API sera accessible � l'adresse http://127.0.0.1:8000

### Documentation interactive

La documentation interactive de l'API est disponible � l'adresse :
http://127.0.0.1:8000/docs

### Endpoints principaux

- `/api/countries` : Liste des pays disponibles
- `/api/predict/{country}` : Pr�diction des cas pour un pays
- `/api/historical/{country}` : Donn�es historiques pour un pays
- `/api/compare` : Comparaison entre pays
- `/api/models/{country}` : M�triques des mod�les pour un pays

## Documentation

La documentation compl�te du projet est disponible dans le dossier `documentation/` :

- `api_documentation.md` : Documentation technique de l'API
- `modeles_ia_documentation.md` : Documentation des mod�les IA
- `guide_utilisateur.md` : Guide utilisateur
- `conduite_au_changement.md` : Rapport sur la conduite au changement

## Tests

Pour tester l'API, ex�cutez :

```
python test_api.py
```

Pour un test simplifi� :

```
python simple_test.py
```

## Licence

� 2025 - EPIVIZ Project Team - Tous droits r�serv�s
#   M S P R 0 2 - f i x  
 #   M S P R 0 2 - f i x  
 