---
description: Vérifie qu'un projet équipé est cohérent — fichiers, cases cochées, page publiée, coûts
argument-hint: (rien) | <chemin du projet>
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(grep:*), Bash(awk:*), Bash(sed:*), Bash(wc:*), Bash(pwd:*), Read, Artifact
---

Contrôle un projet équipé de la méthode. **Cette commande n'écrit rien.** Elle
mesure, elle compare, elle dit ce qui cloche, et elle propose des corrections
que l'utilisateur accepte ou non. Si elle se met à réparer d'elle-même, elle
devient la septième source de vérité.

À lancer quand on doute : après une session interrompue, avant de reprendre un
chantier laissé de côté, ou quand la page publiée ne ressemble plus au fichier.

## 1. Lire la carte

```bash
cat CHANTIER.md
```

Retiens : le **kit**, le **dossier de contexte**, le **fichier de fiches
courant**, l'**artefact du chantier**, l'**artefact feuille de route**.

Si `CHANTIER.md` n'existe pas, le projet n'est pas équipé : dis-le, propose
`/vlp-init`, et arrête-toi. Rien d'autre n'a de sens sans lui.

## 2. Les six vérifications

Lance-les d'un bloc, puis commente la sortie ligne à ligne.

**A — Le fichier de fiches courant existe.**

```bash
ls -la "<fichier de fiches courant>" 2>&1; ls "<contexte>"/*.md
```

Une ligne « courant » qui nomme un fichier absent envoie chaque `/tache` dans
le vide. Une ligne « aucun » alors qu'un fichier de chantier récent n'est pas
clos est l'erreur inverse : un chantier orphelin, que plus rien ne rouvrira.

**B — Les fiches sont extractibles.**

```bash
grep -c '^<!-- FICHE:' "<fichier de fiches courant>"; grep -c '^<!-- /FICHE -->' "<fichier de fiches courant>"; grep -n '^## [A-Z][0-9]' "<fichier de fiches courant>"
```

Les trois comptes doivent concorder. Un marqueur ouvrant sans son fermant fait
que `sed` avale tout jusqu'à la fin du fichier — la fiche « extraite » serait
le chantier entier. Un titre sans marqueurs n'est pas extractible du tout.

**C — Les cases cochées et la page publiée disent la même chose.**

```bash
grep -n '^## [A-Z][0-9] \[x\]' "<fichier de fiches courant>" | wc -l
grep -c 'data-etat="faite"' "<artefact du chantier local>"
```

Le fichier a raison. Si les deux nombres diffèrent, **la page est en retard** :
dis-le, nomme les fiches concernées, et propose de la régénérer — sans le
faire tant que l'utilisateur n'a pas répondu.

**D — Les lettres de fiches ne se marchent pas dessus.**

```bash
grep -n 'Lettres prises' CHANTIER.md; ls "<contexte>"/*.md | sed 's/.*\///'
```

Chaque fichier de chantier consomme une lettre. Une lettre réutilisée fait que
`/tache D2` trouve deux fiches et en joue une au hasard.

**E — Le coût par session.**

```bash
awk '/^## Le socle/{f=1} f && /^## L.*ordre des fiches/{exit} f' "<fichier de fiches courant>" | wc -l
wc -l "<fichier de fiches courant>" "<artefact du chantier local>"
```

Repères : socle **≤ 80 lignes**, page de chantier **≤ 250 lignes**. Ces deux
là se relisent à *chaque* fiche : ce qu'ils portent en trop se paye autant de
fois qu'il reste de fiches. Au-delà, dis de combien et propose quoi retirer.

**F — Les URL sont écrites.**

Les deux lignes d'artefact de `CHANTIER.md` portent-elles une URL, ou encore
« aucun » ? Une URL non écrite n'est pas récupérable : la session suivante
publierait un doublon du même nom au lieu de mettre à jour la page.

Pour vérifier qu'une URL est vivante, `Artifact action:"read"` — **une seule**,
celle du chantier. Ne relis pas la feuille de route en même temps : le but est
de mesurer un coût, pas de le doubler.

## 3. Rendre le verdict

Une liste, une ligne par vérification : `A ✓` ou `A ✗ — <ce qui cloche>`.
Affiche **les comptes bruts à côté du verdict** : un contrôle qui dit « ✗ »
sans dire 4 contre 6 ne se diagnostique pas.

Puis les corrections proposées, **par ordre de gravité**, chacune en une ligne
avec le geste exact. Et rien de plus : c'est l'utilisateur qui décide laquelle
part, et dans quelle session.
