# Claude-vlpWorkflow — mener un gros chantier sans saturer le contexte

Un kit portable — **un seul exemplaire, à côté des projets**, jamais recopié
dedans. C'est un **plugin Claude Code** : il est chargé là où il est, il n'en
existe aucune copie. Il apporte cinq commandes, les gabarits de fichiers, et
la méthode qui les tient ensemble.

Le partage tient en une ligne : **le kit porte le moteur, le projet porte ses
données.** La méthode, la clôture et les gabarits restent ici et servent tous
les projets à la fois ; un projet ne garde que son `CHANTIER.md`, son état, ses
fichiers de fiches et ses pages publiées.

## Le problème qu'il résout

Une session d'assistant **relit tout son passé à chaque tour**. Un lot de
travail mené d'un seul tenant se paye donc de plus en plus cher à mesure qu'il
avance : la dernière heure coûte le prix de toutes les précédentes. Ce n'est
pas un problème de volume horaire, mais de **densité de contexte**.

La parade tient en une phrase :

> **Un chantier s'écrit une fois en fiches, puis chaque fiche s'exécute dans sa
> propre session.**

## Les trois temps

- **Cadrage** — `/vlp:chantier`, une session qui **ne code pas** : elle propose
  les chantiers possibles, questionne, découpe en fiches, puis rend la main.
- **Exécution** — `/vlp:tache R1`, `/clear`, `/vlp:tache R2`… Une fiche par
  session, jamais deux. `/vlp:enchainer` les joue à la suite, chacune dans un
  sous-agent neuf — commode, mais plus cher en tokens qu'à la main.
- **Clôture** — à la dernière case cochée, le chantier est marqué clos et ne se
  rejoue plus.

`/vlp:check` vérifie un projet sans rien écrire. Deux pages publiées suivent
l'avancement, lisibles depuis un téléphone ; elles ne sont jamais la vérité,
les fichiers du projet le restent.

La méthode entière — anatomie d'une fiche, préfixes, où vit quoi — est dans
`methode-chantier.md` ; les pages publiées, dans `ARTEFACTS.md`.

## Installer — un lien, et c'est tout

**1. Récupérer le kit**, une fois, **à côté** des projets, jamais dedans :

```bash
git clone https://github.com/SebastienGrana/Claude-vlpWorkFlow.git
```

```
ProgPerso/
  Claude-vlpWorkflow/   <- le kit, une fois
  MonProjet/            <- les projets, à côté
```

Pour modifier le kit : `git config core.hooksPath .githooks` dans le clone, et
chaque commit passe par `claude plugin validate`.

**2. Le déclarer à Claude Code**, une fois par machine. Un dossier posé dans
`~/.claude/skills/` et portant un `.claude-plugin/plugin.json` se charge tout
seul, dans tous les projets ; ce dossier peut être un **lien** vers le kit —
donc rien n'est copié.

Sur Windows (PowerShell, sans droits administrateur) :

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\vlp" -Target "<chemin>\Claude-vlpWorkflow"
```

Sur macOS ou Linux :

```bash
ln -s "<chemin>/Claude-vlpWorkflow" ~/.claude/skills/vlp
```

Les commandes deviennent `/vlp:init`, `/vlp:chantier`, `/vlp:tache`,
`/vlp:enchainer` et `/vlp:check`, avec l'agent `vlp:fiche`. Le préfixe `vlp:`
évite qu'un `/tache` d'ailleurs prenne la place du tien. **Si tu déplaces le
kit**, refais le lien ; `/vlp:check` dira quels `CHANTIER.md` le citent encore
à l'ancien endroit.

**3. Équiper le projet** : une session ouverte **dans le dossier du projet**,
puis `/vlp:init`. Sept questions, à préparer :

1. le projet en une phrase — ce qu'il fait, ce qu'il ne fait pas ;
2. un alias court (`md`, `cairn`, `api`) — il ne sert que dans un workspace ;
3. le nom du dossier de contexte (`context AI/` par défaut) ;
4. la **livraison** : la commande qui met le code en place, ou « aucune » ;
5. la **vérification** : une commande que la session lance et lit elle-même,
   ou un geste que seul l'utilisateur peut faire ;
6. trois ou quatre **contraintes d'écriture** propres au projet ;
7. les **chantiers qu'on voit venir** : deux à cinq, une ligne chacun.

`CHANTIER.md`, `CLAUDE.md` et le dossier de contexte sont posés, la feuille de
route est publiée. Puis `/clear`, et `/vlp:chantier`. Sans commande, le même
résultat s'obtient en instanciant soi-même les gabarits de `templates/`.

## Vérifier que ça marche

Depuis le dossier du projet, `/vlp:chantier` doit annoncer le projet **sans
rien demander**. S'il demande lequel, `CHANTIER.md` n'est pas à la racine, ou
la session a été ouverte au niveau du workspace. Plus tard, au moindre doute —
page qui ne ressemble plus au fichier, session interrompue —, `/vlp:check`
mesure et compare, et propose des corrections sans rien écrire.

## Quand le kit change

Tu édites le fichier dans le kit, et c'est fini : **rien à synchroniser**, il
n'y a pas de copie. `/reload-plugins` pour que la session en cours le voie ;
sinon la suivante le verra d'elle-même.

## Dans un workspace, plusieurs projets équipés

Chaque projet porte son `CHANTIER.md` à sa racine. Les commandes le cherchent
en remontant depuis le dossier courant, puis d'un cran plus bas :

- session ouverte **dans le projet**, ou dans un workspace à un seul projet
  équipé → `/vlp:tache R3`, rien à préciser ;
- plusieurs projets équipés → elles demandent lequel, ou acceptent l'alias :
  `/vlp:tache cairn N2` ;
- aucun `CHANTIER.md` → elles renvoient vers `/vlp:init`.

## Ce qu'il y a dans le dossier

```
.claude-plugin/            LE MANIFESTE — plugin.json (nom, version), marketplace.json
commands/                  LE MOTEUR — init, chantier, tache, enchainer, check
agents/fiche.md            le sous-agent qui joue une fiche pour /vlp:enchainer
hooks/hooks.json           valide un fichier de fiches à chaque écriture
scripts/                   LA MÉCANIQUE — Python sans dépendance, zéro appel modèle
  vlp.py                   carte, extraire, socle, valider, page… (docstring)
  mesure-tokens.py         le coût en tokens d'une session, en comptes bruts
references/                les morceaux partagés que les commandes lisent
methode-chantier.md        LA DOCTRINE, et où vit quoi — lue depuis le kit, jamais recopiée
cloture.md                 les cinq écritures d'une clôture, décrites une fois
enchainement.md            le contrat de retour d'une fiche enchaînée, décrit une fois
ARTEFACTS.md               les deux pages publiées : nommage, URL, budget
templates/                 LES GABARITS — instanciés dans un projet
archive/                   ce qui a servi et ne sert plus — gardé, pas supprimé
exemples/                  un CHANTIER.md visuel, un scriptable, un extrait de fiches
```
