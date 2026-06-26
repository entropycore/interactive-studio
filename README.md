# GEN-STUDIO

GEN-STUDIO est une application web Flask dédiée à la création artistique, à la visualisation de données et à l’assistance IA. Le projet permet de générer des œuvres, explorer une galerie, analyser des fichiers CSV et discuter avec un assistant nommé Honar.

## Fonctionnalités

- Interface d’accueil et navigation dans le site
- Galerie des créations sauvegardées
- Génération d’œuvres artistiques visuelles
- Analyse et visualisation de données à partir de fichiers CSV
- Assistant IA Honar avec système de chat
- Gestion des notes créatives
- Gestion des assets, uploads et wallpapers

## Prérequis

- Docker Desktop installé et lancé
- Python 3.10 ou plus (si vous voulez lancer le projet sans Docker)
- pip

## Démarrage rapide avec Docker (recommandé)

1. Ouvrir Docker Desktop avant de lancer la commande.
2. Ouvrir un terminal dans la racine du projet.
3. Lancer la commande suivante :

```bash
docker compose up --build
```

4. Ouvrir l’adresse suivante dans votre navigateur :

```text
http://localhost:5000
```

> Si Docker Desktop n’est pas déjà lancé, la commande peut échouer ou ne pas fonctionner correctement.

## Installation locale (optionnelle)

1. Ouvrir un terminal dans la racine du projet.
2. Créer et activer un environnement virtuel :

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Installer les dépendances :

```bash
pip install -r modules/requirements.txt
```

4. Créer un fichier `.env` à la racine du projet avec votre clé API Gemini si vous voulez utiliser l’assistant Honar :

```env
GEMINI_API_KEY=your_api_key_here
```

5. Lancer le projet :

```bash
python app.py
```

Puis ouvrir :

```text
http://127.0.0.1:5000
```

## Structure du projet

- `app.py` : application Flask principale
- `templates/` : fichiers HTML de l’interface
- `static/` : fichiers CSS, JavaScript et assets publics
- `modules/` : logique métier, IA, génération artistique et outils média
- `data/` : fichiers de données et sauvegardes JSON/CSV

## Notes

- Si la variable `GEMINI_API_KEY` n’est pas définie, l’assistant Honar affichera un message de secours au lieu d’appeler l’API.
- Les fichiers générés sont stockés dans le dossier `static/outputs`.
