# Générateur de Prompts Photo

App iOS pour générer des prompts ultra-détaillés pour Gemini.

## Structure

- `app.py` : logique Python
- `index.html` : interface
- `data/*.txt` : banques de données modifiables

## Compilation

Le workflow GitHub Actions compile automatiquement l'IPA à chaque push sur `main`.

## Installation

1. Télécharge l'IPA depuis les Artifacts GitHub Actions
2. Installe via TrollStore (iPhone jailbreaké)

## Modification des banques

Modifie les fichiers dans `data/` puis push sur GitHub. Pas besoin de recompiler.
