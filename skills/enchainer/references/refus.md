<!-- Lu par /vlp:enchainer (étape 3 point 2) sur un verdict REFUSÉE, jamais sur un
     BLOQUÉE ni sans refus : sans refus, ce fichier ne coûte rien. -->

# Un refus, pas un blocage

## Avant de choisir

- **Cause**, dite par le relecteur : `REFUSÉE — fiche : <motifs>` (la faute
  reviendrait avec tout exécutant) ou `REFUSÉE — copie : <motifs>` (la fiche le
  disait, le sous-agent ne l'a pas fait) — `enchainement.md`.
- **Réécriture proposée** : sous une cause `fiche`, la ligne
  `RÉÉCRITURE : <phrase> → <ce qu'elle devient>` ; sinon absente.
- **Rang** : `· refus <n>`, lu sur la sortie de `cocher --refuser` ; après un
  « résolu », elle porte aussi le motif d'avant, `· dernier : <motif>` — sinon,
  c'est celui de ton refus précédent.
- **Famille**, dès `n` ≥ 2 : compare le motif de ce refus au précédent. **Même
  famille** — le même genre de défaut, sur un autre exemple (`ENA5` : motif,
  dossier, filtre, chemin partiel, dossier sans barre, chaque fois deux noms d'un
  même fichier lancés ensemble) : la cause se lit `fiche`, quoi qu'en dise le
  relecteur, et seules restent 1 — recadrer : chercher l'existant, revoir le
  critère ; le recadrage se montre, rien ne se relance sans la réponse de
  l'utilisateur — et 4. **Famille différente** : les quatre.

Pose un questionnaire (`AskUserQuestion`), ces quatre options :

1. **Réécrire la fiche** — cause `fiche` seulement : montre `RÉÉCRITURE` telle
   quelle ; sur oui, un `Edit` qui l'applique, puis reprends l'étape 3 point 1.
2. **Rejouer telle quelle** — cause `copie` : reprends l'étape 3 point 1.
3. **Jouer à la main** — recommandée dès `n` ≥ 2 : `Skill`, `skill: "vlp:tache"`.
4. **S'arrêter** — le `BLOQUÉE` d'aujourd'hui : étapes 3 bis et 4.

Un rejeu compte dans le plafond de 5. Le chef ne réécrit rien de lui-même, et
n'ouvre rien d'autre que ce contrat.
