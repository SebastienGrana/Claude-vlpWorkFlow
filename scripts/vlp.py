#!/usr/bin/env python3
"""La mécanique du kit vlp : ce que les commandes faisaient au `sed` et à l'`awk`.

Sous-commandes :

- `carte [dossier]` — la carte d'un projet, à injecter avant le 1er tour d'une
  commande. Remonte jusqu'au premier `CHANTIER.md`. Trouvé : `PROJET=<racine>`,
  le fichier en entier, puis — si un fichier de fiches est courant — ses titres
  de fiches numérotés, `PROCHAINE=<fiche>` (la première non cochée, dans l'ordre
  du fichier) ou `PROCHAINE=aucune`, et une `GARDE` si le fichier a des lignes
  mais aucun titre au format attendu. Pas trouvé : une ligne `VOISIN=` par
  sous-dossier équipé, avec son alias, ou `AUCUN_PROJET`. Sort toujours 0 : la
  commande lit la sortie, elle ne doit pas se faire refuser l'injection.
  `--python NOM` : une ligne vide, `PYTHON=NOM`, puis la carte, et un tampon dans
  le dossier temporaire ; `--relais` en plus : n'écrit rien si un tampon de moins
  de `RELAIS_SECONDES` existe (le premier Python a déjà répondu), sans le retirer.
- `extraire <fichier> <fiche>` — la fiche entre ses marqueurs, marqueurs
  compris, puis `--- fiche, lignes : N`. Sans marqueurs, repli sur le titre
  jusqu'au premier `---`, annoncé par une `GARDE`. Absente : sort 1. Critère
  `(visuel)` : une ligne `ARRÊT:` avant le compte.
- `socle <fichier>` — de `## Le socle commun` (compris) à `## L'ordre des
  fiches` (exclu), puis `--- socle, lignes : N`. Vide : sort 1.
- `sessions <fichier>` — un id de ligne `**Session**` par ligne, dédoublonnés,
  dans l'ordre du fichier.
- `cout <fichier> [--session]` — `mesure-tokens.py` sur toutes les sessions du
  fichier, celles des fiches et celle du cadrage, que `ouvrir` note en tête (aucune :
  `SESSIONS 0 — pas de total`, sort 0), coupées aux commits comme la page : `DÉCOUPE
  aux commits de fiche`, une ligne par fiche, `hors fiches`, `TOTAL (fiches + hors
  fiches)` — aucun tour gardé : `GARDE: découpe à zéro`. Sans Git, sans commit qui
  nomme le préfixe, ou clos sans commit de fiche : `DÉCOUPE aucune — <raison>`, puis
  les tables des sessions entières. `--session` : `SESSION=<CLAUDE_CODE_SESSION_ID>`,
  puis (id non vide) la table de cette session seule, et celle de cette session plus
  celles du fichier.
- `valider <fichier>… [--plan]` — les écarts d'un fichier de fiches, un par ligne
  `fichier:ligne: message`, puis `VALIDE|INVALIDE <n> fiches · socle <n> lignes
  · <n> écarts · <n> avertissements — <fichier>`. Avertit si une fiche ou le
  socle dépasse son seuil. Un écart : sort 1. `--plan` : ensuite, `<n>:<ligne>`
  pour chaque titre de fiche, `**Dépend de**`, `**Tentatives**`, `**Critère de fin**`.
- `lignes <chemin>…` — `<n> <fichier>`, `DOSSIER <d>` (` → <réel>` si lien) ou
  `ABSENT <chemin>` ; `~` et `*` développés ; puis `SEUILS page · fiche · socle`. Sort 0.
- `equiper <dossier> [--contexte C]` — ce que `/vlp:init` regarde : `DOSSIER=`,
  les 20 premiers sous-dossiers `nom/` (sans les cachés), `CLAUDE.md` s'il est
  là, les lignes `PROJET=`, `VOISIN=`, `AUCUN_PROJET` de la carte, et `ETAT=`
  pour `<dossier>/C` (défaut `context AI`). Sort 0.
- `lire <chemin>…` — imprime des fichiers du kit, chemins relatifs à sa racine
  (le parent de `scripts/`) : remplace un `cat` hors du projet, que PowerShell
  refuse. Hors du kit : `GARDE:` ; absent : `ABSENT <chemin>` ; l'un ou l'autre
  sort 1, les autres fichiers sont imprimés.
- `cocher <fichier> <fiche> [--resolu T] [--date D] [--verifier | --refuser M]` — `[ ]` → `[x]`
  sur le titre de la fiche et, si `CLAUDE_CODE_SESSION_ID` n'est pas vide, `**Session** : <id>`
  avant sa ligne `**Dépend de**` (déjà là : pas redoublée) ; `--resolu` réduit
  un bloc `**Tentatives**` à `**Tentatives** (<date>) — résolu par : T`.
  `COCHÉ <fiche> · Session <id|absente>`. Introuvable ou déjà cochée : `GARDE:`,
  rien écrit, sort 1. `--verifier` n'écrit rien, et rend `CASE <fiche> [x]` (sort 0) ou
  `CASE <fiche> [ ]` (sort 1) ; puis, si le sujet du dernier commit du dépôt du fichier commence
  par `<fiche>:` ou `<fiche> :` (le sous-agent a commité), `TÊTE <sha> <sujet>` et sort 1 ; hors d'un
  dépôt, `SANS GIT`, et la case seule décide. `--refuser M` (chantier REV) : `[x]` → `[ ]`, et
  sous le titre le bloc `**Tentatives** (<date>) — non résolu.`, `1. FAITE refusée à la
  relecture.`, `Erreur : M` ; déjà là, il gagne la ligne numérotée suivante et son `Erreur :`
  prend M, sans se doubler. `REFUSÉ <fiche>`.
- `relecture <fiche> [--sha S]` — ce que lit le relecteur de `/vlp:enchainer` (chantier REV). Sans
  `--sha`, un instantané de l'arbre — suivis et non suivis, selon `.gitignore` — en commit de parent
  `HEAD`, par un index temporaire : ni `HEAD` ni l'index ne bougent ; avec, ce commit. Deux worktrees
  détachés `vlp-relecture-*` dans le dossier temporaire, ceux d'un appel précédent retirés d'abord :
  APRÈS sur le commit, AVANT sur son parent. Imprime `APRÈS=`, `AVANT=`, `FICHIER=` (le fichier de
  fiches courant du `CHANTIER.md` d'APRÈS), le socle et la fiche comme `socle` et `extraire`,
  `git diff --name-status`, une ligne `HORS FICHE <chemin>` par fichier changé que la ligne
  **Fichiers** ne nomme pas — hors le fichier de fiches et `artefacts/` —, puis le diff. `--retirer` :
  retire ces worktrees, `RETIRÉ <n>`. Pas de dépôt, commit inconnu ou sans parent, fiche absente :
  `GARDE:`, aucun worktree ne reste, sort 1.
- `page <fichier> [<page.html>]` — régénère la page du chantier depuis le fichier
  de fiches : états, avancement, comptage, coûts (`**Session**`), date. Les coûts
  se coupent aux commits `<ID> :` (`git log`), sous-agents compris, plus une ligne
  « hors fiches » ; la session du cadrage, notée en tête par `ouvrir`, se coupe comme
  celles des fiches — ses tours d'avant l'ouverture vont hors fiches. Sans Git, sans
  commit qui nomme le préfixe, ou clos sans commit de fiche, ils se tirent de
  l'ancienne page. Sans page :
  `<dossier du fichier>/artefacts/<même nom>.html`. Garde de la page l'en-tête — sauf
  sa plage de fiches, refaite depuis le fichier —, les notes, le journal, le blocage
  et le bilan.
  `--note <fiche> <texte>`, `--journal <texte>` (répétables) ; `--creer
  --projet P --titre T --resultat R` part du gabarit ; `--verifier` n'écrit
  rien et sort 1 si états ou avancement diffèrent du fichier.
- `hook` — le hook `PostToolUse` (`Write|Edit`) du plugin : lit sur stdin le
  JSON du hook, prend `tool_input.file_path` (relatif : contre `cwd`). Sort 0
  muet si ce n'est pas un fichier de fiches — JSON illisible, chemin absent, pas
  `.md`, ou ni marqueur `<!-- FICHE:X1 -->` ni `## Le socle commun` hors bloc de
  code. Sinon `valider` : écart → écarts, bilan et consigne sur stderr, sort 2 ;
  valide → le JSON `hookSpecificOutput` dont `additionalContext` est le bilan,
  sort 0.
- `filet` — le hook `PostToolUse` du sous-agent : lit sur stdin le JSON du hook.
  Sort 0 muet si pas un sous-agent (`agent_id` absent, ou `agent_type` ne
  contient pas « fiche »), ou si le transcript du sous-agent est absent. Sinon
  compte les tours rendus et lit `maxTurns` d'`agents/fiche.md` ; si
  `tours_restants <= 3`, rend un JSON `hookSpecificOutput` avec l'avertissement,
  sort 0 ; sinon sort 0 muet.
- `etat <contexte>` — `ETAT=<NN>-etat.md` : le fichier d'état déjà présent,
  sinon le premier nombre à deux chiffres libre après le plus grand (`01` si le
  dossier est vide ou absent). Sort 0.
- `renvois <projet>` — les fichiers que l'index (1re cellule de ses tables) et
  le routage de `CLAUDE.md` (dernière cellule) nomment entre accents graves et
  qui n'existent ni contre le dossier de contexte ni contre la racine : une
  ligne `ABSENT: <source>:<ligne>: <nom>` chacun, puis `RENVOIS <n> nommés ·
  <n> absents`. Ignorés : un nom à `<…>` ou `*`, sans `.`, une ligne dont la 1re
  cellule commence par `*(`. Un absent : sort 1. Avant `RENVOIS`, une ligne
  `AVERTISSEMENT: <fichier> <n> lignes > <seuil>` par fichier de tête au-delà
  de son seuil, puis `POIDS CLAUDE.md <n>/<seuil> · CHANTIER.md <n>/<seuil> ·
  index <n>/<seuil>` (`absent` pour <n>) ; un poids ne change pas la sortie.
- `niveau <projet>` — en quoi un projet équipé a dérivé du kit ; n'écrit rien.
  Agrège `renvois` (renvois absents en écarts, poids en avertissements, la ligne
  `POIDS` telle quelle), `feuille --verifier` et, si un fichier de fiches est
  courant, `page --verifier` ; ajoute ce que rien ne voyait : un `${…}` cité sur
  une ligne de champ ou de table de `CHANTIER.md`, de l'index ou du fichier
  d'état, et la table des chantiers clos restée dans `CHANTIER.md`. Compte le
  Markdown resté brut de la feuille régénérée, toujours sur une ligne `MARKDOWN
  <n> ** · <n> liens Markdown · <n> liens cassés — <page>` : un écart s'il n'est
  pas nul. Une copie locale de `methode-chantier.md` n'est pas un écart : la
  méthode la tolère pour un projet équipé avant la règle. Une ligne `ÉCART:
  <catégorie>: <phrase>`
  par écart (`renvois`, `feuille`, `page`, `variable`, `clos`), puis `NIVEAU <n>
  écarts · <n> avertissements — <projet>`. Un écart : sort 1.
  `--ecrire` corrige les seuls écarts mécaniques — la table des chantiers clos
  retirée de `CHANTIER.md` (jamais si l'index ne nomme pas chacun de ses
  fichiers), la feuille de route posée depuis le gabarit puis régénérée, le
  bloc repliable des clos posé sur une feuille d'avant le 2026-09-17, et les
  lignes closes écrites avant `gras_et_liens` converties en place. Les
  renvois absents et les fichiers de tête hors seuil restent en `ÉCART:`. Tout
  se calcule avant la première écriture. Bilan `NIVEAU <n> corrigés · <n> à la
  main — <projet>` ; un écart restant : sort 1. `--date` fige la date.
- `feuille <projet> [--todo N] [--verifier]` — régénère dans
  `<contexte>/artefacts/feuille-de-route.html` la `ZONE:encours` (depuis le
  fichier de fiches courant et l'artefact du chantier), la `ZONE:todo` (depuis
  la TODO du fichier d'état ; `--todo N` y pose le badge « en cours », gardé
  d'un appel à l'autre tant qu'un chantier est ouvert) et les lettres prises du
  pied (plus celle du chantier courant) ; la date seulement si la page change.
  `FEUILLE todo <n> · encours <oui|non> · lettres <n> · <réécrite|inchangée>
  — <page>`. `--verifier` n'écrit rien, dit `identique|écart`, sort 1 sur écart.
- `clore <projet> --livre T [--tokens N] [--abandon T] [--fait T] [--surpris T]
  [--date D]` — les écritures mécaniques de `cloture.md` : `**CLOS**` (et les
  abandonnées) dans le fichier de fiches courant, et `**Fait.** L1..Ln (date) :
  <fait, sinon livre>` à la place de `**Fait.**` ou `**Où on en est.**` ; la
  ligne ouverte de l'index passée à « clos » ; la ligne « jouer une fiche » du
  routage de `CLAUDE.md` retirée, et `| relire un chantier clos | <index> |`
  posée à sa place si elle manque ;
  dans la page du chantier, `ZONE:bilan` visible (Livré, Surpris) et coûts régénérés,
  `ZONE:blocage` cachée — absentes : `GARDE:`, le reste est écrit ; avec
  `--resume T`, dans « Où on en est » de `CLAUDE.md`, `- Clos le <date> : T
  (chantier L).` (déjà là : rien), et seules les `CLOS_GARDES` dernières lignes de
  cette forme restent ; dans `CHANTIER.md`, courant et artefact à `aucun`,
  la lettre aux lettres prises (plus de table des clos) ; dans la feuille
  de route, une ligne en tête de `ZONE:clos`, le total cumulé resommé des
  comptes bruts, puis `feuille`. Tout est calculé avant la première écriture.
  `CLOS <lettre> <plage> · total <brut> · routage <0|1> · index <0|1> · bilan
  <0|1> — <projet>`. Aucun chantier ouvert, ou
  déjà `**CLOS**` : `GARDE:`, sort 1.
- `ouvrir <projet> --fiches F --titre T [--artefact URL]` — les écritures
  mécaniques de l'ouverture : dans `CHANTIER.md`, courant = `F (L1..Ln)` et
  artefact = l'URL (sinon `aucun`, ou l'ancienne si F est déjà courant) ; une
  ligne « on joue une fiche » après la ligne de l'index au plus grand numéro ;
  une ligne « jouer une fiche du chantier » avant « relire un chantier clos »
  (sinon le premier « relire le chantier ») du routage de `CLAUDE.md`. Une ligne
  déjà là n'est pas redoublée ; relancé sur F, seule la plage de sa ligne
  d'index `**ouvert**` suit le fichier. `CLAUDE_CODE_SESSION_ID` non vide et sur
  aucune ligne `**Session**` du fichier : `**Session** : <id>` avant sa première
  ligne `## ` — la session du cadrage, que `cout` et `page` mesurent. `OUVERT
  <lettre> <plage> · index <+n|~1> · routage +<n> · session +<0|1> · artefact <url>
  — <projet>` (`~1` : plage refaite) ; index ou routage introuvable : `GARDE:`, le
  reste est écrit.
  Un autre chantier déjà ouvert, ou F porte `**CLOS**` : `GARDE:`, sort 1.

Python 3 sans dépendance, zéro appel modèle.
"""
import argparse
import glob
import io
import json
import os
import re
import sys

TITRE = re.compile(r"^## [A-Z]{1,3}[0-9]")
PREFIXE = re.compile(r"^[A-Z]{1,3}")
COURANT = re.compile(r"^\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*(.+?)\s*$")
ALIAS = re.compile(r"^\s*-\s*\*\*alias\*\*\s*:\s*(\S+)")
SESSION = re.compile(r"^\*\*Session\*\* : (.+?)\s*$")
FERMANT = "<!-- /FICHE -->"


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def lignes_de(chemin):
    lignes = lire(chemin).split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()
    return lignes


class Absent(ValueError):
    """Un chemin nommé par `CHANTIER.md` ne désigne pas de fichier. Sous-classe
    de `ValueError` : les `except ValueError` qui gardent déjà leur contexte la
    voient ; sinon `main` l'attrape — c'est le seul endroit où la règle vit."""


def chemin_garde(chemin, libelle="fichier", nom=None):
    """Le chemin, ou `Absent` : le point unique où un chemin venu de
    `CHANTIER.md` est vérifié. `nom` : ce qu'on montre quand le relatif parle
    mieux que l'absolu."""
    if not os.path.isfile(chemin):
        raise Absent("%s introuvable : %s" % (libelle, nom or chemin))
    return chemin


def lignes_gardees(chemin, libelle="fichier", nom=None):
    """Les lignes d'un chemin gardé : toute lecture d'un chemin de `CHANTIER.md`
    passe par ici."""
    return lignes_de(chemin_garde(chemin, libelle, nom))


def lignes_du_projet(projet, chemin_relatif, libelle):
    """Les lignes d'un chemin relatif au projet, gardées."""
    return lignes_gardees(os.path.join(projet, chemin_relatif), libelle, chemin_relatif)


# --- carte -------------------------------------------------------------------

def equipe(d):
    """Vrai si `d` porte `CHANTIER.md` à la casse exacte : sous Windows et
    macOS, `isfile` prendrait un `chantier.md` pour la carte."""
    try:
        return "CHANTIER.md" in os.listdir(d) and os.path.isfile(os.path.join(d, "CHANTIER.md"))
    except OSError:
        return False


def trouver(depart):
    d = os.path.abspath(depart)
    while True:
        if equipe(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def fichier_courant(carte_texte):
    """Le chemin du fichier de fiches courant, ou None s'il vaut « aucun »."""
    for ligne in carte_texte.split("\n"):
        m = COURANT.match(ligne)
        if m:
            valeur = re.sub(r"\s+\([^)]*\)$", "", m.group(1)).strip()
            return None if valeur.lower().startswith("aucun") else valeur
    return None


def fiches(chemin):
    """(nombre de lignes, [(numéro, titre)], prochaine ou None)."""
    lignes = lignes_de(chemin)
    titres = [(i, l) for i, l in enumerate(lignes, 1) if TITRE.match(l)]
    prochaine = next((l.split()[1] for _, l in titres if "[x]" not in l), None)
    return len(lignes), titres, prochaine


def carte(depart, sortie):
    racine = trouver(depart)
    if racine is None:
        voisins = sorted(os.path.join(v, "CHANTIER.md") for v in glob.glob(os.path.join(os.path.abspath(depart), "*"))
                         if equipe(v))
        for v in voisins:
            m = next((ALIAS.match(l) for l in lire(v).split("\n") if ALIAS.match(l)), None)
            sortie.write("VOISIN=%s alias=%s\n" % (os.path.dirname(v), m.group(1) if m else "?"))
        if not voisins:
            sortie.write("AUCUN_PROJET\n")
        return 0
    texte = lire(os.path.join(racine, "CHANTIER.md"))
    sortie.write("PROJET=%s\n--- CHANTIER.md ---\n%s" % (racine, texte))
    if not texte.endswith("\n"):
        sortie.write("\n")
    courant = fichier_courant(texte)
    if courant is None:
        sortie.write("--- fichier de fiches courant : aucun ---\n")
        return 0
    try:
        n, titres, prochaine = fiches(chemin_garde(os.path.join(racine, courant),
                                                  "fichier de fiches", courant))
    except Absent as e:
        # `cmd_equiper` appelle `carte` en direct : elle garde, elle ne lève pas.
        sortie.write("GARDE: %s\n" % e)
        return 1
    sortie.write("--- fiches : %s (%d lignes, %d titres) ---\n" % (courant, n, len(titres)))
    for i, l in titres:
        sortie.write("%d:%s\n" % (i, l))
    if n and not titres:
        sortie.write("GARDE: aucun titre de fiche au format '## X1' — ne rien conclure\n")
        return 1
    sortie.write("PROCHAINE=%s\n" % (prochaine or "aucune"))
    return 0


RELAIS_SECONDES = 30


def carte_injectee(depart, python, relais, sortie):
    """La carte d'une injection `py … --python py 2>"…/relais-python.err"; python3 … --relais 2>…;
    py … --relais 2>…; echo fin` (chantier Y, Y1 ; ordre inversé en U4 : sous Windows le message du raccourci
    Store de `python3` tombe après la carte, sous Ubuntu « py: command not found » avant ; le 3e appel remet
    à 0 le `$LASTEXITCODE` de PowerShell, que `echo` ne touche pas) : une ligne vide d'abord,
    `PYTHON=<nom>` pour le corps de la skill, et rien au relais si le premier lancement a déjà écrit la carte.

    Le `2>"<fichier>"` de chaque appel (NIV1) : le lanceur absent parle avant que Python démarre, et son
    message entrait dans la carte injectée. `2>` vers un chemin est la seule écriture que PowerShell et bash
    lisent pareil — `2>$null` est une erreur de syntaxe sous bash, `2>/dev/null` un chemin `C:/dev/null` absent
    sous PowerShell. Le message n'est pas perdu : le 1er appel repart de zéro (`2>`), les deux suivants ajoutent (`2>>`),
    et `relais-python.err`, à la racine du plugin, garde la trace d'une injection entière."""
    import hashlib
    import tempfile
    import time
    cle = hashlib.sha1(os.path.abspath(depart).encode("utf-8")).hexdigest()[:16]
    tampon = os.path.join(tempfile.gettempdir(), "vlp-carte-%s" % cle)
    if relais:
        # Le tampon reste : le 3e appel de l'injection (`py … --relais`) doit se taire aussi.
        try:
            recent = time.time() - os.path.getmtime(tampon) < RELAIS_SECONDES
        except OSError:
            recent = False
        if recent:
            return 0
    else:
        try:
            with open(tampon, "w", encoding="utf-8") as f:
                f.write(python)
        except OSError:
            pass
    sortie.write("\nPYTHON=%s\n" % python)
    return carte(depart, sortie)


# --- extraire, socle, sessions -----------------------------------------------

def extraire_lignes(lignes, fiche):
    """(lignes de la fiche, garde ou None). Liste vide : fiche absente."""
    ouvrant = "<!-- FICHE:%s -->" % fiche
    debut = next((i for i, l in enumerate(lignes) if l.strip() == ouvrant), None)
    if debut is not None:
        # Un fermant oublié : `sed` avalait la fiche suivante sans rien dire.
        # On s'arrête au prochain marqueur ouvrant, et on le dit.
        fin = next((i for i in range(debut + 1, len(lignes))
                    if lignes[i].strip() == FERMANT or lignes[i].startswith("<!-- FICHE:")), len(lignes))
        if fin == len(lignes) or lignes[fin].strip() != FERMANT:
            return lignes[debut:fin], "GARDE: marqueur fermant absent après %s — fiche lue jusqu'au marqueur suivant ou la fin" % ouvrant
        return lignes[debut:fin + 1], None
    titre = "## %s " % fiche
    debut = next((i for i, l in enumerate(lignes) if l.startswith(titre)), None)
    if debut is None:
        return [], None
    fin = next((i for i in range(debut + 1, len(lignes)) if lignes[i].rstrip() == "---"), len(lignes) - 1)
    return lignes[debut:fin + 1], "GARDE: pas de marqueurs pour %s — repli du titre au premier '---', un '---' dans un bloc de code le coupe" % fiche


def socle_lignes(lignes):
    debut = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), None)
    if debut is None:
        return []
    fin = next((i for i in range(debut + 1, len(lignes)) if re.match(r"^## L.*ordre des fiches", lignes[i])), len(lignes))
    return lignes[debut:fin]


def sessions_de(lignes):
    vues = []
    for l in lignes:
        m = SESSION.match(l)
        if m and m.group(1) not in vues:
            vues.append(m.group(1))
    return vues


def sessions_entete(lignes):
    """Les sessions de l'en-tête, avant le premier titre de fiche : le cadrage, que `ouvrir`
    note (chantier CAD)."""
    k = next((i for i, l in enumerate(lignes) if TITRE.match(l)), len(lignes))
    return sessions_de(lignes[:k])


def cmd_extraire(chemin, fiche, sortie):
    extrait, garde = extraire_lignes(lignes_de(chemin), fiche)
    if garde:
        sortie.write(garde + "\n")
    if not extrait:
        sortie.write("GARDE: fiche introuvable : %s\n--- fiche, lignes : 0\n" % fiche)
        return 1
    sortie.write("\n".join(extrait) + "\n")
    if any(CRITERE_VISUEL.match(l) for l in extrait):
        # Le sous-agent de /vlp:enchainer a rendu FAITE sur une fiche visuelle (P3) :
        # la consigne vient du script, pas de sa mémoire. Pas GARDE: — vlp:jouer
        # rendrait RETOUR avant tout travail.
        sortie.write(ARRET + "\n")
    sortie.write("--- fiche, lignes : %d\n" % len(extrait))
    return 0


def cmd_socle(chemin, sortie):
    extrait = socle_lignes(lignes_de(chemin))
    if extrait:
        sortie.write("\n".join(extrait) + "\n")
    sortie.write("--- socle, lignes : %d\n" % len(extrait))
    return 0 if extrait else 1


def cmd_sessions(chemin, sortie):
    for s in sessions_de(lignes_de(chemin)):
        sortie.write(s + "\n")
    return 0


def cmd_cout(chemin, session, sortie):
    """Le coût du fichier de fiches, coupé aux commits comme la page : une ligne par fiche
    (`ligne_parts`), puis hors fiches, puis `TOTAL`. Sans heures de commit, les tables
    brutes de `mesure-tokens.py` sur les sessions entières, sous une ligne qui dit pourquoi.
    `--session` met d'abord la table de la session courante, pour `/vlp:tache`. Sans `tr` ni
    `xargs` : les commandes du kit tournent aussi sous PowerShell (chantier Y)."""
    import contextlib
    lignes = lignes_de(chemin)
    ids = sessions_de(lignes)
    code = 0
    if session:
        s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
        sortie.write("SESSION=%s\n" % s)
        if not s:
            return 0
        with contextlib.redirect_stdout(sortie):
            code = mesure().main([s]) or 0
        ids = [s] + [i for i in ids if i != s]
    elif not ids:
        sortie.write("SESSIONS 0 — pas de total\n")
        return 0
    fiches_ = fiches_du_fichier(lignes)
    pourquoi, gardes = [], []
    heures = heures_commits(chemin, [f[0] for f in fiches_], pourquoi,
                            any(l.startswith("**CLOS**") for l in lignes))
    decoupe = heures and parts_aux_commits(fiches_, heures, gardes, sessions_entete(lignes))
    for g in gardes:
        sortie.write(g + "\n")
    if not decoupe:
        if heures:
            pourquoi.append("aucune session de fiche mesurée")
        sortie.write("DÉCOUPE aucune — %s : sessions entières, sous-agents compris\n" % pourquoi[0])
        with contextlib.redirect_stdout(sortie):
            return mesure().main(ids) or code
    parts, hors = decoupe
    sortie.write("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                 "un sous-agent compte à son départ\n")
    for ident, s_, a_ in parts:
        sortie.write(ligne_parts(ident, s_, a_) + "\n")
    sortie.write(ligne_parts("hors fiches", *hors) + "\n")
    sortie.write(ligne_parts("TOTAL (fiches + hors fiches)", plus(*[p[1] for p in parts], hors[0]),
                             plus(*[p[2] for p in parts], hors[1])) + "\n")
    return code


KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_lire(chemins, sortie):
    """Un `cat` d'un fichier du kit est hors du projet : PowerShell le refuse
    (chantier U). Python, lui, est permis par `allowed-tools`."""
    racine = os.path.realpath(KIT)
    code = 0
    for c in chemins:
        vrai = os.path.realpath(os.path.join(racine, c))
        if os.path.commonpath([racine, vrai]) != racine:
            sortie.write("GARDE: hors du kit : %s\n" % c)
            code = 1
        elif not os.path.isfile(vrai):
            sortie.write("ABSENT %s\n" % c)
            code = 1
        else:
            texte = lire(vrai)
            sortie.write(texte if texte.endswith("\n") else texte + "\n")
    return code


def cmd_cocher(a, sortie):
    """La coche et la ligne Session en une écriture : l'id vient de
    l'environnement, pas d'un `$env:` que PowerShell refuse (chantier U)."""
    lignes = lignes_de(a.fichier)
    titre = "## %s [" % a.fiche
    debut = next((i for i, l in enumerate(lignes) if l.startswith(titre)), None)
    if debut is None:
        sortie.write("GARDE: fiche introuvable : %s\n" % a.fiche)
        return 1
    if a.verifier:
        cocher = lignes[debut].startswith("## %s [x]" % a.fiche)
        sortie.write("CASE %s [%s]\n" % (a.fiche, "x" if cocher else " "))
        # La tête du dépôt (chantier REV) : un dernier commit qui nomme la fiche est celui du
        # sous-agent — `VAL1:` compris, que `COMMIT_FICHE` laisse passer.
        dossier = os.path.dirname(os.path.abspath(a.fichier))
        if git_texte(["rev-parse", "--git-dir"], dossier)[0] != 0:
            sortie.write("SANS GIT\n")
            return 0 if cocher else 1
        code, tete = git_texte(["log", "-1", "--format=%h %s"], dossier)
        sha, _, sujet = tete.strip().partition(" ") if code == 0 else ("", "", "")
        if re.match(r"%s\s*:" % re.escape(a.fiche), sujet):
            sortie.write("TÊTE %s %s\n" % (sha, sujet))
            return 1
        return 0 if cocher else 1
    if a.refuser is not None:
        return refuser(a, lignes, debut, sortie)
    if not lignes[debut].startswith("## %s [ ]" % a.fiche):
        sortie.write("GARDE: %s déjà cochée — rien écrit\n" % a.fiche)
        return 1
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    lignes[debut] = lignes[debut].replace("[ ]", "[x]", 1)
    if a.resolu:
        t = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Tentatives**")), None)
        if t is not None:
            n = next((i for i in range(t + 1, fin) if not lignes[i].strip() or lignes[i].startswith("**")), fin)
            date = a.date or __import__("datetime").date.today().isoformat()
            lignes[t:n] = ["**Tentatives** (%s) — résolu par : %s" % (date, a.resolu)]
            fin -= n - t - 1
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if s and "**Session** : %s" % s not in lignes[debut:fin]:
        dep = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Dépend de**")), debut + 1)
        lignes.insert(dep, "**Session** : %s" % s)
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("COCHÉ %s · Session %s\n" % (a.fiche, s or "absente"))
    return 0


def refuser(a, lignes, debut, sortie):
    """Le refus du relecteur (chantier REV) : la case rouverte, et sous le titre le bloc de
    `tache-blocage.md` — déjà là, il gagne la ligne numérotée suivante et son `Erreur :` prend
    le nouveau motif ; il ne se double jamais."""
    fin = next((i for i in range(debut + 1, len(lignes))
                if lignes[i].strip() == FERMANT or TITRE.match(lignes[i])), len(lignes))
    lignes[debut] = lignes[debut].replace("[x]", "[ ]", 1)
    date = a.date or __import__("datetime").date.today().isoformat()
    essai, erreur = "FAITE refusée à la relecture.", "Erreur : %s" % a.refuser
    bloc = next((i for i in range(debut + 1, fin) if lignes[i].startswith("**Tentatives**")), None)
    if bloc is None:
        # Sous le titre, après sa ligne vide s'il en a une — comme les blocs écrits à la main.
        k = debut + 2 if debut + 1 < fin and not lignes[debut + 1].strip() else debut + 1
        lignes[k:k] = (["**Tentatives** (%s) — non résolu." % date, "1. " + essai, erreur]
                       + ([""] if k == debut + 2 else []))
    else:
        n = next((i for i in range(bloc + 1, fin) if not lignes[i].strip() or lignes[i].startswith("**")), fin)
        if "non résolu" not in lignes[bloc]:
            lignes[bloc] = "**Tentatives** (%s) — non résolu." % date
        numeros = [i for i in range(bloc + 1, n) if re.match(r"[0-9]+\. ", lignes[i])]
        p = numeros[-1] + 1 if numeros else bloc + 1
        suivant = int(lignes[numeros[-1]].split(".")[0]) + 1 if numeros else 1
        lignes.insert(p, "%d. %s" % (suivant, essai))
        e = next((i for i in range(p + 1, n + 1) if lignes[i].startswith("Erreur :")), None)
        if e is None:
            lignes.insert(p + 1, erreur)
        else:
            lignes[e] = erreur
    with open(a.fichier, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n")
    sortie.write("REFUSÉ %s\n" % a.fiche)
    return 0


# --- relecture ---------------------------------------------------------------

RELECTURE = "vlp-relecture-"    # le préfixe des worktrees de relecture : `--retirer` ne retire qu'eux


def git_texte(args, cwd, env=None):
    """(code, texte) de `git <args>` dans `cwd` : la sortie si le code vaut 0, sinon la première ligne
    d'erreur. Git qui ne se lance pas : (None, raison) — jamais un traceback."""
    import subprocess
    try:
        r = subprocess.run([GIT, "-c", "core.quotepath=false"] + args, cwd=cwd, env=env, capture_output=True,
                           encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git ne se lance pas : %s" % e
    if r.returncode:
        return r.returncode, ((r.stderr or "").strip().splitlines() or ["code %d" % r.returncode])[0]
    return 0, r.stdout


def retirer_relectures(racine):
    """Retire les worktrees `vlp-relecture-*` du dépôt, puis `prune` : le nombre retiré."""
    code, liste = git_texte(["worktree", "list", "--porcelain"], racine)
    n = 0
    for ligne in liste.splitlines() if code == 0 else []:
        chemin = ligne[len("worktree "):] if ligne.startswith("worktree ") else ""
        if os.path.basename(chemin.rstrip("/\\")).startswith(RELECTURE):
            n += git_texte(["worktree", "remove", "--force", chemin], racine)[0] == 0
    git_texte(["worktree", "prune"], racine)
    return n


def instantane(racine):
    """(code, sha) : l'arbre de travail — suivis et non suivis, selon `.gitignore` — en commit de
    parent `HEAD`, par un index temporaire : ni `HEAD` ni l'index réel ne bougent."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="vlp-index-") as d:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(d, "index"))
        for args in (["read-tree", "HEAD"], ["add", "-A"], ["write-tree"]):
            code, arbre = git_texte(args, racine, env)
            if code != 0:
                return code, arbre
    # Une identité à lui : l'instantané ne dépend pas de la configuration du poste.
    env = dict(os.environ, GIT_AUTHOR_NAME="vlp", GIT_AUTHOR_EMAIL="vlp@relecture",
               GIT_COMMITTER_NAME="vlp", GIT_COMMITTER_EMAIL="vlp@relecture")
    return git_texte(["commit-tree", arbre.strip(), "-p", "HEAD", "-m", "vlp relecture : instantané"], racine, env)


def noms_fichiers(fiche):
    """Ce que nomme la ligne **Fichiers** d'une fiche, jusqu'à la ligne vide ou au champ suivant :
    chaque `…` entre backticks, et chaque mot hors d'eux — le gabarit n'en met pas."""
    k = next((i for i, l in enumerate(fiche) if l.startswith("**Fichiers**")), None)
    if k is None:
        return set()
    para = [fiche[k][len("**Fichiers**"):]]
    for l in fiche[k + 1:]:
        if not l.strip() or l.startswith(("**", "<!--")):
            break
        para.append(l)
    texte = " ".join(para)
    return (set(re.findall(r"`([^`]+)`", texte))
            | set(re.split(r"[\s,;:()]+", re.sub(r"`[^`]*`", " ", texte)))) - {""}


def nomme(chemin, noms):
    """Vrai si `chemin` (relatif au dépôt, en `/`) est nommé : égal, fin de chemin après un `/`
    (`vlp.py` pour `scripts/vlp.py`), ou sous un dossier nommé (`templates/`)."""
    return any(chemin == n or chemin.endswith("/" + n) or (n.endswith("/") and "/" + n in "/" + chemin)
               for n in noms)


def cmd_relecture(a, sortie):
    """La relecture d'une fiche (chantier REV) : ce qu'en dit la docstring du module."""
    import tempfile
    projet = trouver(os.getcwd())
    code, racine = git_texte(["rev-parse", "--show-toplevel"], projet or os.getcwd())
    if code != 0:
        sortie.write("GARDE: pas de dépôt Git — %s\n" % racine)
        return 1
    racine = racine.strip()
    if a.retirer:
        sortie.write("RETIRÉ %d\n" % retirer_relectures(racine))
        return 0
    if not a.fiche or projet is None:
        sortie.write("GARDE: %s\n" % ("relecture <fiche> [--sha S], ou relecture --retirer" if not a.fiche
                                      else "pas de CHANTIER.md au-dessus de %s" % os.getcwd()))
        return 1
    retirer_relectures(racine)
    if a.sha:
        code, sha = git_texte(["rev-parse", "--verify", "--quiet", a.sha + "^{commit}"], racine)
        pourquoi = "commit inconnu : %s" % a.sha
    else:
        code, sha = instantane(racine)
        pourquoi = "instantané impossible — %s" % sha
    if code != 0:
        sortie.write("GARDE: %s\n" % pourquoi)
        return 1
    sha = sha.strip()
    code, parent = git_texte(["rev-parse", "--verify", "--quiet", sha + "^"], racine)
    if code != 0:
        sortie.write("GARDE: commit sans parent : %s\n" % sha[:12])
        return 1
    parent = parent.strip()
    dossiers = []
    for nom, rev in (("apres", sha), ("avant", parent)):
        d = tempfile.mkdtemp(prefix=RELECTURE + nom + "-")
        code, err = git_texte(["worktree", "add", "--detach", d, rev], racine)
        dossiers.append(d)
        if code != 0:
            retirer_relectures(racine)
            sortie.write("GARDE: worktree %s impossible — %s\n" % (nom, err))
            return 1
    # Le fichier de fiches que nomme CHANTIER.md dans APRÈS, au même endroit du dépôt que le projet.
    code, prefixe = git_texte(["rev-parse", "--show-prefix"], projet)
    prefixe = prefixe.strip() if code == 0 else ""
    apres_projet = os.path.normpath(os.path.join(dossiers[0], prefixe))
    courant = fichier_courant(lire(os.path.join(apres_projet, "CHANTIER.md"))) if equipe(apres_projet) else None
    fichier = os.path.normpath(os.path.join(apres_projet, courant)) if courant else ""
    fiche, _ = extraire_lignes(lignes_de(fichier) if os.path.isfile(fichier) else [], a.fiche)
    if not fiche:
        retirer_relectures(racine)
        sortie.write("GARDE: fiche %s absente du fichier de fiches courant d'APRÈS : %s\n" % (a.fiche, courant or "aucun"))
        return 1
    sortie.write("APRÈS=%s\nAVANT=%s\nFICHIER=%s\n" % (dossiers[0], dossiers[1], fichier))
    cmd_socle(fichier, sortie)
    cmd_extraire(fichier, a.fiche, sortie)
    code, etat = git_texte(["diff", "--name-status", "--no-color", parent, sha], racine)
    sortie.write(etat if code == 0 else "GARDE: git diff --name-status en échec — %s\n" % etat)
    fiches_rel, noms = prefixe + courant.replace("\\", "/"), noms_fichiers(fiche)
    for ligne in etat.splitlines() if code == 0 else []:
        chemin = ligne.split("\t")[-1]
        if chemin != fiches_rel and "/artefacts/" not in "/" + chemin and not nomme(chemin, noms):
            sortie.write("HORS FICHE %s\n" % chemin)
    code, diff = git_texte(["diff", "--no-color", "--no-ext-diff", parent, sha], racine)
    sortie.write(diff if code == 0 else "GARDE: git diff en échec — %s\n" % diff)
    return 0


def cmd_lignes(chemins, sortie):
    """`wc -l` et `ls` sans shell : une ligne par chemin (motif `*` et `~` compris)."""
    for motif in chemins:
        trouves = sorted(glob.glob(os.path.expanduser(motif))) or [os.path.expanduser(motif)]
        for c in trouves:
            if os.path.isdir(c):
                reel = os.path.realpath(c)
                sortie.write("DOSSIER %s%s\n" % (c, "" if os.path.normcase(reel) == os.path.normcase(os.path.abspath(c)) else " → " + reel))
            elif os.path.isfile(c):
                sortie.write("%d %s\n" % (len(lignes_de(c)), c))
            else:
                sortie.write("ABSENT %s\n" % motif)
    sortie.write("SEUILS page %d · fiche %d · socle %d\n" % (SEUIL_PAGE, SEUIL_FICHE, SEUIL_SOCLE))
    return 0


PLAN = re.compile(r"^## [A-Z]{1,3}[0-9]|^\*\*(Dépend de|Tentatives|Critère de fin)\*\*")


def cmd_equiper(dossier, contexte, sortie):
    """Ce que `/vlp:init` regarde avant d'équiper, sans `pwd`, `ls`, `head` ni `grep`."""
    d = os.path.abspath(dossier)
    sortie.write("DOSSIER=%s\n" % d)
    sous = sorted((n for n in os.listdir(d) if not n.startswith(".") and os.path.isdir(os.path.join(d, n))), key=str.lower)
    for n in sous[:20]:
        sortie.write("%s/\n" % n)
    if "CLAUDE.md" in os.listdir(d):
        sortie.write("CLAUDE.md\n")
    c = io.StringIO()
    carte(d, c)
    for l in c.getvalue().splitlines():
        if re.match(r"^(PROJET|VOISIN)=|^AUCUN_PROJET", l):
            sortie.write(l + "\n")
    sortie.write("ETAT=%s\n" % nom_etat(os.path.join(d, contexte)))
    return 0


# --- valider -----------------------------------------------------------------

OUVRANT = re.compile(r"^<!-- FICHE:(\S+) -->$")
CRITERE = "**Critère de fin**"
CRITERE_VISUEL = re.compile(r"^\*\*Critère de fin\*\* \(visuel\)")
ARRET = "ARRÊT: critère de fin (visuel) — livre, puis rends RETOUR sans cocher"
CODE_EN_LIGNE = re.compile(r"`[^`]*`")
# Les seuils vivent ici ; la doc dit « le seuil de vlp.py » et n'écrit pas le chiffre.
SEUIL_FICHE = 50
SEUIL_SOCLE = 80
# Fichiers de tête, lus à chaque session ou chaque fiche (mesure : chantier J, J1).
SEUIL_CLAUDE = 80
SEUIL_CHANTIER = 50
SEUIL_INDEX = 80
CLOS_GARDES = 5  # chantiers clos gardés dans « Où on en est » de CLAUDE.md


def valider_lignes(lignes):
    """(écarts, avertissements, nombre de fiches, lignes du socle) ; un écart
    ou un avertissement est un couple (numéro de ligne, message)."""
    ecarts, avert = [], []
    blocs = []          # (id du marqueur, début, fin) — indices 0
    ouvert = None       # (id, début)
    for i, l in enumerate(lignes):
        s = l.strip()
        m = OUVRANT.match(s)
        if m:
            if ouvert:
                ecarts.append((i + 1, "marqueur imbriqué : <!-- FICHE:%s --> ouvert ligne %d sans fermant"
                               % (ouvert[0], ouvert[1] + 1)))
                blocs.append((ouvert[0], ouvert[1], i - 1))
            ouvert = (m.group(1), i)
        elif s == FERMANT:
            if ouvert:
                blocs.append((ouvert[0], ouvert[1], i))
                ouvert = None
            else:
                ecarts.append((i + 1, "marqueur fermant sans ouvrant"))
    if ouvert:
        ecarts.append((ouvert[1] + 1, "marqueur ouvrant sans fermant : <!-- FICHE:%s -->" % ouvert[0]))
        blocs.append((ouvert[0], ouvert[1], len(lignes) - 1))

    titres = [(i, l.split()[1]) for i, l in enumerate(lignes) if TITRE.match(l)]
    vus, fiches_ = {}, []
    for n, (i, ident) in enumerate(titres):
        if ident in vus:
            ecarts.append((i + 1, "identifiant en double : %s (déjà ligne %d)" % (ident, vus[ident] + 1)))
        vus.setdefault(ident, i)
        bloc = next((b for b in blocs if b[1] < i <= b[2]), None)
        if bloc is None:
            ecarts.append((i + 1, "titre sans marqueurs : %s" % ident))
            suivant = titres[n + 1][0] if n + 1 < len(titres) else len(lignes)
            fin = next((j for j in range(i + 1, suivant) if lignes[j].rstrip() == "---"), suivant) - 1
            fiches_.append((ident, i, fin))
        else:
            if bloc[0] != ident:
                ecarts.append((i + 1, "marqueur %s ≠ titre %s" % (bloc[0], ident)))
            fiches_.append((ident, bloc[1], bloc[2]))

    premiere = min([i for i, _ in titres] + [b[1] for b in blocs] + [len(lignes)])
    socle = socle_lignes(lignes)
    for nom, motif in (("## Le socle commun", r"^## Le socle"), ("## L'ordre des fiches", r"^## L.*ordre des fiches")):
        ou = [i for i, l in enumerate(lignes) if re.match(motif, l)]
        if not ou:
            ecarts.append((1, "section absente : %s" % nom))
        elif len(ou) > 1:
            ecarts.append((ou[1] + 1, "section en double : %s (déjà ligne %d)" % (nom, ou[0] + 1)))
        elif ou[0] > premiere:
            ecarts.append((ou[0] + 1, "section après la première fiche : %s" % nom))

    if socle and len(socle) > SEUIL_SOCLE:
        debut_socle = next((i for i, l in enumerate(lignes) if l.startswith("## Le socle")), 1)
        avert.append((debut_socle + 1, "socle : %d lignes, au-delà du seuil de vlp.py (%d)"
                      % (len(socle), SEUIL_SOCLE)))

    for ident, debut, fin in fiches_:
        corps = lignes[debut:fin + 1]
        if not any(l.startswith(CRITERE) for l in corps):
            ecarts.append((debut + 1, "fiche %s sans ligne %s" % (ident, CRITERE)))
        ouvert_code = False   # un code en ligne peut commencer sur la ligne d'avant
        for j, l in enumerate(corps, debut + 1):
            if not l.strip() or l.lstrip().startswith("```"):
                ouvert_code = False
                continue
            # Une mention entre accents graves parle du marqueur, elle ne le pose pas.
            hors_code = CODE_EN_LIGNE.sub("", ("`" if ouvert_code else "") + l)
            if hors_code.count("`") % 2:
                ouvert_code, hors_code = True, hors_code[:hors_code.index("`")]
            else:
                ouvert_code = False
            if "(visuel)" in hors_code and not CRITERE_VISUEL.match(l):
                ecarts.append((j, "fiche %s : (visuel) hors de la ligne « %s (visuel) » — /vlp:enchainer ne s'y arrêtera pas"
                               % (ident, CRITERE)))
        if len(corps) > SEUIL_FICHE:
            avert.append((debut + 1, "fiche %s : %d lignes, au-delà du seuil de vlp.py (%d)"
                          % (ident, len(corps), SEUIL_FICHE)))
    return sorted(ecarts), avert, len(vus), len(socle)


def cmd_valider(chemins, sortie, plan=False):
    code = cmd_valider_seul(chemins, sortie)
    for chemin in chemins if plan else []:
        for n, l in enumerate(lignes_de(chemin) if os.path.isfile(chemin) else [], 1):
            if PLAN.match(l):
                sortie.write("%s%d:%s\n" % (chemin + ":" if len(chemins) > 1 else "", n, l))
    return code


def cmd_valider_seul(chemins, sortie):
    code = 0
    for chemin in chemins:
        if not os.path.isfile(chemin):
            sortie.write("%s:0: fichier introuvable\nINVALIDE 0 fiches · socle 0 lignes · 1 écarts · 0 avertissements — %s\n"
                         % (chemin, chemin))
            code = 1
            continue
        if rapport(chemin, lignes_de(chemin), sortie):
            code = 1
    return code


def rapport(chemin, lignes, sortie):
    """Écrit les écarts, les avertissements et le bilan ; rend le nombre d'écarts."""
    ecarts, avert, n, socle = valider_lignes(lignes)
    for ligne, message in ecarts:
        sortie.write("%s:%d: %s\n" % (chemin, ligne, message))
    for ligne, message in avert:
        sortie.write("%s:%d: avertissement : %s\n" % (chemin, ligne, message))
    sortie.write("%s %d fiches · socle %d lignes · %d écarts · %d avertissements — %s\n"
                 % ("INVALIDE" if ecarts else "VALIDE", n, socle, len(ecarts), len(avert), chemin))
    return len(ecarts)


# --- hook --------------------------------------------------------------------

MARQUE = re.compile(r"^<!-- FICHE:[A-Z]{1,3}[0-9]+ -->$")


def est_fichier_de_fiches(lignes):
    """Un marqueur de fiche ou le titre du socle, hors bloc de code : la méthode
    et les commandes en montrent dans des blocs, elles ne sont pas des fiches."""
    code = False
    for l in lignes:
        if l.lstrip().startswith("```"):
            code = not code
        elif not code and (MARQUE.match(l.strip()) or l.startswith("## Le socle commun")):
            return True
    return False


def cmd_hook(entree, sortie, erreur):
    try:
        d = json.loads(entree.read())
    except ValueError:
        return 0
    ti = d.get("tool_input") if isinstance(d, dict) else None
    chemin = ti.get("file_path") if isinstance(ti, dict) else None
    if not isinstance(chemin, str) or not chemin.lower().endswith(".md"):
        return 0
    if not os.path.isabs(chemin) and isinstance(d.get("cwd"), str):
        chemin = os.path.join(d["cwd"], chemin)
    if not os.path.isfile(chemin):
        return 0
    lignes = lignes_de(chemin)
    if not est_fichier_de_fiches(lignes):
        return 0
    texte = io.StringIO()
    if rapport(chemin, lignes, texte):
        erreur.write(texte.getvalue() + "Corrige ce fichier de fiches avant de continuer.\n")
        return 2
    bilan = texte.getvalue().strip().splitlines()[-1]
    sortie.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": bilan}},
                            ensure_ascii=False) + "\n")
    return 0


# --- filet -------------------------------------------------------------------

SEUIL_FILET = 3  # Tours restants à partir desquels on avertit le sous-agent


def cmd_filet(entree, sortie, erreur):
    """Avertit quand le sous-agent approche du plafond de tours.

    Lit le JSON du hook sur stdin — `PostToolUse` ou `PostToolUseFailure`, après
    tout outil. Si nous sommes dans un sous-agent (agent_type contient 'fiche'
    et agent_id existe), compte les tours déjà rendus et avertit si
    tours_restants <= SEUIL_FILET, au nom de l'événement reçu.
    """
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0

    # Vérifier que c'est un sous-agent de fiche
    agent_type = d.get("agent_type", "")
    agent_id = d.get("agent_id")
    if "fiche" not in agent_type or not agent_id:
        return 0

    transcript_path = d.get("transcript_path")
    if not isinstance(transcript_path, str):
        return 0

    # Chemin du transcript du sous-agent
    # Sur Windows, les chemins JSON peuvent avoir des barres obliques
    transcript_path_os = transcript_path.replace("/", os.sep)
    base = os.path.splitext(transcript_path_os)[0]
    subagent_path = os.path.join(base, "subagents", f"agent-{agent_id}.jsonl")

    # Compter les tours du sous-agent — None : le transcript ne s'ouvre pas
    tours = comptoir_tours(subagent_path)
    if tours is None:
        return 0

    # Lire maxTurns depuis agents/fiche.md
    # Le chemin est relatif au kit — nous sommes dans scripts/vlp.py
    kit_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fiche_path = os.path.join(kit_root, "agents", "fiche.md")

    max_turns = lire_max_turns(fiche_path)
    if max_turns is None:
        return 0

    tours_restants = max_turns - tours
    if 0 < tours_restants <= SEUIL_FILET:
        tour_mot = "tour" if tours_restants == 1 else "tours"
        message = f"Attention : {tours_restants} {tour_mot} restant{'s' if tours_restants > 1 else ''}. Rends ton statut maintenant — RETOUR avec ce qui est fait et ce qui reste, si la fiche n'est pas finie."
        # Même forme après un succès ou un échec (doc des hooks, lue le 2026-09-24) :
        # seul le nom change, celui de l'événement reçu.
        evenement = d.get("hook_event_name") or "PostToolUse"
        sortie.write(json.dumps(
            {"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": message}},
            ensure_ascii=False
        ) + "\n")

    return 0


def comptoir_tours(chemin):
    """Compte les tours distincts (message.id) dans un transcript de sous-agent ;
    None s'il ne s'ouvre pas. Ouvert par `ouvrir` de mesure-tokens.py : sous
    Windows, dès 260 caractères, isfile et open disent absent un fichier présent (FIL1)."""
    tours = set()
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    d = json.loads(ligne)
                    message = d.get("message")
                    if isinstance(message, dict):
                        usage = message.get("usage")
                        if isinstance(usage, dict):
                            mid = message.get("id")
                            if mid:
                                tours.add(mid)
                except json.JSONDecodeError:
                    pass
    except UnicodeDecodeError:
        pass
    except OSError:
        return None
    return len(tours)


def lire_max_turns(chemin):
    """Lit maxTurns depuis le frontmatter YAML d'un fichier."""
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            lignes = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None

    # Chercher le frontmatter YAML
    if len(lignes) < 2 or not lignes[0].strip().startswith("---"):
        return None

    for i in range(1, len(lignes)):
        ligne = lignes[i].strip()
        if ligne.startswith("---"):
            break
        if ligne.startswith("maxTurns:"):
            try:
                return int(ligne.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass

    return None


# --- page --------------------------------------------------------------------

# Le seuil vit dans le script (SEUIL_PAGE) : ici, il est défini et cité.
SEUIL_PAGE = 250
GABARIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "artefact-chantier.html")
LI_FICHE = re.compile(r'[ \t]*<li class="fiche"[^>]*>.*?</li>\n?', re.S)
UL_FICHES = re.compile(r'(<ul class="fiches">)(.*?)(\n[ \t]*</ul>)', re.S)
# Relit tout ce que `ligne_cout` écrit : le total entre parenthèses, ou nu sous
# 1 000 (`arrondi`), négatif compris ; le prix, négatif compris, ou `?` quand il
# manque. Un négatif, `couts` l'écrit sans Git quand l'ancienne page affiche plus
# que la session mesurée : il se relit avec son signe (chantier TAR).
COUT = re.compile(r"(?:\((\d[\d ]*)\)|(-?\d+)) · (\d+) tours · (-?[\d,]+|\?) \$")
_mesure = None


def mesure():
    """`mesure-tokens.py`, importé une fois (le tiret interdit `import`)."""
    global _mesure
    if _mesure is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mesure_tokens", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesure-tokens.py"))
        _mesure = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mesure)
    return _mesure


def esc(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Dollars par million de tokens, moyenne des 19 chantiers dont le coût a ete
# mesure par mesure-tokens.py (183 243 381 tokens pour 153,40 $ ; etendue
# 0,663 a 1,022 selon la part de cache). Sert aux ESTIMATIONS de page, jamais
# a un cout annonce : un cout mesure vient toujours de mesure-tokens.py.
USD_PAR_MTOKENS = 0.8371


def estimation_usd(n):
    """Le cout approximatif de `n` tokens, en dollars, comme `≈230 $`."""
    v = n / 1_000_000.0 * USD_PAR_MTOKENS
    return "≈%s $" % (("%.2f" % v).replace(".", ",") if v < 10 else "%d" % round(v))


def milliers(n):
    return "{:,}".format(n).replace(",", " ")


def arrondi(n):
    """La convention de coût en tête de templates/artefact-chantier.html."""
    if n < 1000:
        return str(n)
    # Dès 999 950, les milliers s'arrondiraient à « 1000,0k » : c'est déjà le million.
    valeur, unite = (n / 1_000_000, "M") if n >= 999_950 else (n / 1000, "k")
    return "≈%s%s (%s)" % (("%.1f" % valeur).replace(".", ","), unite, milliers(n))


def ligne_cout(total, tours, usd):
    return "%s · %d tours · %s $" % (arrondi(total), tours, "?" if usd is None else ("%.2f" % usd).replace(".", ","))


def fiches_du_fichier(lignes):
    """[(id, titre, coché, sessions)] dans l'ordre du fichier."""
    titres = [(i, l) for i, l in enumerate(lignes) if TITRE.match(l)]
    rendu = []
    for n, (i, l) in enumerate(titres):
        suivant = titres[n + 1][0] if n + 1 < len(titres) else len(lignes)
        ident = l.split()[1]
        titre = l.split(" — ", 1)[1] if " — " in l else l
        rendu.append((ident, titre.replace("`", "").strip(), "[x]" in l, sessions_de(lignes[i:suivant])))
    return rendu


def lis_page(html):
    """{id: (data-etat ou None, note html ou None, cout html ou None)}."""
    vues = {}
    for li in LI_FICHE.findall(html):
        ident = re.search(r'<span class="id">(.*?)</span>', li)
        if not ident:
            continue
        etat = re.search(r'data-etat="(\w+)"', li)
        note = re.search(r'<span class="note">(.*?)</span>', li, re.S)
        cout = re.search(r'<span class="cout mono">(.*?)</span>', li, re.S)
        vues[ident.group(1)] = (etat and etat.group(1), note and note.group(1), cout and cout.group(1))
    return vues


def etats(fiches_, anciens):
    """{id: faite | encours | bloquee | None} — le fichier a raison ; seul
    `bloquee` vient de la page, et ne survit pas à la case cochée."""
    rendu, premiere = {}, True
    for ident, _, coche, _ in fiches_:
        if coche:
            rendu[ident] = "faite"
        elif premiere:
            rendu[ident] = "bloquee" if anciens.get(ident, (None,))[0] == "bloquee" else "encours"
            premiere = False
        else:
            rendu[ident] = None
    return rendu


def triplet(texte):
    """(total, tours, usd) lus sur une ligne de coût affichée, ou None ; usd
    vaut None sur `? $`."""
    c = texte and COUT.search(texte)
    if not c:
        return None
    from decimal import Decimal
    usd = None if c.group(4) == "?" else Decimal(c.group(4).replace(",", "."))
    return int((c.group(1) or c.group(2)).replace(" ", "")), int(c.group(3)), usd


def moins(a, b):
    """a − b, ou None si l'un manque : un prix inconnu le reste."""
    return None if a is None or b is None else a - b


GIT = "git"     # test-vlp.py le remplace pour simuler un poste sans Git
COMMIT_FICHE = re.compile(r"^([A-Z]{1,3}[0-9]+) :")
INFINI = float("inf")


def heures_commits(fichier, ids, pourquoi=None, clos=False):
    """({id: heure}, [heures], [autres heures]) en secondes UTC, lus par `git log` dans le
    dossier du fichier : l'heure d'auteur du commit `<id> :` de chaque fiche — le plus ancien
    s'il y en a deux —, celles de tous les commits qui nomment le préfixe (`REP`, `REP2`…),
    puis celles des autres commits, triées : elles bornent le chantier (`plages`).
    Sans commit de fiche, `{}` d'abord : un chantier en cours. None sans `git`, sans dépôt,
    sans commit qui nomme le préfixe, ou sans commit de fiche d'un chantier `clos` — sa
    dernière mention est sa clôture, rien ne tomberait après (chantier ZER) : le repli,
    jamais un traceback — et sa raison, ajoutée à la liste `pourquoi` si on en donne une."""
    import subprocess
    pourquoi = [] if pourquoi is None else pourquoi
    if not ids:
        pourquoi.append("aucune fiche au fichier")
        return None
    try:
        r = subprocess.run([GIT, "log", "--format=%at %s"], cwd=os.path.dirname(os.path.abspath(fichier)),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        pourquoi.append("git ne se lance pas : %s" % e)
        return None
    if r.returncode:
        pourquoi.append("git log en échec : %s" % ((r.stderr or "").strip().splitlines() or ["code %d" % r.returncode])[0])
        return None
    nomme = re.compile(r"(?<![A-Za-z0-9])(?:%s)[0-9]*(?![A-Za-z0-9])"
                       % "|".join(sorted({PREFIXE.match(i).group(0) for i in ids})))
    commits, prefixe, autres = {}, [], []
    for ligne in r.stdout.splitlines():
        heure, _, sujet = ligne.partition(" ")
        if not heure.isdigit():
            continue
        (prefixe if nomme.search(sujet) else autres).append(int(heure))
        c = COMMIT_FICHE.match(sujet)
        if c and c.group(1) in ids:
            commits[c.group(1)] = min(int(heure), commits.get(c.group(1), int(heure)))
    if not commits:
        if not prefixe:
            pourquoi.append("aucun commit qui nomme %s" % PREFIXE.match(ids[0]).group(0))
            return None
        if clos:
            pourquoi.append("chantier clos sans commit « %s : » ni d'une autre fiche" % ids[0])
            return None
        return {}, sorted(prefixe), sorted(autres)
    return commits, sorted(prefixe), sorted(autres)


def plages(fiches_, heures, gardes):
    """([(id, (début, fin])] dans l'ordre des commits, [plages hors fiches]). Une fiche va
    du commit de la précédente au sien ; la première part du dernier commit antérieur qui
    nomme le préfixe, à défaut de l'origine ; une fiche à session sans commit va jusqu'au
    bout du transcript, et part de l'ouverture (le dernier commit qui nomme le préfixe)
    tant qu'aucune fiche n'a de commit — en cours : clos, `heures_commits` rend le repli. L'origine : le dernier commit qui ne nomme pas le
    préfixe, avant ce début — le chantier d'avant, quand une session en enchaîne plusieurs ;
    à défaut, le début de la session. Hors fiches : de l'origine à la première fiche, et de
    la dernière au premier commit suivant qui nomme le préfixe — la clôture ; sans lui,
    jusqu'au bout. Au-delà, rien ne compte : une mention plus tardive n'étire rien. Ni
    commit de fiche ni fiche à session : ([], [])."""
    commits, prefixe, autres = heures
    ordre = sorted(commits, key=commits.get)
    premier = commits[ordre[0]] if ordre else INFINI    # sans commit de fiche : le dernier qui nomme
    debut = max((t for t in prefixe if t < premier), default=-INFINI)
    origine = max((t for t in autres if t < (premier if debut == -INFINI else debut)), default=-INFINI)
    debut = max(debut, origine)
    rendu = []
    for ident in ordre:
        rendu.append((ident, (debut, commits[ident])))
        debut = commits[ident]
    sans = [f[0] for f in fiches_ if f[0] not in commits and f[3]]
    for ident in sans[:-1]:
        gardes.append("GARDE: %s porte une session sans commit « %s : » — ses tours comptent dans une autre plage"
                      % (ident, ident))
    if sans:
        rendu.append((sans[-1], (debut, INFINI)))
    if not rendu:
        return [], []
    dernier = rendu[-1][1][1]
    fin = min((t for t in prefixe if t > dernier), default=INFINI)
    return rendu, [p for p in ((origine, rendu[0][1][0]), (dernier, fin)) if p[0] < p[1]]


def parts_aux_commits(fiches_, heures, gardes, entete=()):
    """([(id, session, sous-agents)], (session, sous-agents) hors fiches), ou None sans
    transcript mesurable, ou sans fiche à découper. Les sessions : celles des fiches, puis
    `entete` — le cadrage (`sessions_entete`). Chaque fiche qui a une plage la prend dans
    chaque session et ses sous-agents (la plage de `mesurer`) ; le reste fait « hors fiches ». Une part vaut
    (total, tours, usd, n) — n : les transcripts qui y ont un tour —, usd arrondi au
    centime : tout s'additionne, dans `cout` comme sur la page. Aucun tour gardé, ni aux
    fiches ni hors fiches : une `GARDE:` le dit, les nombres restent (chantier ZER)."""
    from decimal import ROUND_HALF_UP, Decimal
    m = mesure()
    sessions, fichiers = [], []
    for groupe in [f[3] for f in fiches_] + [list(entete)]:
        sessions += [s for s in groupe if s not in sessions]
    for s in sessions:
        chemin, erreur = m.resoudre(s)
        if erreur:
            gardes.append("GARDE: session non mesurée : %s — %s" % (s, erreur))
            continue
        fichiers += [(chemin, 0)] + [(a, 1) for a in m.sous_agents(chemin)]    # 0 : session, 1 : sous-agent
    if not fichiers:
        return None
    par_fiche, trous = plages(fiches_, heures, gardes)
    if not par_fiche:
        return None

    def part(bornes):
        rendu = [[0, 0, Decimal(0), 0], [0, 0, Decimal(0), 0]]
        for chemin, sorte in fichiers:
            p, tours = rendu[sorte], 0
            for plage in bornes:
                r, erreur = m.mesurer(chemin, plage)
                if erreur:
                    g = "GARDE: transcript non mesuré : %s — %s" % (chemin, erreur)
                    gardes.extend([] if g in gardes else [g])
                    continue
                p[0], p[1], tours = p[0] + r["total"], p[1] + r["tours"], tours + r["tours"]
                p[2] = None if p[2] is None or r["usd_exact"] is None else p[2] + r["usd_exact"]
            p[3] += 1 if tours else 0
        return tuple((t, n, None if u is None else u.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), k)
                     for t, n, u, k in rendu)

    parts, hors = [(ident,) + part([p]) for ident, p in par_fiche], part(trous)
    if not plus(*[q for _, s, a in parts for q in (s, a)], *hors)[1]:
        gardes.append("GARDE: découpe à zéro — aucun tour de %d transcript%s ne tombe dans une plage"
                      % (len(fichiers), "s" if len(fichiers) > 1 else ""))
    return parts, hors


def plus(*parts):
    """La somme de parts (total, tours, usd, n) ; usd None dès qu'un prix manque."""
    usd = None if any(p[2] is None for p in parts) else sum(p[2] for p in parts)
    return sum(p[0] for p in parts), sum(p[1] for p in parts), usd, sum(p[3] for p in parts)


def ligne_parts(nom, session, agents):
    """`<nom> · <somme> = session <…> + <n> sous-agents <…>` : une ligne de `cout` qui nomme
    ce qu'elle compte. La somme d'abord : c'est le nombre de la page, et `triplet` la relit."""
    n = agents[3]
    return "%s · %s = session %s + %s" % (
        nom, ligne_cout(*plus(session, agents)[:3]), ligne_cout(*session[:3]),
        "%d sous-agent%s %s" % (n, "s" if n > 1 else "", ligne_cout(*agents[:3])) if n else "0 sous-agent")


def couts_aux_commits(fiches_, heures, gardes, entete=()):
    """`couts` coupé aux commits (`parts_aux_commits`) : une ligne par fiche, session et
    sous-agents sommés ; « hors fiches » à part, et total = fiches + hors fiches."""
    decoupe = parts_aux_commits(fiches_, heures, gardes, entete)
    if decoupe is None:
        return {}, None, None
    parts, hors = decoupe
    sommes = {ident: plus(s, a) for ident, s, a in parts}
    hors = plus(*hors)
    return ({ident: ligne_cout(*v[:3]) for ident, v in sommes.items()},
            plus(*sommes.values(), hors)[:3], hors[:3])


def couts(fiches_, anciens, ancien_total, gardes, heures=None, entete=()):
    """({id: ligne de coût}, total, hors fiches) — total et hors fiches en (total, tours,
    usd), ou None. Avec les heures des commits (`heures_commits`) : `couts_aux_commits`.
    Sans elles, tirés de l'ancienne page, sans hors fiches. Une session portée
    par plusieurs fiches : les premières gardent le coût déjà affiché (l'écart
    du compteur à leur clôture), la dernière prend le reste — moins la part que
    l'ancienne page n'attribuait à aucune fiche (le cadrage joué dans la même
    session), si une seule session est partagée."""
    if heures:
        return couts_aux_commits(fiches_, heures, gardes, entete)
    m = mesure()
    mesures = {}
    for _, _, _, sessions in fiches_:
        for s in sessions:
            if s in mesures:
                continue
            chemin, erreur = m.resoudre(s)
            r = None
            if not erreur:
                r, erreur = m.mesurer(chemin)
            if erreur:
                gardes.append("GARDE: session non mesurée : %s — %s" % (s, erreur))
            mesures[s] = r
    # La part non attribuée de l'ancienne page : son total moins ses coûts affichés.
    base = triplet(ancien_total)
    for ident in anciens:
        c = triplet(anciens[ident][2])
        if base and c:
            base = (base[0] - c[0], base[1] - c[1], moins(base[2], c[2]))
    partagees = [s for s in mesures if mesures[s] and sum(1 for f in fiches_ if s in f[3]) > 1]
    if not base or len(partagees) != 1 or base[0] < 0 or base[1] < 0:
        base = (0, 0, 0)
    rendu = {}
    for s, r in mesures.items():
        if r is None:
            continue
        porteurs = [f[0] for f in fiches_ if s in f[3]]
        total, tours, usd = r["total"], r["tours"], r["usd_exact"]
        if len(porteurs) > 1:
            total, tours = total - base[0], tours - base[1]
            usd = moins(usd, base[2])
        for ident in porteurs[:-1]:
            ancien = anciens.get(ident, (None, None, None))[2]
            c = triplet(ancien)
            if not c:
                gardes.append("GARDE: %s partage la session %s sans coût affiché — tout le coût va sur %s"
                              % (ident, s, porteurs[-1]))
                continue
            rendu[ident] = ancien
            total, tours = total - c[0], tours - c[1]
            usd = moins(usd, c[2])
        rendu[porteurs[-1]] = ligne_cout(total, tours, usd)
    mesurees = [r for r in mesures.values() if r]
    if not mesurees:
        return rendu, None, None
    usd = None if any(r["usd_exact"] is None for r in mesurees) else sum(r["usd_exact"] for r in mesurees)
    return rendu, (sum(r["total"] for r in mesurees), sum(r["tours"] for r in mesurees), usd), None


def comptage(fiches_, etat):
    faites = sum(1 for e in etat.values() if e == "faite")
    texte = "%d fiches · %d %s" % (len(fiches_), faites, "faite" if faites <= 1 else "faites")
    courante = next((i for i, e in etat.items() if e in ("encours", "bloquee")), None)
    if courante:
        texte += " · %s : %s" % ("bloquée" if etat[courante] == "bloquee" else "en cours", courante)
    return texte


def creer(fichier, projet, titre, resultat):
    html = lire(GABARIT)
    fiches_ = fiches_du_fichier(lignes_de(fichier))
    remplacements = [
        (r"<title>.*?</title>", "<title>%s — %s</title>" % (esc(projet), esc(titre))),
        (r'(<div class="eyebrow">).*?(</div>)', r"\g<1>%s · fiches \g<2>" % esc(projet)),
        (r"<h1>.*?</h1>", "<h1>%s</h1>" % esc(titre)),
        (r"(</h1>\s*<p>).*?(</p>)", r"\g<1>%s\g<2>" % esc(resultat).replace("\\", "\\\\")),
        (r'(<ul class="journal">).*?(\n[ \t]*</ul>)', r"\g<1>\g<2>"),
        (r'(<div class="blocage">\s*<p>).*?(</p>\s*<pre>).*?(</pre>)', r"\g<1>\g<2>\g<3>"),
        (r"(<h2>Chantier clos le ).*?(</h2>\s*<div class=\"bilan\">).*?(\n[ \t]*</div>)", r"\g<1>\g<2>\n      <p></p>\g<3>"),
        (r'(Fichier de fiches : <span class="mono">).*?(</span>)', r"\g<1>%s\g<2>" % esc(fichier.replace("\\", "/"))),
    ]
    for motif, rempl in remplacements:
        html, n = re.subn(motif, rempl, html, count=1, flags=re.S)
        if not n:
            raise ValueError("gabarit : motif introuvable : %s" % motif)
    return html


def regenerer(html, fichier, notes, journal, date, gardes):
    lignes = lignes_de(fichier)
    fiches_ = fiches_du_fichier(lignes)
    if not fiches_:
        raise ValueError("aucun titre de fiche au format '## X1' dans %s" % fichier)
    anciens = lis_page(html)
    etat = etats(fiches_, anciens)
    ancien_total = re.search(r'<p class="mono cout-total">(.*?)</p>', html, re.S)
    clos = any(l.startswith("**CLOS**") for l in lignes)
    heures = heures_commits(fichier, [f[0] for f in fiches_], clos=clos) if any(f[3] for f in fiches_) else None
    cout, total, hors = couts(fiches_, anciens, ancien_total and ancien_total.group(1), gardes, heures,
                              sessions_entete(lignes))
    etiquette = {"faite": "faite", "encours": "en cours", "bloquee": "bloquée", None: "à faire"}
    items = []
    for ident, titre, _, _ in fiches_:
        e = etat[ident]
        note = esc(notes[ident]) if ident in notes else anciens.get(ident, (None, None))[1]
        li = ['      <li class="fiche"%s>' % (' data-etat="%s"' % e if e else ""),
              '        <span class="id">%s</span><span class="titre">%s</span>' % (ident, esc(titre)),
              '        <span class="etat">%s</span>' % etiquette[e]]
        if note:
            li.append('        <span class="note">%s</span>' % note)
        if ident in cout:
            li.append('        <span class="cout mono">%s</span>' % cout[ident])
        items.append("\n".join(li + ["      </li>"]))
    prefixe = re.search(r'<p class="mono cout-total">(.*?) : ', html)
    prefixe = prefixe.group(1) if prefixe else "Coût du chantier"
    html = re.sub(r'\n[ \t]*<p class="mono cout-(?:total|hors)">.*?</p>', "", html, flags=re.S)
    bloc = "\n" + "\n".join(items)
    bloc_total = ""
    if hors:
        bloc_total += '\n    <p class="mono cout-hors">Hors fiches : %s</p>' % ligne_cout(*hors)
    if total:
        bloc_total += '\n    <p class="mono cout-total">%s : %s</p>' % (prefixe, ligne_cout(*total))
    html, n = UL_FICHES.subn(lambda m: m.group(1) + bloc + m.group(3) + bloc_total, html, count=1)
    if not n:
        raise ValueError("page : liste des fiches introuvable")
    spans = "".join('<span%s></span>' % (' data-etat="%s"' % etat[f[0]] if etat[f[0]] else "") for f in fiches_)
    html, n = re.subn(r'(<div class="avancement">\s*).*?(\s*</div>)', lambda m: m.group(1) + spans + m.group(2), html, count=1, flags=re.S)
    html, n2 = re.subn(r'(<p class="mono" style="margin-top:.5rem">).*?(</p>)',
                       lambda m: m.group(1) + comptage(fiches_, etat) + m.group(2), html, count=1, flags=re.S)
    if not (n and n2):
        raise ValueError("page : avancement ou ligne de comptage introuvable")
    blocage = re.search(r'<section( hidden)?>(\s*<h2>Arrêt sur blocage</h2>\s*<div class="blocage">\s*<p>)(.*?)</p>', html, re.S)
    if blocage and not blocage.group(1):
        fiche_bloquee = re.match(r"\s*([A-Z]{1,3}[0-9]+)", blocage.group(3))
        if fiche_bloquee and etat.get(fiche_bloquee.group(1)) == "faite":
            html = html[:blocage.start()] + "<section hidden>" + html[blocage.start() + len("<section>"):]
    for texte in journal:
        ligne = '      <li><time datetime="%s">%s</time><span>%s</span></li>' % (date, date, esc(texte))
        html, n = re.subn(r'(<ul class="journal">.*?)(\n[ \t]*</ul>)', lambda m: m.group(1) + "\n" + ligne + m.group(2),
                          html, count=1, flags=re.S)
        if not n:
            raise ValueError("page : journal introuvable")
    # La plage de l'en-tête, vide à la création (`creer`), suit le fichier ; ce qui la suit
    # (« · clos », écrit à la main) reste (chantier PLA).
    html = re.sub(r'(<div class="eyebrow">[^<]*? · fiches )(?:[A-Z]{1,3}\d+(?:–[A-Z]{1,3}\d+)?)?',
                  lambda m: m.group(1) + plage([f[0] for f in fiches_]), html, count=1)
    html = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)', lambda m: m.group(1) + date + m.group(2), html, count=1)
    return html, fiches_, etat, total, hors


def verifier_page(html, fichier, sortie):
    fiches_ = fiches_du_fichier(lignes_de(fichier))
    anciens = lis_page(html)
    etat = etats(fiches_, anciens)
    ecarts = []
    for ident, _, _, _ in fiches_:
        if ident not in anciens:
            ecarts.append("%s : absente de la page" % ident)
        elif anciens[ident][0] != etat[ident]:
            ecarts.append("%s : page %s, fichier %s" % (ident, anciens[ident][0] or "à faire", etat[ident] or "à faire"))
    for ident in anciens:
        if ident not in etat:
            ecarts.append("%s : sur la page, absente du fichier" % ident)
    avancement = re.search(r'<div class="avancement">(.*?)</div>', html, re.S)
    spans = re.findall(r'<span(?: data-etat="(\w+)")?></span>', avancement.group(1)) if avancement else []
    attendu = [etat[f[0]] or "" for f in fiches_]
    if spans != attendu:
        ecarts.append("avancement : page %s, fichier %s" % (spans, attendu))
    for e in ecarts:
        sortie.write("ÉCART: %s\n" % e)
    sortie.write("%s %d fiches · %d écarts (états et avancement seulement)\n"
                 % ("À JOUR" if not ecarts else "EN RETARD", len(fiches_), len(ecarts)))
    return 1 if ecarts else 0


def page_du_fichier(fichier):
    """La page par défaut d'un fichier de fiches : `<dossier>/artefacts/<nom>.html`."""
    return os.path.join(os.path.dirname(fichier), "artefacts",
                        os.path.splitext(os.path.basename(fichier))[0] + ".html")


def cmd_page(a, sortie):
    date = a.date or __import__("datetime").date.today().isoformat()
    if a.creer:
        if os.path.exists(a.page):
            sortie.write("GARDE: la page existe déjà : %s — --creer n'écrase rien\n" % a.page)
            return 1
        if not (a.projet and a.titre and a.resultat):
            sortie.write("GARDE: --creer demande --projet, --titre et --resultat\n")
            return 1
        html = creer(a.fichier, a.projet, a.titre, a.resultat)
        os.makedirs(os.path.dirname(os.path.abspath(a.page)), exist_ok=True)
    elif not os.path.isfile(a.page):
        sortie.write("GARDE: page introuvable : %s — --creer pour la créer\n" % a.page)
        return 1
    else:
        html = lire(a.page)
    if a.verifier:
        return verifier_page(html, a.fichier, sortie)
    gardes = []
    try:
        html, fiches_, etat, total, hors = regenerer(html, a.fichier, dict(a.note or []), a.journal or [], date, gardes)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    with open(a.page, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    n = html.count("\n") + (0 if html.endswith("\n") else 1)
    for g in gardes:
        sortie.write(g + "\n")
    sortie.write("PAGE %s · %s · %d lignes · total %s%s\n"
                 % (a.page, comptage(fiches_, etat), n, ligne_cout(*total) if total else "non mesuré",
                    ", dont hors fiches %s" % ligne_cout(*hors) if hors else ""))
    if n > SEUIL_PAGE:
        sortie.write("GARDE: %d lignes, au-delà du seuil du script (%d) — la page est relue à chaque fiche\n"
                     % (n, SEUIL_PAGE))
    return 0


# --- etat --------------------------------------------------------------------

NUMERO = re.compile(r"^(\d\d)-")


def nom_etat(contexte):
    """Le `*-etat.md` présent, sinon le premier numéro libre après le plus grand."""
    try:
        noms = sorted(os.listdir(contexte))
    except OSError:
        noms = []
    for n in noms:
        if NUMERO.match(n) and n.endswith("-etat.md"):
            return n
    pris = [int(NUMERO.match(n).group(1)) for n in noms if NUMERO.match(n)]
    return "%02d-etat.md" % (max(pris) + 1 if pris else 1)


# --- renvois -----------------------------------------------------------------

LIGNE_CHEMIN = re.compile(r"^\s*-\s*\*\*(contexte|index)\*\*\s*:\s*(.+?)\s*$")
CODE = re.compile(r"`([^`]+)`")


def noms_de_table(lignes, colonne, debut=None):
    """(numéro, nom) des noms entre accents graves dans la cellule `colonne`
    (0 ou -1) des lignes de table ; à partir du titre `debut` s'il est donné,
    jusqu'au titre `## ` suivant."""
    dedans = debut is None
    for i, l in enumerate(lignes, 1):
        if debut is not None and l.startswith("## "):
            dedans = l.startswith(debut)
            continue
        if not dedans or not l.startswith("|") or re.match(r"^\|[\s|:-]+\|?$", l):
            continue
        cellules = [c.strip() for c in l.strip().strip("|").split("|")]
        if cellules[0].startswith("*("):
            continue
        for nom in CODE.findall(cellules[colonne]):
            if "<" in nom or "*" in nom or "." not in nom:
                continue
            yield i, nom


def cmd_renvois(projet, sortie):
    carte_ = os.path.join(projet, "CHANTIER.md")
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    chemins = {"contexte": "context AI/"}
    for l in lignes_de(carte_):
        m = LIGNE_CHEMIN.match(l)
        if m:
            chemins[m.group(1)] = m.group(2)
    contexte = chemins["contexte"]
    index = chemins.get("index", contexte.rstrip("/") + "/00-INDEX.md")
    sources = [(index, 0, None), ("CLAUDE.md", -1, "## Routage")]
    nommes, absents = 0, 0
    for source, colonne, debut in sources:
        chemin = os.path.join(projet, source)
        if not os.path.isfile(chemin):
            if source == index:
                absents += 1
                sortie.write("ABSENT: CHANTIER.md: %s\n" % index)
            continue
        for i, nom in noms_de_table(lignes_de(chemin), colonne, debut):
            nommes += 1
            if not any(os.path.exists(os.path.join(projet, base, nom)) for base in (contexte, "")):
                absents += 1
                sortie.write("ABSENT: %s:%d: %s\n" % (source, i, nom))
    poids = []
    for nom, source, seuil in (("CLAUDE.md", "CLAUDE.md", SEUIL_CLAUDE), ("CHANTIER.md", "CHANTIER.md", SEUIL_CHANTIER),
                               ("index", index, SEUIL_INDEX)):
        chemin = os.path.join(projet, source)
        n = len(lignes_de(chemin)) if os.path.isfile(chemin) else None
        if n is not None and n > seuil:
            sortie.write("AVERTISSEMENT: %s %d lignes > %d\n" % (source, n, seuil))
        poids.append("%s %s/%d" % (nom, "absent" if n is None else n, seuil))
    sortie.write("POIDS %s\n" % " · ".join(poids))
    sortie.write("RENVOIS %d nommés · %d absents\n" % (nommes, absents))
    return 1 if absents else 0


# --- feuille -----------------------------------------------------------------

AUCUN_ENCOURS = ('    <div class="encours">\n      <div class="titre">Aucun chantier ouvert</div>\n'
                 '      <div>Lancer <span class="mono">/vlp:chantier</span> pour en ouvrir un.</div>\n    </div>\n')
BADGE_COURS = ' <span class="badge" data-etat="cours">en cours</span>'


def retirer_chevrons_url(val):
    """Retirer les chevrons d'une URL si elle est entièrement entre chevrons."""
    if val and re.match(r"^<(https?://[^>]+)>$", val):
        return val[1:-1]
    return val


def champ(lignes, nom, defaut=None):
    """La valeur d'une ligne `- **nom** : valeur` de `CHANTIER.md`."""
    motif = re.compile(r"^\s*-\s*\*\*%s\*\*\s*:\s*(.+?)\s*$" % re.escape(nom))
    for l in lignes:
        m = motif.match(l)
        if m:
            return retirer_chevrons_url(m.group(1))
    return defaut


def lettre_de(id_fiche):
    """Le préfixe d'un id de fiche : `RNV` pour `RNV12`, `Z` pour `Z3`."""
    m = PREFIXE.match(id_fiche)
    return m.group(0) if m else id_fiche[:1]


def lettres_prises(lignes):
    """Les lettres de la ligne « Lettres de fiche déjà prises » : une par entrée, `X (titre)`
    ou `X` seule ; les entrées se séparent aux virgules hors parenthèses, et un titre à
    virgule n'en ajoute pas (chantier TAR)."""
    texte = " ".join(l for l in lignes if l.strip())
    i = texte.find("Lettres de fiche déjà prises")
    if i < 0:
        return []
    fin = texte.find("Un nouveau chantier", i)
    liste = texte[i:fin if fin > 0 else None].split(":", 1)[-1]
    entrees, profondeur, debut = [], 0, 0
    for k, c in enumerate(liste):
        profondeur += {"(": 1, ")": -1}.get(c, 0)
        if c == "," and not profondeur:
            entrees.append(liste[debut:k])
            debut = k + 1
    entrees.append(liste[debut:])
    return [m.group(1) for m in (re.match(r"\s*([A-Z]{1,3})(?: \(|\.?\s*$)", e) for e in entrees) if m]


def plage(ids):
    return "%s–%s" % (ids[0], ids[-1]) if len(ids) > 1 else ids[0]


# Le gras et les liens Markdown d'un texte déjà échappé. Un <span class="mono"> y est mis
# de côté sous un jeton `<n>` : hors des balises, un texte échappé n'a aucun `<`.
MONO = re.compile(r'<span class="mono">[^<]*</span>')
MORCEAU = re.compile(r"((?:%s|[^<])+)|<[^>]*>" % MONO.pattern)
JETON = re.compile(r"<(\d+)>")
GRAS = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
LIEN = re.compile(r'\[([^\[\]]+)\]\((https?://(?:[^\s"()<]|\([^\s"()<]*\))+)\)')


def gras_et_liens(html):
    """`**x**` → `<strong>`, `[t](http…)` → `<a>` ; deux passes = une.

    Rien n'est converti dans un `<span class="mono">`, mais un gras peut l'englober.
    Toute autre balise borne un gras et reste telle quelle : une ligne entière se
    rejoue sans qu'un gras saute d'une cellule à l'autre. Un lien devient un jeton
    entier, son gras converti dedans : un gras du dehors l'englobe, sans le couper.
    """
    def morceau(m):
        if not m.group(1):
            return m.group(0)
        mis = []

        def jeton(bout):
            mis.append(bout)
            return "<%d>" % (len(mis) - 1)

        def rendu(t):
            return JETON.sub(lambda j: mis[int(j.group(1))], GRAS.sub(r"<strong>\1</strong>", t))

        t = MONO.sub(lambda j: jeton(j.group(0)), m.group(0))
        t = LIEN.sub(lambda j: jeton('<a href="%s">%s</a>' % (j.group(2), rendu(j.group(1)))), t)
        return rendu(t)
    return MORCEAU.sub(morceau, html)


def cellule_md(texte):
    texte = esc(texte.replace("\\|", "|"))
    return gras_et_liens(CODE.sub(lambda m: '<span class="mono">%s</span>' % m.group(1), texte))


def todo_du_fichier(lignes):
    """[(numéro, chantier, apporte, coût, dépend)] de la table `| # | Chantier |`."""
    rangs, dedans = [], False
    for l in lignes:
        if l.startswith("| # | Chantier"):
            dedans = True
            continue
        if not dedans:
            continue
        if not l.startswith("|"):
            break
        if re.match(r"^\|[\s|:-]+\|?$", l):
            continue
        cellules = [c.strip() for c in re.split(r"(?<!\\)\|", l.strip())[1:-1]]
        if len(cellules) >= 5:
            rangs.append(cellules[:5])
    return rangs


def zone(html, nom, ouvre, ferme):
    """(début, fin) du contenu entre `ouvre` (après le marqueur `ZONE:nom`) et `ferme`."""
    i = html.find("<!-- ZONE:%s" % nom)
    if i < 0:
        raise ValueError("marqueur ZONE:%s absent de la page" % nom)
    debut = html.find(ouvre, html.find("-->", i))
    fin = html.find(ferme, debut)
    if debut < 0 or fin < 0:
        raise ValueError("ZONE:%s sans %s … %s" % (nom, ouvre.strip(), ferme.strip()))
    return debut + len(ouvre), fin


def feuille(projet, html, todo, date):
    """(page régénérée, bilan) : encours, todo et lettres depuis `CHANTIER.md` et le fichier d'état."""
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    etat = champ(carte_, "fichier d'état")
    if not etat:
        raise ValueError("fichier d'état introuvable : aucun")
    lignes_etat = lignes_du_projet(projet, etat, "fichier d'état")
    courant = fichier_courant("\n".join(carte_))
    lettres = lettres_prises(carte_)
    if courant:
        lignes = lignes_du_projet(projet, courant, "fichier de fiches courant")
        ids = [l.split()[1] for l in lignes if TITRE.match(l)]
        titre = next((re.sub(r"^# Chantier \S+ — ", "", l) for l in lignes if l.startswith("# ")), courant)
        url = champ(carte_, "artefact du chantier", "aucun")
        lien = "" if url.lower().startswith("aucun") else ' — <a href="%s">la page du chantier</a>' % esc(url)
        encours = ('    <div class="encours">\n      <div class="titre">%s%s</div>\n'
                   '      <div>Fiches <span class="mono">%s</span>%s</div>\n    </div>\n'
                   % (cellule_md(titre), BADGE_COURS, plage(ids) if ids else "?", lien))
        if ids and lettre_de(ids[0]) not in lettres:
            lettres.append(lettre_de(ids[0]))
    else:
        encours = AUCUN_ENCOURS
    d, f = zone(html, "todo", "<tbody>\n", "        </tbody>")
    if todo is None and courant:
        m = re.search(r'<tr><td class="mono">(\d+)</td><td>(?:(?!</td>).)*?' + re.escape(BADGE_COURS), html[d:f])
        todo = m.group(1) if m else None
    rangs = todo_du_fichier(lignes_etat)
    if todo is not None and todo not in [r[0] for r in rangs]:
        raise ValueError("--todo %s absent de la TODO de %s" % (todo, etat))
    corps = "".join('          <tr><td class="mono">%s</td><td>%s%s</td><td>%s</td><td class="mono">%s</td>'
                    '<td class="mono">%s</td></tr>\n'
                    % (esc(n), cellule_md(ch), BADGE_COURS if n == todo else "", cellule_md(ap),
                       cellule_md(co), cellule_md(de)) for n, ch, ap, co, de in rangs) \
        or '          <tr><td colspan="5" class="rien-cell">Rien en attente.</td></tr>\n'
    neuf = html[:d] + corps + html[f:]
    d, f = zone(neuf, "encours", "\n", "  </section>")
    neuf = neuf[:d] + encours + neuf[f:]
    neuf = re.sub(r'(Lettres de fiche prises : <span class="mono">).*?(</span>)',
                  lambda m: m.group(1) + ", ".join(lettres) + m.group(2), neuf, count=1)
    if neuf != html:
        neuf = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)',
                      lambda m: m.group(1) + date + m.group(2), neuf, count=1)
    bilan = "FEUILLE todo %d · encours %s · lettres %d" % (len(rangs), "oui" if courant else "non", len(lettres))
    return neuf, bilan


def page_feuille(projet):
    contexte = champ(lignes_de(os.path.join(projet, "CHANTIER.md")), "contexte", "context AI/")
    return os.path.join(projet, contexte, "artefacts", "feuille-de-route.html")


def cmd_feuille(a, sortie):
    if not equipe(a.projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % a.projet)
        return 1
    page = page_feuille(a.projet)
    if not os.path.isfile(page):
        sortie.write("GARDE: feuille de route introuvable : %s\n" % page)
        return 1
    html = lire(page)
    try:
        neuf, bilan = feuille(a.projet, html, a.todo, a.date or __import__("datetime").date.today().isoformat())
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    if a.verifier:
        sortie.write("%s · %s — %s\n" % (bilan, "identique" if neuf == html else "écart", page))
        return 0 if neuf == html else 1
    with open(page, "w", encoding="utf-8", newline="") as f:
        f.write(neuf)
    sortie.write("%s · %s — %s\n" % (bilan, "inchangée" if neuf == html else "réécrite", page))
    return 0


# --- la ZONE:clos d'une feuille de route -------------------------------------
# Lue par `clore`, qui y ajoute une ligne à chaque clôture, et par
# `niveau --ecrire`, qui pose sur une feuille d'avant le 2026-09-17 ce que le
# gabarit a depuis : le bloc repliable et l'estimation en dollars du pied — et
# convertit les lignes écrites avant `gras_et_liens`.

# Le coût brut d'une cellule : entre parenthèses (`≈1,5k (1 500)`), ou nu, fait de
# chiffres seuls, sous 1 000 (`arrondi`) — plage, date et pied n'en sont pas (chantier TAR).
BRUT = re.compile(r'<td class="mono">(?:[^<]*\((\d[\d ]*)\)|(\d+))</td>')
# `clore` écrit ses lignes à dix espaces, et les repère à dix espaces.
RANG_CLOS = re.compile(r"          <tr>\n.*?          </tr>\n", re.S)
PIED_CLOS = re.compile(r'(Total cumulé</td><td class="mono"><strong>.*?</strong></td>)<td[^>]*>([^<]*)</td>', re.S)
GABARIT_FEUILLE = "templates/artefact-feuille-de-route.html"


def lignes_clos(corps):
    """Les `<tr>` de chantiers clos d'un corps de table — les lignes d'exemple
    du gabarit, reconnaissables à leurs `<…>`, n'en sont pas."""
    return [r for r in RANG_CLOS.findall(corps) if '<td class="mono">&lt;' not in r]


def total_clos(corps):
    """La somme des coûts bruts — entre parenthèses, ou nus sous 1 000 — d'un corps de table."""
    return sum(int(re.sub(r"\D", "", entre or nu)) for entre, nu in BRUT.findall(corps))


def resume_clos(n, total):
    """Ce que le bloc repliable montre sans être déplié."""
    if not n:
        return "aucun chantier clos"
    if not total:  # aucun des clos ne porte de coût mesuré : pas de 0 $ inventé.
        return "%d chantiers clos · coût non mesuré" % n
    return "%d chantiers clos · %s tokens · %s" % (n, arrondi(total), estimation_usd(total))


def regles_clos():
    """Les règles CSS du bloc repliable, lues dans le gabarit : elles n'ont pas
    de second exemplaire ici."""
    return [l for l in lire(os.path.join(KIT, GABARIT_FEUILLE)).splitlines(True)
            if l.lstrip().startswith(("details.clos", ".resume-clos"))]


def migrer_feuille(html):
    """Une feuille de route d'avant le 2026-09-17 n'a ni bloc repliable ni
    cellule d'estimation au pied de la table des clos : les poser, sans toucher
    à l'indentation des lignes de `ZONE:clos`. Rend le HTML — le même s'il les
    a déjà."""
    if "details.clos" not in html:
        i = html.find("tfoot td {")
        i = html.find("\n", i) + 1 if i >= 0 else html.find("</style>")
        html = html[:i] + "".join(regles_clos()) + html[i:]
    i = html.find("<!-- ZONE:clos")
    if i < 0:
        return html
    fin = html.find("  </section>", i)
    debut = html.find('    <div class="tableau">', i)
    if not 0 <= debut < fin:
        return html
    corps = html[debut:fin]
    total = total_clos(corps)
    # Une cellule qui porte déjà des dollars est celle que `clore` entretient.
    corps = PIED_CLOS.sub(lambda m: m.group(0) if "$" in m.group(2)
                          else m.group(1) + '<td class="mono">%s</td>' % estimation_usd(total),
                          corps, count=1)
    if '<details class="clos">' not in html[i:fin]:
        corps = ('    <details class="clos">\n      <summary><span class="resume-clos">%s</span>'
                 '</summary>\n' % resume_clos(len(lignes_clos(corps)), total)) + corps + "    </details>\n"
    return html[:debut] + corps + html[fin:]


CHEVRONS_HREF = re.compile(r'href="&lt;([^"]*)&gt;"')


def migrer_clos(html):
    """(HTML, n) : les lignes de `ZONE:clos` écrites avant `gras_et_liens` y
    passent, et un `href="&lt;URL&gt;"` redevient `href="URL"` ; n lignes changées.
    Les dix espaces restent, la ligne d'exemple du gabarit aussi. Deux passes = une."""
    d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    n = 0

    def rang(m):
        nonlocal n
        avant = m.group(0)
        if not lignes_clos(avant):  # la ligne d'exemple du gabarit
            return avant
        apres = CHEVRONS_HREF.sub(r'href="\1"', gras_et_liens(avant))
        n += apres != avant
        return apres
    corps = RANG_CLOS.sub(rang, html[d:f])
    return html[:d] + corps + html[f:], n


def markdown_brut(html):
    """(`**`, liens Markdown, liens cassés) restés dans les zones todo, encours et
    clos d'une feuille de route, en occurrences — hors code cité, hors ligne
    d'exemple du gabarit."""
    (a, b), (c, d), (e, f) = (zone(html, "todo", "<tbody>\n", "        </tbody>"),
                              zone(html, "encours", "\n", "  </section>"),
                              zone(html, "clos", "<tbody>\n", "        </tbody>"))
    clos = RANG_CLOS.sub(lambda m: "".join(lignes_clos(m.group(0))), html[e:f])
    texte = MONO.sub("", html[a:b] + html[c:d] + clos)
    return texte.count("**"), texte.count("](http"), texte.count('href="&lt;')


# --- niveau ------------------------------------------------------------------

# Ce qu'on ne regarde pas : une copie locale de `methode-chantier.md`. La
# méthode dit qu'un projet équipé avant la règle garde la sienne — on a
# seulement cessé d'en fabriquer.
VARIABLE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}")
# Une variable ne compte que là où une commande lit un chemin : le champ d'une
# ligne `- **nom** : …`, ou une cellule de table. Ailleurs c'est de la prose qui
# cite la règle, et le fichier d'état en cite beaucoup.
PORTEUSE = re.compile(r"^\s*(?:-\s*\*\*[^*]+\*\*\s*:|\|)")
TITRE_CLOS = re.compile(r"^#+\s.*\bclos\b", re.I)


def capte(fn, *args):
    """(code, lignes) d'une sous-commande rejouée pour son texte : `niveau`
    n'invente aucun contrôle que les autres savent déjà faire."""
    s = io.StringIO()
    code = fn(*(args + (s,)))
    return code, s.getvalue().splitlines()


def variables_citees(projet, sources):
    """(chemin, numéro, variable) de chaque `${…}` posée en chemin lisible."""
    for libelle, chemin in sources:
        for i, l in enumerate(lignes_du_projet(projet, chemin, libelle), 1):
            if PORTEUSE.match(l):
                for v in VARIABLE.findall(l):
                    yield chemin, i, v


def table_des_clos(lignes):
    """Le numéro du titre « Chantiers clos » suivi d'une table, ou None : le
    titre seul ne gêne pas, c'est la table qui double l'index."""
    debut = None
    for i, l in enumerate(lignes, 1):
        if l.startswith("#"):
            debut = i if TITRE_CLOS.match(l) else None
        elif debut and l.startswith("|"):
            return debut
    return None


FICHIER_MD = re.compile(r"[\w][\w./ -]*\.md")


def entete_clos():
    """Le titre et la phrase que le gabarit de `CHANTIER.md` pose à la place
    d'une table des chantiers clos."""
    g = lignes_de(os.path.join(KIT, "templates", "CHANTIER.md"))
    i = next(k for k, l in enumerate(g) if TITRE_CLOS.match(l))
    j = next(k for k in range(i, len(g)) if g[k].startswith("Lettres de fiche déjà prises"))
    return g[i:j]


def sans_table_des_clos(carte_, index):
    """`CHANTIER.md` sans sa table des chantiers clos, ou None si la retirer
    perdrait quelque chose : la ligne des lettres prises doit suivre la table,
    et l'index nommer chacun de ses fichiers."""
    i = table_des_clos(carte_)
    if i is None:
        return None
    i -= 1
    j = next((k for k in range(i, len(carte_)) if carte_[k].startswith("Lettres de fiche déjà prises")), None)
    if j is None:
        return None
    vus = "\n".join(index)
    for l in carte_[i:j]:
        if l.startswith("|") and any(os.path.basename(nom) not in vus for nom in FICHIER_MD.findall(l)):
            return None
    return carte_[:i] + entete_clos() + carte_[j:]


def cmd_niveau(a, sortie):
    """En quoi un projet équipé a dérivé du kit. Sans `--ecrire`, n'écrit rien
    nulle part ; avec, corrige les écarts dont la bonne valeur se déduit sans
    jugement, et laisse les autres en `ÉCART:`. Comme `clore`, tout se calcule
    avant la première écriture."""
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    date = a.date or __import__("datetime").date.today().isoformat()
    ecarts = avertissements = corriges = 0
    ecritures = []
    carte_ = lignes_du_projet(projet, "CHANTIER.md", "carte")

    _, lignes = capte(cmd_renvois, projet)
    poids = "POIDS non mesuré"
    for l in lignes:
        if l.startswith("ABSENT: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s — nommé, introuvable\n" % l[8:])
        elif l.startswith("AVERTISSEMENT: "):
            avertissements += 1
            sortie.write("AVERTISSEMENT: poids: %s\n" % l[15:])
        elif l.startswith("POIDS "):
            poids = l
        elif l.startswith("GARDE: "):
            ecarts += 1
            sortie.write("ÉCART: renvois: %s\n" % l[7:])

    page = page_feuille(projet)
    absente = not os.path.isfile(page)
    html = lire(os.path.join(KIT, GABARIT_FEUILLE)) if absente else lire(page)
    migre = migrer_feuille(html)
    try:
        neuf, _ = feuille(projet, migre, None, date)
        converti, n = migrer_clos(neuf)
        md = markdown_brut(converti if a.ecrire else neuf)
    except ValueError as e:
        neuf = md = None
        ecarts += 1
        sortie.write("ÉCART: feuille: %s\n" % e)
    if neuf is None:
        pass
    elif absente:
        if a.ecrire:
            ecritures.append((page, converti))
            corriges += 1
            sortie.write("CORRIGÉ: feuille: posée depuis le gabarit puis régénérée — %s\n" % page)
        else:
            ecarts += 1
            sortie.write("ÉCART: feuille: feuille de route introuvable : %s — le gabarit la pose\n" % page)
    else:
        for present, manque, pose in (
                (migre != html, "le bloc repliable des chantiers clos manque, et son estimation en"
                                " dollars — le gabarit les a", "bloc repliable des chantiers clos posé"),
                (neuf != migre, "écart — « vlp.py feuille %s » la régénère" % projet, "régénérée")):
            if not present:
                continue
            if a.ecrire:
                corriges += 1
                sortie.write("CORRIGÉ: feuille: %s\n" % pose)
            else:
                ecarts += 1
                sortie.write("ÉCART: feuille: %s\n" % manque)
        if a.ecrire and n:
            corriges += 1
            sortie.write("CORRIGÉ: feuille: %d lignes closes converties\n" % n)
        if a.ecrire and converti != html:
            ecritures.append((page, converti))
    sortie.write("MARKDOWN non mesuré, la feuille ne se régénère pas — %s\n" % page if md is None
                 else "MARKDOWN %d ** · %d liens Markdown · %d liens cassés — %s\n" % (md + (page,)))
    if md and any(md):
        ecarts += 1
        sortie.write("ÉCART: feuille: Markdown brut ou lien cassé%s\n"
                     % (" — « vlp.py niveau --ecrire » convertit les lignes closes" if n and not a.ecrire else ""))

    courant = fichier_courant("\n".join(carte_))
    if courant:
        fichier = chemin_garde(os.path.join(projet, courant), "fichier de fiches courant", courant)
        code, lignes = capte(cmd_page, argparse.Namespace(
            fichier=fichier, page=page_du_fichier(fichier), note=None, journal=None,
            creer=False, projet=None, titre=None, resultat=None, verifier=True, date=None))
        for l in lignes:
            if l.startswith("ÉCART: ") or l.startswith("GARDE: "):
                ecarts += 1
                sortie.write("ÉCART: page: %s\n" % l[7:])

    contexte = champ(carte_, "contexte", "context AI/")
    index = champ(carte_, "index", contexte.rstrip("/") + "/00-INDEX.md")
    sources = [("carte", "CHANTIER.md"), ("index", index)]
    etat = champ(carte_, "fichier d'état")
    if etat:
        sources.append(("fichier d'état", etat))
    for chemin, i, v in variables_citees(projet, sources):
        ecarts += 1
        sortie.write("ÉCART: variable: %s:%d cite %s — une variable ne vaut que dans"
                     " le texte d'une commande, pas dans un fichier de données\n" % (chemin, i, v))

    rang = table_des_clos(carte_)
    if rang is not None:
        neuve = sans_table_des_clos(carte_, lignes_du_projet(projet, index, "index")) if a.ecrire else None
        if neuve is None:
            ecarts += 1
            sortie.write("ÉCART: clos: CHANTIER.md:%d — la table des chantiers clos vit"
                         " dans l'index, pas dans la carte\n" % rang)
        else:
            ecritures.append((os.path.join(projet, "CHANTIER.md"), "\n".join(neuve) + "\n"))
            corriges += 1
            sortie.write("CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:%d —"
                         " l'index nomme chacun de ses fichiers\n" % rang)

    for chemin, contenu in ecritures:
        dossier = os.path.dirname(chemin)
        if dossier and not os.path.isdir(dossier):
            os.makedirs(dossier)
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write(contenu)
    sortie.write(poids + "\n")
    if a.ecrire:
        sortie.write("NIVEAU %d corrigés · %d à la main — %s\n" % (corriges, ecarts, projet))
    else:
        sortie.write("NIVEAU %d écarts · %d avertissements — %s\n" % (ecarts, avertissements, projet))
    return 1 if ecarts else 0


# --- clore -------------------------------------------------------------------

CLOS_LIGNE = "**CLOS** le %s. Ne se rejoue pas — ne sert plus qu'à relire son socle."
ENTREE_CLOS = re.compile(r"^- Clos le \S+ : .* \(chantier [A-Z]{1,3}\)\.$")
ROUTAGE_CLOS = "| relire un chantier clos |"


def resume_claude(cl, lettre, texte, date, gardes):
    """Ajoute `- Clos le <date> : T (chantier L).` à la section « Où on en est » de `CLAUDE.md`,
    en place, puis n'en garde que les CLOS_GARDES dernières de cette forme. Vrai si une ligne
    est écrite ; déjà là : rien."""
    debut = next((k for k, l in enumerate(cl) if l.startswith("## Où on en est")), None)
    if debut is None:
        gardes.append("section « Où on en est » absente de CLAUDE.md")
        return False
    fin = next((k for k in range(debut + 1, len(cl)) if cl[k].startswith("## ")), len(cl))
    if any("(chantier %s)" % lettre in l for l in cl[debut:fin]):
        return False
    dernier = max(k for k in range(debut, fin) if cl[k].strip())
    # Une ligne, blancs réduits : `ENTREE_CLOS` la relit, et l'élagage la trouve (chantier TAR).
    texte = re.sub(r"\s*\(chantier %s\)$" % re.escape(lettre), "", " ".join(texte.split()).rstrip("."))
    cl.insert(dernier + 1, "- Clos le %s : %s (chantier %s)." % (date, texte, lettre))
    entrees = [k for k in range(debut, fin + 1) if ENTREE_CLOS.match(cl[k])]
    for k in reversed(entrees[:max(0, len(entrees) - CLOS_GARDES)]):
        del cl[k]
    return True


def cmd_clore(a, sortie):
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    date = a.date or __import__("datetime").date.today().isoformat()
    chemin_carte = os.path.join(projet, "CHANTIER.md")
    carte_ = lignes_de(chemin_carte)
    courant = fichier_courant("\n".join(carte_))
    if not courant:
        sortie.write("GARDE: aucun chantier ouvert — rien à clore\n")
        return 1
    chemin_fiches = os.path.join(projet, courant)
    fiches_ = lignes_du_projet(projet, courant, "fichier de fiches")
    ids = [l.split()[1] for l in fiches_ if TITRE.match(l)]
    if not ids:
        sortie.write("GARDE: aucune fiche dans %s\n" % courant)
        return 1
    if any(l.startswith("**CLOS**") for l in fiches_):
        sortie.write("GARDE: %s porte déjà **CLOS**\n" % courant)
        return 1
    lettre = lettre_de(ids[0])
    titre = next((re.sub(r"^# Chantier \S+ — ", "", l) for l in fiches_ if l.startswith("# ")), courant)
    url = champ(carte_, "artefact du chantier", "aucun")
    fait = "%s..%s" % (ids[0], ids[-1]) + (" (%s)" % a.abandon if a.abandon else "")

    # 1. le fichier de fiches
    entete = [CLOS_LIGNE % date] + (["", "Abandonnées : %s." % a.abandon.rstrip(".")] if a.abandon else []) + [""]
    ligne_fait = "**Fait.** %s..%s (%s) : %s" % (ids[0], ids[-1], date, (a.fait or a.livre).rstrip("."))  + "."
    i = next((k for k, l in enumerate(fiches_) if l.startswith(("**Fait.**", "**Où on en est.**"))), None)
    if i is None:
        i = next(k for k, l in enumerate(fiches_) if l.startswith("# ")) + 2
        fiches_[i:i] = entete + [ligne_fait, ""]
    else:
        fin_para = i
        while fin_para + 1 < len(fiches_) and fiches_[fin_para + 1].strip():
            fin_para += 1
        fiches_[i:fin_para + 1] = entete + [ligne_fait]
    gardes, ecritures, faits = [], [], {"routage": 0, "index": 0, "bilan": 0}
    nom = os.path.basename(courant)

    # 1 bis. l'index et le routage de CLAUDE.md passent à « clos »
    index = champ(carte_, "index")
    chemin_index = os.path.join(projet, index) if index else None
    if not chemin_index or not os.path.isfile(chemin_index):
        gardes.append("index introuvable : %s" % index)
    else:
        idx = lignes_de(chemin_index)
        k = next((k for k, l in enumerate(idx) if l.startswith("| `%s` |" % nom) and "**ouvert**" in l), None)
        if k is None:
            gardes.append("ligne ouverte de %s absente de l'index" % nom)
        else:
            m = re.search(r"« (.*) »", idx[k])
            idx[k] = "| `%s` | on relit le socle du chantier %s — **clos** « %s », `%s..%s` |" % (
                nom, lettre, m.group(1) if m else titre, ids[0], ids[-1])
            ecritures.append((chemin_index, "\n".join(idx) + "\n"))
            faits["index"] = 1
    chemin_claude = os.path.join(projet, "CLAUDE.md")
    if not os.path.isfile(chemin_claude):
        gardes.append("CLAUDE.md introuvable")
    else:
        cl = lignes_de(chemin_claude)
        k = next((k for k, l in enumerate(cl) if l.startswith("| jouer une fiche du chantier %s (" % lettre)
                  and "`%s`" % courant in l), None)
        if k is None:
            gardes.append("ligne « jouer une fiche du chantier %s » absente de CLAUDE.md" % lettre)
        else:
            del cl[k]
            if not any(l.startswith(ROUTAGE_CLOS) for l in cl):
                cl.insert(k, "%s `%s` — sa ligne y nomme le fichier de fiches |" % (ROUTAGE_CLOS, index or "00-INDEX.md"))
            faits["routage"] = 1
        if a.resume:
            if resume_claude(cl, lettre, a.resume, date, gardes):
                faits["résumé"] = 1
        if faits["routage"] or faits.get("résumé"):
            ecritures.append((chemin_claude, "\n".join(cl) + "\n"))

    # 1 ter. la ZONE:bilan de la page du chantier
    chemin_page = os.path.join(projet, os.path.dirname(courant), "artefacts", nom[:-3] + ".html")
    if not os.path.isfile(chemin_page):
        gardes.append("page du chantier introuvable : %s" % chemin_page)
    else:
        pg = lire(chemin_page)
        try:
            d, f = zone(pg, "bilan", "\n", "  </section>")
            db, fb = zone(pg, "blocage", "\n", "  </section>")
        except ValueError as e:
            gardes.append("page du chantier : %s" % e)
        else:
            corps = ('  <section>\n    <h2>Chantier clos le %s</h2>\n    <div class="bilan">\n      <p>Livré : %s</p>\n'
                     % (date, esc(a.livre))) + ('      <p>Surpris : %s</p>\n' % esc(a.surpris) if a.surpris else "") + "    </div>\n"
            bloc = pg[db:fb]
            bloc = re.sub(r"^  <section>", "  <section hidden>", bloc, count=1)
            pg = pg[:db] + bloc + pg[fb:d] + corps + pg[f:] if db < d else pg[:d] + corps + pg[f:db] + bloc + pg[fb:]
            couts_page = []    # les gardes de regenerer portent déjà « GARDE: »
            try:
                pg = regenerer(pg, chemin_fiches, {}, [], date, couts_page)[0]
            except ValueError as e:
                couts_page.append("page du chantier : coûts non régénérés — %s" % e)
            gardes.extend(re.sub(r"^GARDE: ", "", g) for g in couts_page)
            ecritures.append((chemin_page, pg))
            faits["bilan"] = 1

    # 2. CHANTIER.md
    for k, l in enumerate(carte_):
        m = re.match(r"^(\s*-\s*\*\*(?:fichier de fiches courant|artefact du chantier)\*\*\s*:\s*)", l)
        if m:
            carte_[k] = m.group(1) + "aucun"
    texte = "\n".join(carte_) + "\n"
    j = texte.find("Lettres de fiche déjà prises")
    if j < 0:
        sortie.write("GARDE: ligne « Lettres de fiche déjà prises » absente de CHANTIER.md\n")
        return 1
    if lettre not in lettres_prises(carte_):
        k = texte.find(". Un nouveau chantier", j)
        k = k if k >= 0 else texte.find("\n", j)
        texte = texte[:k] + ", %s (%s)" % (lettre, titre) + texte[k:]

    # 3. la feuille de route
    page = page_feuille(projet)
    html = lire(page) if os.path.isfile(page) else None
    total = None
    if html is not None:
        try:
            d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
        except ValueError as e:
            sortie.write("GARDE: %s\n" % e)
            return 1
        anciens = lignes_clos(html[d:f])
        lien = cellule_md(titre) if url.lower().startswith("aucun") else '<a href="%s">%s</a>' % (esc(url), cellule_md(titre))
        ligne = ('          <tr>\n            <td>%s <span class="badge" data-etat="clos">clos</span></td>\n'
                 '            <td class="mono">%s</td><td class="mono">%s</td>\n'
                 '            <td class="mono">%s</td>\n            <td>%s</td>\n          </tr>\n'
                 % (lien, plage(ids), date, "non mesuré" if a.tokens is None else arrondi(a.tokens), cellule_md(a.livre)))
        corps = ligne + "".join(anciens)
        html = html[:d] + corps + html[f:]
        total = total_clos(corps)
        html = re.sub(r"(Total cumulé</td><td class=\"mono\"><strong>).*?(</strong></td><td[^>]*>).*?(</td>)",
                      lambda m: m.group(1) + arrondi(total) + m.group(2) + estimation_usd(total) + m.group(3),
                      html, count=1)
        # Le résumé du bloc repliable : ce qu'on voit sans déplier.
        html = re.sub(r"(<span class=\"resume-clos\">).*?(</span>)",
                      lambda m: m.group(1) + resume_clos(len(anciens) + 1, total) + m.group(2),
                      html, count=1)
        etat = champ(carte_, "fichier d'état")
        try:
            zone(html, "todo", "<tbody>\n", "        </tbody>")
            zone(html, "encours", "\n", "  </section>")
            if not etat or not os.path.isfile(os.path.join(projet, etat)):
                raise ValueError("fichier d'état introuvable : %s" % etat)
        except ValueError as e:
            sortie.write("GARDE: %s — rien d'écrit\n" % e)
            return 1

    with open(chemin_fiches, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(fiches_) + "\n")
    with open(chemin_carte, "w", encoding="utf-8", newline="") as fh:
        fh.write(texte)
    for chemin, contenu in ecritures:
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write(contenu)
    for g in gardes:
        sortie.write("GARDE: %s — le reste est écrit\n" % g)
    if html is None:
        sortie.write("GARDE: feuille de route introuvable : %s — CHANTIER.md et fiches écrits\n" % page)
    else:
        try:
            html, bilan = feuille(projet, html, None, date)
        except ValueError as e:
            sortie.write("GARDE: %s — CHANTIER.md et fiches écrits, feuille non écrite\n" % e)
            return 1
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(html)
        sortie.write(bilan + " · réécrite — %s\n" % page)
    sortie.write("CLOS %s %s · total %s · routage %d · index %d · bilan %d%s — %s\n" % (
        lettre, fait, "non mesuré" if total is None else milliers(total), faits["routage"], faits["index"], faits["bilan"],
        " · résumé %d" % faits.get("résumé", 0) if a.resume else "", projet))
    return 0


# --- ouvrir ------------------------------------------------------------------

LIGNE_FICHIER = re.compile(r"^\| `\d\d")


def cmd_ouvrir(a, sortie):
    projet = a.projet
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return 1
    fichier = a.fiches.replace("\\", "/")
    chemin_fiches = os.path.join(projet, fichier)
    fiches_ = lignes_gardees(chemin_fiches, "fichier de fiches", fichier)
    ids = [l.split()[1] for l in fiches_ if TITRE.match(l)]
    if not ids:
        sortie.write("GARDE: aucune fiche dans %s\n" % fichier)
        return 1
    if any(l.startswith("**CLOS**") for l in fiches_):
        sortie.write("GARDE: %s porte **CLOS** — un chantier clos ne se rouvre pas\n" % fichier)
        return 1
    chemin_carte = os.path.join(projet, "CHANTIER.md")
    carte_ = lignes_de(chemin_carte)
    courant = fichier_courant("\n".join(carte_))
    if courant and courant != fichier:
        sortie.write("GARDE: un chantier est déjà ouvert : %s\n" % courant)
        return 1
    lettre, fait = lettre_de(ids[0]), "%s..%s" % (ids[0], ids[-1])
    url = retirer_chevrons_url(a.artefact) or (champ(carte_, "artefact du chantier", "aucun") if courant else "aucun")
    gardes = []

    # 1. CHANTIER.md
    vus = set()
    for k, l in enumerate(carte_):
        m = re.match(r"^(\s*-\s*\*\*(fichier de fiches courant|artefact du chantier)\*\*\s*:\s*)", l)
        if m:
            carte_[k] = m.group(1) + ("%s (%s)" % (fichier, fait) if m.group(2).startswith("fichier") else url)
            vus.add(m.group(2))
    for nom in ("fichier de fiches courant", "artefact du chantier"):
        if nom not in vus:
            sortie.write("GARDE: ligne « %s » absente de CHANTIER.md — rien d'écrit\n" % nom)
            return 1

    # 2. l'index
    ecritures = []
    nom = os.path.basename(fichier)
    index = champ(carte_, "index")
    chemin_index = os.path.join(projet, index) if index else None
    n_index = "+0"
    if not chemin_index or not os.path.isfile(chemin_index):
        gardes.append("index introuvable : %s" % index)
    else:
        idx = lignes_de(chemin_index)
        if not any(l.startswith("| `%s` |" % nom) for l in idx):
            rangs = [k for k, l in enumerate(idx) if LIGNE_FICHIER.match(l)]
            if not rangs:
                gardes.append("aucune ligne de fichier dans %s" % index)
            else:
                rang = max(rangs, key=lambda k: int(idx[k][3:5]))
                idx.insert(rang + 1,"| `%s` | on joue une fiche `%s*` — chantier **ouvert** « %s », `%s` |"
                           % (nom, lettre, a.titre, fait))
                ecritures.append((chemin_index, idx))
                n_index = "+1"
        else:
            # Relancé sur le fichier ouvert : seule la plage de sa ligne suit le fichier (chantier PLA).
            k = next(k for k, l in enumerate(idx) if l.startswith("| `%s` |" % nom))
            ligne = re.sub(r"`[^`]*` \|$", "`%s` |" % fait, idx[k])
            if "**ouvert**" in idx[k] and ligne != idx[k]:
                idx[k] = ligne
                ecritures.append((chemin_index, idx))
                n_index = "~1"

    # 3. le routage de CLAUDE.md
    chemin_claude = os.path.join(projet, "CLAUDE.md")
    n_routage = 0
    if not os.path.isfile(chemin_claude):
        gardes.append("CLAUDE.md introuvable")
    else:
        cl = lignes_de(chemin_claude)
        if not any("`%s`" % fichier in l for l in cl if l.startswith("|")):
            rang = next((k for k, l in enumerate(cl) if l.startswith(ROUTAGE_CLOS)),
                        next((k for k, l in enumerate(cl) if l.startswith("| relire le chantier")), None))
            if rang is None:
                gardes.append("aucune ligne « relire un chantier clos » ni « relire le chantier » dans CLAUDE.md")
            else:
                titre = a.titre[:1].lower() + a.titre[1:]
                cl.insert(rang, "| jouer une fiche du chantier %s (%s) | `%s` — chantier **ouvert**, par `/vlp:tache %s<n>` |"
                          % (lettre, titre, fichier, lettre))
                ecritures.append((chemin_claude, cl))
                n_routage = 1

    # 4. la session du cadrage, avant la première ligne `## ` : le socle dans un vrai fichier,
    # jamais entre le marqueur d'une fiche et son titre (chantier CAD). Un titre de fiche en
    # commence une : `next` la trouve toujours.
    n_session = 0
    s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if s and s not in sessions_de(fiches_):
        k = next(k for k, l in enumerate(fiches_) if l.startswith("## "))
        fiches_[k:k] = ["**Session** : %s" % s, ""]
        ecritures.append((chemin_fiches, fiches_))
        n_session = 1

    ecritures.append((chemin_carte, carte_))
    for chemin, lignes in ecritures:
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lignes) + "\n")
    for g in gardes:
        sortie.write("GARDE: %s — le reste est écrit\n" % g)
    sortie.write("OUVERT %s %s · index %s · routage +%d · session +%d · artefact %s — %s\n"
                 % (lettre, fait, n_index, n_routage, n_session, url, projet))
    return 0


# --- entrée ------------------------------------------------------------------

def main(argv, sortie=None, entree=None, erreur=None):
    sortie = sortie or sys.stdout
    p = argparse.ArgumentParser(prog="vlp.py", description="La mécanique du kit vlp.")
    sous = p.add_subparsers(dest="cmd", required=True)
    c = sous.add_parser("carte")
    c.add_argument("dossier", nargs="?", default=None)
    c.add_argument("--python")
    c.add_argument("--relais", action="store_true")
    e = sous.add_parser("extraire")
    e.add_argument("fichier")
    e.add_argument("fiche")
    s = sous.add_parser("socle")
    s.add_argument("fichier")
    se = sous.add_parser("sessions")
    se.add_argument("fichier")
    co = sous.add_parser("cout")
    co.add_argument("fichier")
    co.add_argument("--session", action="store_true")
    li = sous.add_parser("lignes")
    li.add_argument("chemins", nargs="+")
    eq = sous.add_parser("equiper")
    eq.add_argument("dossier")
    eq.add_argument("--contexte", default="context AI")
    v = sous.add_parser("valider")
    v.add_argument("fichiers", nargs="+")
    v.add_argument("--plan", action="store_true")
    pg = sous.add_parser("page")
    pg.add_argument("fichier")
    pg.add_argument("page", nargs="?")
    pg.add_argument("--note", nargs=2, action="append", metavar=("FICHE", "TEXTE"))
    pg.add_argument("--journal", action="append")
    pg.add_argument("--creer", action="store_true")
    pg.add_argument("--projet")
    pg.add_argument("--titre")
    pg.add_argument("--resultat")
    pg.add_argument("--verifier", action="store_true")
    pg.add_argument("--date")
    sous.add_parser("hook")
    sous.add_parser("filet")
    et = sous.add_parser("etat")
    et.add_argument("contexte")
    rv = sous.add_parser("renvois")
    rv.add_argument("projet")
    nv = sous.add_parser("niveau")
    nv.add_argument("projet")
    nv.add_argument("--ecrire", action="store_true")
    nv.add_argument("--date")
    fe = sous.add_parser("feuille")
    fe.add_argument("projet")
    fe.add_argument("--todo")
    fe.add_argument("--verifier", action="store_true")
    fe.add_argument("--date")
    cl = sous.add_parser("clore")
    cl.add_argument("projet")
    cl.add_argument("--livre", required=True)
    cl.add_argument("--tokens", type=int)
    cl.add_argument("--abandon")
    cl.add_argument("--fait")
    cl.add_argument("--surpris")
    cl.add_argument("--resume")
    cl.add_argument("--date")
    ou = sous.add_parser("ouvrir")
    ou.add_argument("projet")
    ou.add_argument("--fiches", required=True)
    ou.add_argument("--titre", required=True)
    ou.add_argument("--artefact")
    lr = sous.add_parser("lire")
    lr.add_argument("chemins", nargs="+")
    co2 = sous.add_parser("cocher")
    co2.add_argument("fichier")
    co2.add_argument("fiche")
    co2.add_argument("--resolu")
    co2.add_argument("--date")
    cv = co2.add_mutually_exclusive_group()
    cv.add_argument("--verifier", action="store_true")
    cv.add_argument("--refuser")
    rl = sous.add_parser("relecture")
    rl.add_argument("fiche", nargs="?")
    rl.add_argument("--sha")
    rl.add_argument("--retirer", action="store_true")
    a = p.parse_args(argv)
    try:
        return repartir(a, sortie, entree, erreur)
    except Absent as e:
        sortie.write("GARDE: %s\n" % e)
        return 1


def repartir(a, sortie, entree, erreur):
    """Le dispatch. Une `Absent` levée ici est gardée par `main`, et nulle part
    ailleurs : un chemin de `CHANTIER.md` ne fait plus tomber le script."""
    if a.cmd == "lire":
        return cmd_lire(a.chemins, sortie)
    if a.cmd == "ouvrir":
        return cmd_ouvrir(a, sortie)
    if a.cmd == "clore":
        return cmd_clore(a, sortie)
    if a.cmd == "feuille":
        return cmd_feuille(a, sortie)
    if a.cmd == "renvois":
        return cmd_renvois(a.projet, sortie)
    if a.cmd == "niveau":
        return cmd_niveau(a, sortie)
    if a.cmd == "etat":
        sortie.write("ETAT=%s\n" % nom_etat(a.contexte))
        return 0
    if a.cmd == "hook":
        return cmd_hook(entree or sys.stdin, sortie, erreur or sys.stderr)
    if a.cmd == "filet":
        return cmd_filet(entree or sys.stdin, sortie, erreur or sys.stderr)
    if a.cmd == "page":
        chemin_garde(a.fichier)
        if a.page is None:
            a.page = page_du_fichier(a.fichier)
        return cmd_page(a, sortie)
    if a.cmd == "carte":
        if a.python:
            return carte_injectee(a.dossier or os.getcwd(), a.python, a.relais, sortie)
        return carte(a.dossier or os.getcwd(), sortie)
    if a.cmd == "valider":
        return cmd_valider(a.fichiers, sortie, a.plan)
    if a.cmd == "equiper":
        return cmd_equiper(a.dossier, a.contexte, sortie)
    if a.cmd == "lignes":
        return cmd_lignes(a.chemins, sortie)
    if a.cmd == "relecture":
        return cmd_relecture(a, sortie)
    chemin_garde(a.fichier)
    if a.cmd == "extraire":
        return cmd_extraire(a.fichier, a.fiche, sortie)
    if a.cmd == "cocher":
        return cmd_cocher(a, sortie)
    if a.cmd == "socle":
        return cmd_socle(a.fichier, sortie)
    if a.cmd == "cout":
        return cmd_cout(a.fichier, a.session, sortie)
    return cmd_sessions(a.fichier, sortie)


if __name__ == "__main__":
    # Sous Windows, la console n'est pas en UTF-8 : sans ceci, les accents
    # sortent illisibles.
    for flux in (sys.stdin, sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
