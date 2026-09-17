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
  fichier (aucune : `SESSIONS 0 — pas de total`, sort 0). `--session` :
  `SESSION=<CLAUDE_CODE_SESSION_ID>`, puis (id non vide) la table de cette
  session seule, et celle de cette session plus celles du fichier.
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
- `cocher <fichier> <fiche> [--resolu T] [--date D]` — `[ ]` → `[x]` sur le titre
  de la fiche et, si `CLAUDE_CODE_SESSION_ID` n'est pas vide, `**Session** : <id>`
  avant sa ligne `**Dépend de**` (déjà là : pas redoublée) ; `--resolu` réduit
  un bloc `**Tentatives**` à `**Tentatives** (<date>) — résolu par : T`.
  `COCHÉ <fiche> · Session <id|absente>`. Introuvable ou déjà cochée : `GARDE:`,
  rien écrit, sort 1.
- `page <fichier> [<page.html>]` — régénère la page du chantier depuis le fichier
  de fiches : états, avancement, comptage, coûts (`**Session**`), date. Sans
  page : `<dossier du fichier>/artefacts/<même nom>.html`. Garde
  de la page l'en-tête, les notes, le journal, le blocage et le bilan.
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
  dans la page du chantier, `ZONE:bilan` visible (Livré, Surpris) et
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
  (sinon le premier « relire le chantier ») du routage de `CLAUDE.md`. Une ligne déjà là n'est pas redoublée.
  `OUVERT <lettre> <plage> · index +<n> · routage +<n> · artefact <url> —
  <projet>` ; index ou routage introuvable : `GARDE:`, le reste est écrit.
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

TITRE = re.compile(r"^## [A-Z][0-9]")
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
    """La carte d'une injection `py … --python py; python3 … --python python3 --relais; py … --python py
    --relais; echo fin` (chantier Y, Y1 ; ordre inversé en U4 : sous Windows le message du raccourci Store
    de `python3` tombe après la carte, sous Ubuntu « py: command not found » avant ; le 3e appel remet à 0
    le `$LASTEXITCODE` de PowerShell, que `echo` ne touche pas) : une ligne vide d'abord,
    `PYTHON=<nom>` pour le corps de la skill, et rien au relais si le premier lancement a déjà écrit la carte."""
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
    """`mesure-tokens.py` sur les sessions du fichier, sans `tr` ni `xargs` : les
    commandes du kit tournent aussi sous PowerShell (chantier Y)."""
    import contextlib
    ids = sessions_de(lignes_de(chemin))
    tables = []
    if session:
        s = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
        sortie.write("SESSION=%s\n" % s)
        if not s:
            return 0
        tables = [[s], [s] + [i for i in ids if i != s]]
    elif ids:
        tables = [ids]
    else:
        sortie.write("SESSIONS 0 — pas de total\n")
        return 0
    code = 0
    for argv in tables:
        with contextlib.redirect_stdout(sortie):
            code = mesure().main(argv) or code
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


PLAN = re.compile(r"^## [A-Z][0-9]|^\*\*(Dépend de|Tentatives|Critère de fin)\*\*")


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

MARQUE = re.compile(r"^<!-- FICHE:[A-Z][0-9]+ -->$")


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


# --- page --------------------------------------------------------------------

# Le seuil vit dans le script (SEUIL_PAGE) : ici, il est défini et cité.
SEUIL_PAGE = 250
GABARIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "artefact-chantier.html")
LI_FICHE = re.compile(r'[ \t]*<li class="fiche"[^>]*>.*?</li>\n?', re.S)
UL_FICHES = re.compile(r'(<ul class="fiches">)(.*?)(\n[ \t]*</ul>)', re.S)
COUT = re.compile(r"\((\d[\d ]*)\) · (\d+) tours · ([\d,]+) \$")
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


def milliers(n):
    return "{:,}".format(n).replace(",", " ")


def arrondi(n):
    """La convention de coût en tête de templates/artefact-chantier.html."""
    if n < 1000:
        return str(n)
    valeur, unite = (n / 1_000_000, "M") if n >= 1_000_000 else (n / 1000, "k")
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
    """(total, tours, usd) lus sur une ligne de coût affichée, ou None."""
    c = texte and COUT.search(texte)
    if not c:
        return None
    from decimal import Decimal
    return int(c.group(1).replace(" ", "")), int(c.group(2)), Decimal(c.group(3).replace(",", "."))


def couts(fiches_, anciens, ancien_total, gardes):
    """({id: ligne de coût}, (total, tours, usd) ou None). Une session portée
    par plusieurs fiches : les premières gardent le coût déjà affiché (l'écart
    du compteur à leur clôture), la dernière prend le reste — moins la part que
    l'ancienne page n'attribuait à aucune fiche (le cadrage joué dans la même
    session), si une seule session est partagée."""
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
            base = (base[0] - c[0], base[1] - c[1], base[2] - c[2])
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
            usd = None if usd is None else usd - base[2]
        for ident in porteurs[:-1]:
            ancien = anciens.get(ident, (None, None, None))[2]
            c = triplet(ancien)
            if not c:
                gardes.append("GARDE: %s partage la session %s sans coût affiché — tout le coût va sur %s"
                              % (ident, s, porteurs[-1]))
                continue
            rendu[ident] = ancien
            total, tours = total - c[0], tours - c[1]
            usd = None if usd is None else usd - c[2]
        rendu[porteurs[-1]] = ligne_cout(total, tours, usd)
    mesurees = [r for r in mesures.values() if r]
    if not mesurees:
        return rendu, None
    usd = None if any(r["usd_exact"] is None for r in mesurees) else sum(r["usd_exact"] for r in mesurees)
    return rendu, (sum(r["total"] for r in mesurees), sum(r["tours"] for r in mesurees), usd)


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
    plage = "%s–%s" % (fiches_[0][0], fiches_[-1][0]) if fiches_ else ""
    remplacements = [
        (r"<title>.*?</title>", "<title>%s — %s</title>" % (esc(projet), esc(titre))),
        (r'(<div class="eyebrow">).*?(</div>)', r"\g<1>%s · fiches %s\g<2>" % (esc(projet), plage)),
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
    cout, total = couts(fiches_, anciens, ancien_total and ancien_total.group(1), gardes)
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
    html = re.sub(r'\n[ \t]*<p class="mono cout-total">.*?</p>', "", html, flags=re.S)
    bloc = "\n" + "\n".join(items)
    if total:
        bloc_total = '\n    <p class="mono cout-total">%s : %s</p>' % (prefixe, ligne_cout(*total))
    else:
        bloc_total = ""
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
        fiche_bloquee = re.match(r"\s*([A-Z][0-9]+)", blocage.group(3))
        if fiche_bloquee and etat.get(fiche_bloquee.group(1)) == "faite":
            html = html[:blocage.start()] + "<section hidden>" + html[blocage.start() + len("<section>"):]
    for texte in journal:
        ligne = '      <li><time datetime="%s">%s</time><span>%s</span></li>' % (date, date, esc(texte))
        html, n = re.subn(r'(<ul class="journal">.*?)(\n[ \t]*</ul>)', lambda m: m.group(1) + "\n" + ligne + m.group(2),
                          html, count=1, flags=re.S)
        if not n:
            raise ValueError("page : journal introuvable")
    html = re.sub(r'(Mis à jour le <span class="mono">).*?(</span>)', lambda m: m.group(1) + date + m.group(2), html, count=1)
    return html, fiches_, etat, total


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
        html, fiches_, etat, total = regenerer(html, a.fichier, dict(a.note or []), a.journal or [], date, gardes)
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return 1
    with open(a.page, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    n = html.count("\n") + (0 if html.endswith("\n") else 1)
    for g in gardes:
        sortie.write(g + "\n")
    sortie.write("PAGE %s · %s · %d lignes · total %s\n"
                 % (a.page, comptage(fiches_, etat), n, ligne_cout(*total) if total else "non mesuré"))
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


def champ(lignes, nom, defaut=None):
    """La valeur d'une ligne `- **nom** : valeur` de `CHANTIER.md`."""
    motif = re.compile(r"^\s*-\s*\*\*%s\*\*\s*:\s*(.+?)\s*$" % re.escape(nom))
    for l in lignes:
        m = motif.match(l)
        if m:
            return m.group(1)
    return defaut


def lettres_prises(lignes):
    texte = " ".join(l for l in lignes if l.strip())
    i = texte.find("Lettres de fiche déjà prises")
    if i < 0:
        return []
    fin = texte.find("Un nouveau chantier", i)
    return re.findall(r"(?:: |, )([A-Z]) \(", texte[i:fin if fin > 0 else None])


def plage(ids):
    return "%s–%s" % (ids[0], ids[-1]) if len(ids) > 1 else ids[0]


def cellule_md(texte):
    texte = esc(texte.replace("\\|", "|"))
    return CODE.sub(lambda m: '<span class="mono">%s</span>' % m.group(1), texte)


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
        if ids and ids[0][0] not in lettres:
            lettres.append(ids[0][0])
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


# --- clore -------------------------------------------------------------------

CLOS_LIGNE = "**CLOS** le %s. Ne se rejoue pas — ne sert plus qu'à relire son socle."
BRUT = re.compile(r'<td class="mono">[^<]*\(([\d  ]+)\)</td>')
ENTREE_CLOS = re.compile(r"^- Clos le \S+ : .* \(chantier [A-Z]\)\.$")
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
    texte = re.sub(r"\s*\(chantier %s\)$" % re.escape(lettre), "", texte.rstrip("."))
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
    lettre = ids[0][0]
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
        anciens = re.findall(r"          <tr>\n.*?          </tr>\n", html[d:f], re.S)
        anciens = [r for r in anciens if '<td class="mono">&lt;' not in r]
        lien = cellule_md(titre) if url.lower().startswith("aucun") else '<a href="%s">%s</a>' % (esc(url), cellule_md(titre))
        ligne = ('          <tr>\n            <td>%s <span class="badge" data-etat="clos">clos</span></td>\n'
                 '            <td class="mono">%s</td><td class="mono">%s</td>\n'
                 '            <td class="mono">%s</td>\n            <td>%s</td>\n          </tr>\n'
                 % (lien, plage(ids), date, "non mesuré" if a.tokens is None else arrondi(a.tokens), cellule_md(a.livre)))
        corps = ligne + "".join(anciens)
        html = html[:d] + corps + html[f:]
        total = sum(int(re.sub(r"\D", "", n)) for n in BRUT.findall(corps)) + (a.tokens if a.tokens is not None and a.tokens < 1000 else 0)
        html = re.sub(r"(Total cumulé</td><td class=\"mono\"><strong>).*?(</strong>)",
                      lambda m: m.group(1) + arrondi(total) + m.group(2), html, count=1)
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
    lettre, fait = ids[0][0], "%s..%s" % (ids[0], ids[-1])
    url = a.artefact or (champ(carte_, "artefact du chantier", "aucun") if courant else "aucun")
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
    n_index = 0
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
                n_index = 1

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

    ecritures.append((chemin_carte, carte_))
    for chemin, lignes in ecritures:
        with open(chemin, "w", encoding="utf-8", newline="") as fh:
            fh.write("\n".join(lignes) + "\n")
    for g in gardes:
        sortie.write("GARDE: %s — le reste est écrit\n" % g)
    sortie.write("OUVERT %s %s · index +%d · routage +%d · artefact %s — %s\n"
                 % (lettre, fait, n_index, n_routage, url, projet))
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
    et = sous.add_parser("etat")
    et.add_argument("contexte")
    rv = sous.add_parser("renvois")
    rv.add_argument("projet")
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
    if a.cmd == "etat":
        sortie.write("ETAT=%s\n" % nom_etat(a.contexte))
        return 0
    if a.cmd == "hook":
        return cmd_hook(entree or sys.stdin, sortie, erreur or sys.stderr)
    if a.cmd == "page":
        chemin_garde(a.fichier)
        if a.page is None:
            a.page = os.path.join(os.path.dirname(a.fichier), "artefacts",
                                  os.path.splitext(os.path.basename(a.fichier))[0] + ".html")
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
