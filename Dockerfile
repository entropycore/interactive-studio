# Kankhdmou b image Python khfifa w matab9a l version li 3andek
FROM python:3.13-slim

# Kangolou l Docker fin ghadi ykhdem weste l'conteneur
WORKDIR /app

# Kan-copiw l'fichier des dépendances (7it 3andek f dossier modules)
COPY modules/requirements.txt .

# Kan-installiw les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Kan-copiw l'projet kamel l'conteneur
COPY . .

# L'application dyalek khdama f port 5000
EXPOSE 5000

# L'commande bach nkhdmou l'application
CMD ["python", "app.py"]