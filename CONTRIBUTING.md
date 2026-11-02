# Contribuer à StegScope

Merci de votre intérêt. Ce projet reste volontairement simple ; toute
contribution qui préserve cette lisibilité est la bienvenue.

## Mettre en place l'environnement

```bash
git clone https://github.com/qkjhdflj/stegscope.git
cd stegscope
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Ajouter un outil d'analyse

Le moteur repose sur un registre déclaratif dans `stegscope/analysis.py`. Pour
brancher un nouvel outil, ajoutez une entrée `Tool` à la liste `TOOLS` :

```python
Tool(
    "foremost",
    "Carving",
    "foremost",
    "Récupère les fichiers par signature.",
    _simple_runner("foremost", ["-T"]),
    extensions={"png", "jpg", "bmp"},  # optionnel
)
```

- `available()` détecte automatiquement l'absence du binaire via `shutil.which`.
- Les appels passent par `subprocess` sans shell, avec un timeout.
- Pour un traitement sur mesure, écrivez une fonction `runner(path, timeout) -> Result`
  sur le modèle de `_strings_runner`.

## Style

- Code lisible, sans commentaire superflu.
- Pas de dépendance ajoutée sans nécessité réelle.

## Proposer un changement

1. Créez une branche dédiée.
2. Vérifiez que l'application démarre et qu'une analyse aboutit.
3. Ouvrez une pull request décrivant le besoin et la solution.
