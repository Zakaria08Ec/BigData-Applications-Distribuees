# 1. Utiliser une image Python officielle légère
FROM python:3.10-slim

# 2. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier le fichier des dépendances
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le contenu du dossier source dans le conteneur
COPY . .

# 6. Exposer le port sur lequel FastAPI tourne (par défaut 8000)
EXPOSE 8000

# 7. Commande pour lancer l'application au démarrage du conteneur
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]