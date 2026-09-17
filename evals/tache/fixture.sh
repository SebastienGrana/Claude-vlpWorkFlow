#!/bin/bash
set -e

# Write CHANTIER.md for tache case
cat > CHANTIER.md << 'CHANTIER_EOF'
# Chantier courant — Eval case: tache

- **alias** : tache-eval
- **kit** : ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : methode-chantier.md, à la racine du kit
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/19-tache.md
- **artefact feuille de route** : aucun
- **artefact du chantier** : aucun
- **livraison** : aucune
- **vérification** : /vlp:tache lit bien la fiche demandée (T2, pas T1)

## Contraintes d'écriture

- Prose en français, code et commentaires en anglais.
- Aucun chemin absolu.

## Chantiers clos

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| Aucun | Aucun | N/A | N/A |

Lettres de fiche déjà prises : Aucune.
CHANTIER_EOF

# Write fiches file with two tasks
mkdir -p "context AI"
cat > "context AI/19-tache.md" << 'FICHES_EOF'
# État du chantier tache — cas eval

Chantier de test pour vérifier que /vlp:tache lit bien la fiche demandée.

**Fait.** Aucune fiche. Cas créé le 2026-09-17.

## Le socle commun

Pas de socle pour ce cas.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `T1` | Première fiche | rien |
| `T2` | Deuxième fiche | rien |

---

<!-- FICHE:T1 -->
## T1 [ ] — Première fiche

**Dépend de** : rien.
**Fichiers** : aucun.

**Prompt**
Réponds seulement par le mot ORANGE-T1, puis arrête-toi : n'écris rien, ne coche rien.

**Critère de fin**
Le mot demandé est affiché.
<!-- /FICHE -->

---

<!-- FICHE:T2 -->
## T2 [ ] — Deuxième fiche

**Dépend de** : rien.
**Fichiers** : aucun.

**Prompt**
Réponds seulement par le mot CITRON-T2, puis arrête-toi : n'écris rien, ne coche rien.

**Critère de fin**
Le mot demandé est affiché.
<!-- /FICHE -->
FICHES_EOF

echo "Tache fixtures written"
