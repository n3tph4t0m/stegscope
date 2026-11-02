<div align="center">

# StegScope

**Analyse d'images et stéganographie en self-hosted, pensée pour le CTF.**

Une alternative minimaliste et rapide à Aperi'Solve : déposez une image, le
serveur enchaîne les outils d'analyse habituels et renvoie un rapport lisible,
avec mise en évidence des motifs de type flag.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/status-actif-brightgreen?style=flat-square)

</div>

---

## Aperçu

StegScope expose une interface web sombre où l'on dépose une image. En arrière-plan,
un serveur Flask exécute une batterie d'outils d'analyse dans un environnement isolé,
agrège les résultats et surligne automatiquement les chaînes ressemblant à un flag.

```
┌──────────────┐   upload    ┌───────────────┐   subprocess   ┌──────────────────────────┐
│  Navigateur  │ ──────────▶ │  Flask (API)  │ ─────────────▶ │ file · exiftool · strings │
│  (dark UI)   │ ◀────────── │  /api/analyze │ ◀───────────── │ binwalk · zsteg           │
└──────────────┘   rapport   └───────────────┘    résultats   └──────────────────────────┘
```

## Démarrage rapide

```bash
git clone https://github.com/qkjhdflj/stegscope.git
cd stegscope
./start.sh
```

`start.sh` crée l'environnement virtuel, installe les dépendances au premier
lancement puis sert l'interface sur **http://127.0.0.1:5000**.

## Fonctionnalités

- Dépôt par glisser-déposer ou sélection de fichier.
- Enchaînement automatique de `file`, `exiftool`, `strings`, `binwalk` et `zsteg`.
- Filtrage des chaînes sur les motifs de flag (`xxx{...}`) et les lignes sensibles.
- Détection des outils absents sur le serveur, signalés sans interrompre l'analyse.
- Interface sombre épurée, upload validé et travail en répertoire temporaire isolé.

## Stack technique

| Couche | Technologies |
|---|---|
| Backend | Python 3, Flask, `subprocess` (sans shell, avec timeout) |
| Analyse | `file`, `exiftool`, `strings`, `binwalk`, `zsteg` |
| Frontend | HTML5, Tailwind CSS (CDN), JavaScript natif — aucune étape de build |

## Prérequis

Python 3.10 ou supérieur, et les outils d'analyse accessibles dans le `PATH`.

```bash
# Debian / Ubuntu / Kali
sudo apt install exiftool binwalk file binutils
# zsteg (gem Ruby)
sudo gem install zsteg
```

Les outils absents ne bloquent pas l'application : ils apparaissent comme
« indisponible » dans le rapport.

## Installation manuelle

Si vous préférez ne pas utiliser `start.sh` :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Configuration

Réglable par variables d'environnement :

| Variable | Rôle | Défaut |
|---|---|---|
| `STEGSCOPE_SECRET` | Clé de session Flask | aléatoire |
| `STEGSCOPE_UPLOADS` | Répertoire de travail | `./uploads` |
| `STEGSCOPE_MAX_BYTES` | Taille maximale d'un upload | `16777216` (16 Mo) |
| `STEGSCOPE_TIMEOUT` | Délai par outil, en secondes | `25` |

## Utilisation

1. Ouvrir l'interface et déposer une image (PNG, JPG, GIF, BMP, WEBP, TIFF).
2. Chaque outil produit une carte de résultat ; les motifs de flag détectés sont
   mis en évidence en haut de la carte `strings`.
3. Le fichier est supprimé du serveur dès l'analyse terminée.

## Structure du projet

```
stegscope/
├── run.py                   point d'entrée
├── start.sh                 lanceur (venv + install + run)
├── requirements.txt
└── stegscope/
    ├── __init__.py          application factory
    ├── config.py            configuration par variables d'environnement
    ├── analysis.py          moteur d'analyse (registre d'outils)
    ├── views.py             routes et API
    ├── templates/index.html interface
    └── static/app.js        logique front
```

## Contribuer

Les contributions sont bienvenues. Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour
ajouter un outil d'analyse ou proposer une amélioration.

## Sécurité

StegScope exécute des binaires d'analyse sur les fichiers fournis. À héberger sur
une machine de confiance et à utiliser uniquement sur des fichiers dont vous
disposez des droits : CTF, laboratoires et environnements autorisés.

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
