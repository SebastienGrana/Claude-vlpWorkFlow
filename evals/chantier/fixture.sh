#!/bin/bash
set -e

# Write CHANTIER.md for chantier case (no open chantier)
cat > CHANTIER.md << 'CHANTIER_EOF'
# Chantier courant — Eval case: chantier

- **alias** : chantier-eval
- **kit** : ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : methode-chantier.md, à la racine du kit
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : aucun
- **artefact feuille de route** : aucun
- **artefact du chantier** : aucun
- **livraison** : aucune
- **vérification** : /vlp:chantier propose les deux chantiers

## Contraintes d'écriture

- Prose en français, code et commentaires en anglais.
- Aucun chemin absolu.

## Chantiers clos

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| Aucun | Aucun | N/A | N/A |

Lettres de fiche déjà prises : Aucune.
CHANTIER_EOF

# Write state file with simple chantier names
mkdir -p "context AI"
cat > "context AI/08-etat.md" << 'FICHES_EOF'
# État du chantier chantier — cas eval

Chantier de test pour vérifier que /vlp:chantier propose les chantiers.

**Fait.** Aucune fiche. Cas créé le 2026-09-17.

## La TODO ordonnée — les chantiers possibles

| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |
|---|---|---|---|---|
| 1 | Peindre la girafe | la girafe du jardin retrouve ses taches | 2 fiches | rien |
| 2 | Tailler le bonsaï | le bonsaï tient sur l'étagère | 3 fiches | rien |

FICHES_EOF

echo "Chantier fixtures written"
