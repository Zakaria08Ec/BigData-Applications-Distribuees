# SmartFarm AI - Integrated Farm Operations

## Description
SmartFarm AI est une plateforme de supervision IoT et d'analyse de données agricoles en temps réel. Elle permet le monitoring continu des variables environnementales (Température, Humidité, CO2, Luminosité) et intègre une intelligence artificielle générative (Gemini) pour l'optimisation des rendements et la gestion intelligente des ressources.

## Architecture
Le projet repose sur une architecture distribuée robuste :
- **Backend** : API développée avec FastAPI, gérant les WebSockets pour le flux de données en temps réel et l'orchestration des modèles IA.
- **Frontend** : Dashboard interactif développé en React.js, assurant la visualisation des données et les interactions utilisateur.
- **Communication** : Utilisation du protocole WebSocket pour assurer une latence minimale dans la remontée des informations IoT.
- **Déploiement** : Solution containerisée via Docker pour garantir la portabilité et la reproductibilité de l'environnement.

## Structure du dépôt
Projet_Final/
├── README.md              # Documentation du projet
├── src/                   # Code source (main.py, sensor_ws.py, index.html)
├── data/                  # Jeux de données et fichiers de configuration
├── outputs/               # Captures d'écran et rapports de résultats
├── Dockerfile             # Instructions de build Docker
├── docker-compose.yml     # Orchestration des services
├── requirements.txt       # Liste des dépendances Python
└── image_docker.txt       # Nom et tag de l'image Docker

## Prérequis
- Python 3.10 ou supérieur
- Docker Desktop & Docker Compose installés
- Une clé API Google Gemini valide configurée dans `main.py`

## Procédure d'exécution

### 1. Installation locale
1. Clonez le dépôt et placez-vous dans le dossier `Projet_Final/`.
2. Installez les bibliothèques nécessaires :
```bash
   pip install -r requirements.txt

   Lancez l'API :

Bash
   uvicorn src.main:app --reload

   . Lancement via Docker (Containerisation)
   docker build -t smart-farm-ai:latest .

   Lancez les services :
   docker-compose up

   L'application sera disponible sur http://localhost:8000.