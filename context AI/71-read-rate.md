> **QUAND LIRE** : on joue une fiche `RAT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache RAT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier RAT — Un `Read` raté réveille-t-il le filet ?

**À quoi il sert.** Le filet tire après un `Read` réussi et après un Bash à code non nul
(`FIL3`, rejoué par `EVF`) ; un `Read` sur un fichier absent n'est pas éprouvé.

**Estimé.** 0,5 fiches · ≈2,03 $ — ≈4,05 $/fiche sur 58 clos (le 2026-09-26).

**CLOS** le 2026-09-26. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** RAT1..RAT1 (2026-09-26) : un Read raté réveille le filet : PostToolUseFailure:Read, prouvé à plafond 5 par evals/filet-rate/ (témoin 80 muet) — estimé 0,5 fiches ≈2,03 $ · cadré 1 · joué 1 fiches ≈1,43 $.

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc

## Le socle commun

Cadré seul, la nuit du 2026-09-26, l'utilisateur dormant (« fait le plus de chantier
possible à la main ») : une fiche, aucun changement de `scripts/vlp.py`.

**L'outillage** vient d'`EVF` : `vlp.py kit-essai` (copie à plafond bas), `vlp.py bac`,
`vlp.py transcription`, et `evals/filet/rejouer.sh` pour la forme d'un lancement sous WSL2
(Bash exige un sandbox). La trace de l'eval ne porte pas le contexte des hooks : la
preuve est la transcription gardée (journal d'`EVF2`).

**Invariants** : ni le kit sur disque ni un projet réel ne bougent ; chaque verdict au
journal avec `costUsd`, `turns`, sorties brutes ; témoin à plafond 80.

## L'ordre des fiches

- `RAT1` — le cas `F3` (douze `Read` sur des fichiers absents). Aucune dépendance.

---

<!-- FICHE:RAT1 -->
## RAT1 [x] — Le cas F3 : douze `Read` sur des fichiers absents

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc
**Dépend de** : rien.
**Fichiers** : `evals/filet/` (forme du cas et de `rejouer.sh`) — et rien d'autre.

**Prompt**
Crée `evals/filet-rate/` (tag `filet-rate`, hors du tag `filet` tant que la réponse
n'est pas connue) : son `fixture.sh` pose le bac par `vlp.py bac .` puis ajoute à
`fiches.md` une fiche `F3` « lis `m01.txt` … `m12.txt` », fichiers absents. Lance-le sous
WSL2 à plafond 6 puis 80 ; compte chaque transcription gardée.

**Critère de fin**
Au journal, verdict en tête — **oui** si, à plafond 6, `AVERTISSEMENTS` ≥ 1 avec un
`hook=PostToolUseFailure:Read` (ou `PostToolUse:Read`) ; **non** si aucun — puis la sortie
brute de `vlp.py transcription` aux deux plafonds, `costUsd` et `turns`. Témoin :
plafond 80, `AVERTISSEMENTS=0`.
<!-- /FICHE -->
