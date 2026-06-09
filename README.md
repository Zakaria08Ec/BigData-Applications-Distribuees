# BigData-Applications-Distribuees
# Dépôt de fin de semestre - Applications Distribuées & Big Data

Ce dépôt contient l'ensemble des travaux réalisés au cours du semestre dans le cadre du module **Applications Distribuées adaptées au parcours Big Data**. Il regroupe les travaux pratiques (TPs) hebdomadaires ainsi que le projet final.

## Structure du dépôt
Depot_Final_Semestre/
├── README.md               # Ce fichier
├── Rapport_Final/          # Rapport global de synthèse du semestre
│   └── rapport_final.pdf
├── TPs/                    # Travaux Pratiques (1 à N)
│   ├── TP1/                # Dossier structuré (src/, data/, outputs/, requirements.txt)
│   ├── ...
│   └── TPN/
└── Projet_Final/           # Projet SmartFarm AI
├── README.md           # Documentation spécifique au projet
├── src/                # Code source du projet
├── data/               # Données de test
├── outputs/            # Résultats et captures d'écran
├── Dockerfile          # Configuration Docker
├── docker-compose.yml  # Orchestration du projet
├── requirements.txt    # Dépendances
└── Rapport_Projet/     # Rapport technique du projet
└── rapport_projet.pdf


## Organisation du rendu
1. **Rapport Final Global** : Une synthèse complète de l'ensemble des séances, incluant les objectifs, la démarche, les outils utilisés et une analyse personnelle des difficultés rencontrées.
2. **TPs** : Chaque séance est isolée dans un dossier spécifique contenant son propre code, ses jeux de données et ses résultats.
3. **Projet Final** : Réalisation technique (SmartFarm AI) avec sa propre documentation, sa procédure de construction Docker et son rapport d'ingénierie détaillé.

## Instructions de lancement
Chaque dossier (TP ou Projet) possède son propre fichier `README.md` décrivant les instructions d'installation des dépendances (`requirements.txt`) et les commandes d'exécution. 

*Pour lancer un TP :*
```bash
cd TPs/TPX
pip install -r requirements.txt
python src/main.py
Pour lancer le Projet Final avec Docker :

Bash
cd Projet_Final
docker-compose up
