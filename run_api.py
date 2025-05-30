"""
EPIVIZ 4.1 - Script de lancement de l'API
----------------------------------------
Ce script permet de lancer facilement l'API EPIVIZ avec uvicorn.
"""

import uvicorn
import os
import sys
from api.config import API_HOST, API_PORT, API_DEBUG

def main():
    """Lance l'API EPIVIZ avec les paramètres configurés"""
    print("=== LANCEMENT DE L'API EPIVIZ 4.1 ===")
    print(f"Hôte: {API_HOST}")
    print(f"Port: {API_PORT}")
    print(f"Mode debug: {'Activé' if API_DEBUG else 'Désactivé'}")
    print("\nPour accéder à l'API:")
    print(f"  - Documentation: http://localhost:{API_PORT}/docs")
    print(f"  - Interface principale: http://localhost:{API_PORT}")
    print("\nAppuyez sur CTRL+C pour arrêter l'API")
    print("="*40)
    
    try:
        uvicorn.run("api.app:app", host=API_HOST, port=API_PORT, reload=API_DEBUG)
    except KeyboardInterrupt:
        print("\nArrêt de l'API...")
    except Exception as e:
        print(f"\nErreur lors du lancement de l'API: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
