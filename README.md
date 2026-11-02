# StegScope

Analyse d'images et stéganographie en self-hosted, pensée pour le CTF. Une
alternative minimaliste et rapide à Aperi'Solve : on dépose une image, le
serveur enchaîne les outils d'analyse habituels et renvoie un rapport lisible,
avec mise en évidence des motifs de type flag.

## Fonctionnalités

- Dépôt par glisser-déposer ou sélection de fichier.
- Enchaînement automatique de `file`, `exiftool`, `strings`, `binwalk` et `zsteg`.
- Filtrage des chaînes sur les motifs de flag (`xxx{...}`) et les lignes sensibles.
- Détection des outils absents sur le serveur, signalés sans interrompre l'analyse.
- Interface sombre épurée, upload validé et travail en répertoire temporaire isolé.

## Stack technique

- **Backend** : Python 3 / Flask, appels système isolés via `subprocess` (sans shell, avec timeout).
- **Analyse** : `file`, `exiftool`, `strings`, `binwalk`, `zsteg`.
- **Frontend** : HTML5 et Tailwind CSS via CDN, JavaScript natif (aucune étape de build).

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

## Installation

```bash
git clone <url-du-depot> stegscope
cd stegscope
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
python run.py
```

L'interface est disponible sur http://127.0.0.1:5000.

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

## Sécurité

L'outil exécute des binaires d'analyse sur les fichiers fournis. À héberger sur
une machine de confiance et à utiliser uniquement sur des fichiers dont vous
disposez des droits : CTF, laboratoires et environnements autorisés.

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
