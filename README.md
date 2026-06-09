# 📂 Dépôt de fin de semestre : Applications Distribuées & Big Data

Ce dépôt centralise l'ensemble des travaux réalisés durant le semestre académique 2025-2026. Il témoigne de l'acquisition de compétences techniques en **Data Engineering**, **systèmes distribués** et **conteneurisation**, en passant de l'implémentation algorithmique à l'architecture Big Data robuste.

---

## 🏗 Structure du Dépôt

L'arborescence est organisée pour faciliter la navigation et la reproductibilité des travaux :

```text
Depot_Final_Semestre/
├── README.md               # Documentation globale
├── Rapport_Final/          # Synthèse globale du semestre (PDF)
├── TPs/                    # Travaux Pratiques (Séances 1 à 9)
│   ├── TP1/                # Code, data, et rapports individuels
│   ├── ...
│   └── TP9/
└── Projet_Final/           # Projet SmartFarm AI (Conteneurisé)
    ├── README.md           # Guide dédié au projet final
    ├── src/                # Backend (FastAPI) et Frontend
    ├── data/               # Jeux de données et config
    ├── outputs/            # Logs et résultats
    ├── Dockerfile          # Configuration du build Docker
    ├── docker-compose.yml  # Orchestration des services
    └── Rapport_Projet/     # Rapport technique (PDF)

🛠 Compétences & Technologies
Ce semestre a permis l'implémentation de concepts clés du Big Data :

Ingénierie de données : Modélisation immuable (frozen dataclasses), validation de contrats de messages.

Systèmes Distribués : Architecture RPC, gestion réseau, corrélations de requêtes (request_id).

Stream Processing : Architecture événementielle, fenêtrage temporel, gestion de la latence et du débit.

Tolérance aux pannes : Partitionnement, gestion des offsets, checkpointing et reprise (recovery).

DevOps & Déploiement : Conteneurisation des services et orchestrations via Docker Compose.

🚀 Guide d'exécution
1. Travaux Pratiques (TPs)
Chaque TP dispose de sa propre documentation. Pour exécuter un TP spécifique :

Bash
cd TPs/TPX
pip install -r requirements.txt
python src/main.py
2. Projet Final (SmartFarm AI)
Le projet final est entièrement conteneurisé. Pour le déployer localement :

Assurez-vous que Docker Desktop est en cours d'exécution.

Accédez au dossier du projet :

Bash
cd Projet_Final
Lancez les services :

Bash
docker-compose up --build
Accédez à l'interface : http://localhost:8000

📈 Analyse du Parcours
Le module a nécessité une montée en compétence rapide sur des architectures complexes. La transition d'un modèle monolithique vers un modèle distribué, bien que difficile, a permis de mieux appréhender les contraintes réelles de production : idempotence, backpressure et scalabilité horizontale.
