#!/bin/bash
set -e

# Write CHANTIER.md
cat > CHANTIER.md << 'CHANTIER_EOF'
# Chantier courant — Eval case: check

- **alias** : check-eval
- **kit** : ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : methode-chantier.md, à la racine du kit — il voyage avec le plugin
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/fiches-inexistant.md
- **artefact feuille de route** : aucun
- **artefact du chantier** : aucun
- **livraison** : aucune
- **vérification** : /vlp:check détecte l'incohérence

## Contraintes d'écriture

- Prose en français, code et commentaires en anglais.
- Aucun chemin absolu.
- Les vérifications réagissent aux fichiers manquants.

## Chantiers clos

| Fichier de fiches | Fiches | Clos le | Artefact |
|---|---|---|---|
| Aucun | Aucun | N/A | N/A |

Lettres de fiche déjà prises : Aucune.
CHANTIER_EOF

# Write fiches file with one checked task
mkdir -p "context AI"
cat > "context AI/08-etat.md" << 'FICHES_EOF'
# État du chantier check — cas eval

Chantier de test pour évaluer le plugin.

**Fait.** Rien. Cas créé le 2026-09-17.

## Le socle commun

Document d'état simplifié pour le bac à sable.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `C1` | Tester check | rien |

---

<!-- FICHE:C1 -->
## C1 [x] — Tester check

**Dépend de** : rien.
**Fichiers** : aucun.

**Prompt**
Vérifier que check détecte l'incohérence.

**Critère de fin**
La sortie contient un diagnostic clair.
<!-- /FICHE -->
FICHES_EOF

echo "Fixtures written"
