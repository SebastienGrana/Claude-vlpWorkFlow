#!/usr/bin/env python3
"""La boucle de `/vlp:enchainer clear` : une session `claude -p` neuve par fiche.

Chaque fiche est jouée comme après un `/clear` suivi de `/vlp:tache <fiche>` : un
processus `claude` neuf, sans rien de la fiche d'avant, dans le dossier du projet.
Seul script du kit qui appelle un modèle ; `vlp.py` reste sans appel modèle.

    boucle.py [dossier] --plafond N [--claude C] [--model M] [--effort E]
              [--permission-mode P] [--budget USD] [--traces DOSSIER]
              [--nuit (--canal C [--chantier X] [--reprendre] | --lancer) [--date AAAA-MM-JJ] [--borne-usd USD]
               [--borne-chantiers N] [--carnet CHEMIN]]

Avant chaque fiche : `vlp.py carte` donne `PROCHAINE=` ; `aucune` arrête. Une fiche
à bloc **Tentatives** arrête sans être jouée. Une fiche `(visuel)` (ligne `ARRÊT:`
d'`extraire`) est jouée, puis arrête : `vlp:tache` la livre sans la cocher. Après
chaque fiche, `vlp.py cocher --verifier` : case vide, hors `(visuel)`, arrête.

Imprime `CLAUDE=`, `PROJET=`, puis par fiche `JOUE <fiche> — trace <jsonl>`,
`FICHE <fiche> · CASE [x|  ] · tours <n> · <coût> $ · <s> s` et le texte rendu
par la session, indenté ; enfin `ARRÊT <raison>` et `TOTAL <n> fiches · <tours>
tours · <coût> $ · <s> s`. Sort 0 sur un arrêt prévu (plafond, aucune, visuel),
1 sinon.

`claude` : `--claude`, sinon celui de `vlp.py claude` — la même recherche que `vlp.py bac`
(`VLP_CLAUDE`, le PATH, puis le CLI de l'app sous `Packages`, puis sous `%APPDATA%`).
Un `--claude` en `.py` se lance par ce Python : c'est le faux `claude` des tests.
Permissions : `--permission-mode`, `auto` par défaut — personne ne répond en `-p` —,
plus `git add` et `git commit` (`AUTORISES`), sauf `--amend` et `--no-verify` en tête.
Traces : `--traces`, sinon un dossier temporaire neuf `vlp-boucle-*`, gardé.

`--nuit` (chantier NUI) tient le carnet de `carnet.py` et ouvre `--canal` (exigé), `--chantier` (sans lui : la
boucle d'un canal, NUI7, plus bas), `--date`, `--borne-usd`, `--borne-chantiers` et `--carnet` (absolu ; défaut :
celui de `--date`, sinon du jour, fixé au lancement) ;
`--plafond` y devient facultatif, exigé sans `--nuit`. Sans `--nuit` rien de tout cela ne s'applique
et aucun carnet n'est touché. Avant chaque session — jamais pendant —, la boucle relit le carnet :
un `stop` de n'importe quel canal rend `ARRÊT STOP — <raison>` (sort 1) ; la borne atteinte rend
`ARRÊT borne atteinte — <$ ou chantiers>` (sort 0), chantier ouvert. Une session déjà partie va
au bout : la borne se dépasse d'une session par canal au plus. Après chaque session, une ligne du
carnet (nuit, canal, chantier, role, fiche, modele_demande, modeles_vus, tours_cli, usd_cli, duree_s,
issue, garde, plugin_retard, session) ; la session fille reçoit `VLP_CARNET`, `VLP_CANAL` et `VLP_NUIT=1`.

Sous `--nuit`, chaque session prend ses réglages dans `ROLES`, en tête du fichier : les cinq rôles
(découper, jouer, relire, relance, clore) — prompt, modèle, repli, effort, outils, `--max-turns`,
`--max-budget-usd`, timeout —, la source de chaque plafond en commentaire. Sans `--nuit`, `jouer()` bâtit
la commande d'avant (REG). `main()` joue le rôle jouer, puis relire (NUI5) ; `jouer(…, role=…)` joue les autres,
test-boucle.py le charge comme module, et pour un test `ROLES[<rôle>]["timeout"]` se remplace sur ce module.
Toute session `--nuit` : un `--session-id` neuf, `--permission-prompts none`, le timeout à `subprocess.run`.
Issue de chaque session, dans la ligne du carnet : `timeout`, `coupure` (aucune ligne `result`), `plafond`
(`subtype` `error_max_*`), `limite` (texte du `result`), `pas partie` (`is_error`, ou aucun message
`assistant`), `ratée` (le contrôle du rôle a échoué), `jouée`. `pas partie` et `limite` écrivent une ligne
`stop` : la boucle rend `ARRÊT STOP`, sort 1. Limite « Opus » : les rôles Opus passent à `claude-sonnet-5-5`
jusqu'au reset lu dans le message (illisible : fin de la nuit), une note au carnet, la session relancée une
fois (`BASCULE`) ; « session » ou « weekly » : `stop`. Les `permission_denials` ne classent pas : leur nombre
va au carnet (`garde`).

Relire avant le commit (NUI5, sous `--nuit` seulement) : le rôle jouer n'a ni `git add` ni `git commit`
(`AUTORISES` ne lui va plus ; `INTERDITS` reste). Après sa session, `cocher --verifier` : case cochée sans
`TÊTE`, la session du rôle relire (`relecture <fiche>`, sans `--sha`) ; son premier mot est lu contre
`VERDICTS` de vlp.py, aucun verdict valant `REFUSÉE`. ACCEPTÉE : `cocher --session <relire> --role relire`,
puis `git add -A` et `git commit -m "<fiche> : <titre>"` ; un commit refusé (pre-commit) arrête, sortie 1.
REFUSÉE : `cocher --refuser "<1re ligne du result>"` puis `cocher --session`, l'arbre laissé tel quel ;
`relire()` rend `refuse`, `motif`, `refus_n` (celui de `cocher`), `cause` (le mot entre le verdict et ` :`,
`aucun-verdict` sans verdict), `reecriture` et `erreur_avant` (la ligne `Erreur :` d'avant) à
`relire_et_relancer` (NUI6, ci-dessous). `TÊTE` (la session de jeu a
commité malgré tout) : la relecture part avec ` --sha HEAD` ; REFUSÉE : `git revert --no-edit HEAD` d'abord,
puis les deux `cocher` ; ACCEPTÉE : `cocher --session`, puis un commit de cette ligne seule, sujet
`<fiche> : session de relecture`. La ligne `relire` du carnet porte `refus_n`, `cause` et `garde` (commit
refusé, `TÊTE`) ; le coût du relecteur entre au `TOTAL`.

Relancer ou arrêter (NUI6, sous `--nuit` seulement) : la boucle tient elle-même, par fiche, son `n` de refus
et le dernier motif — `cocher --resolu` de la relance remplace le bloc Tentatives, donc le fichier ne s'en
souvient pas. Départ : lu par `extraire` avant la première session de la fiche (`tentatives()` : `n` = lignes
numérotées égales à `ESSAI_REFUSE` de vlp.py, motif = la ligne `Erreur :`). Un bloc de refus seuls n'arrête plus
la boucle ; tout autre bloc, si. À chaque REFUSÉE (ou aucun verdict), `garde_de` tranche, dans cet ordre :
`meme-erreur` (motif égal au dernier), `refus-max` (`n` ≥ `REFUS_MAX`), puis la cause — `copie` : une session du
rôle `relance` sur l'arbre tel quel (aucun revert, rien de commité), puis la même chaîne de relecture ;
`fiche` : `cause-fiche`, la ligne `RÉÉCRITURE :` au carnet ; toute autre, aucun verdict compris : `sans-cause`,
`cause` valant `aucune`. Un arrêt écrit une ligne du carnet (`garde`, `refus_n`, `cause`, `reecriture`, sans
`role`) et rend `ARRÊT <fiche> … garde <garde>`, sortie 1. La ligne `relance` du carnet porte `refus_n` et `cause`.

Vérification de nuit (NUI6) : si CHANTIER.md porte `- **vérification de nuit** : <commande>` (lue par `champ`
de vlp.py), le shell la lance dans la racine du projet avant la première fiche jouée du chantier, puis après le
commit de chaque ACCEPTÉE, bornée par `TIMEOUT_S` ; un code ≠ 0 ou le délai : `ARRÊT <fiche> : garde
verification`, sortie 1. Libellé absent : rien, ni ligne ni garde.

La boucle d'un canal (NUI7, `--nuit` sans `--chantier`) : `vlp.py plan lire --date --canal` donne les chantiers du
canal, dans l'ordre, et la borne du plan (`--borne-usd`, `--borne-chantiers` la remplacent) ; `--date` (défaut : le
jour du lancement, lu une fois) nomme le plan, les branches et le carnet par défaut ; `--plafond`, s'il est donné,
borne les fiches jouées de tout le canal. Un chantier déjà ouvert au départ arrête le canal. Par chantier : `STOP`,
borne et plafond relus (le canal s'arrête, chantier ouvert) ; un chantier dont « Dépend de » (TODO) nomme un code mis
de côté ou sauté est sauté sans session (`SAUTÉ`, carnet `saute:<code>`, `issue` `pas partie`) ; la branche
`nuit/<date>-<canal>-<code>` part du dernier chantier réussi (`HEAD` au départ) ; `découper` ; `vlp.py valider` et le
nombre de fiches contre 2 × la borne haute du coût de sa ligne TODO ; le commit `Chantier <code> ouvert (nuit) : <n>
fiches` ; les fiches comme sous `--chantier` (NUI5, NUI6) ; sur `aucune`, `cocher --session <id> --role clore` puis la
session `clore` (`/vlp:tache`), qui commite. Réussi : plus de fichier de fiches courant, arbre propre — sa pointe est la
base du suivant. Mis de côté (`MIS DE CÔTÉ`, carnet `mis-de-cote:<raison>`) : découpage sans fichier, `valider` en
écart ou en avertissement, trop de fiches, TODO illisible, un arrêt de chantier de NUI6 (sa ligne `ARRÊT` imprimée
telle quelle), une session de jeu ou de relance qui clôt le chantier (carnet `cloture-hors-role`), une clôture qui
laisse le chantier ouvert ou l'arbre sale. `mettre_de_cote` est seule à le faire : arbre propre, rien ; sinon `git
add -A` et le commit WIP (`WIP_SUJET` de vlp.py, relu par `de_cote`). Un commit de la boucle refusé par un hook (WIP : carnet `wip-refuse`)
arrête le canal, arbre tel quel — jamais `--no-verify`. `lire_carte` lit `PLUGIN_RETARD=` : son nombre va à
`plugin_retard` des lignes. Sort 0 quand le plan est fini ou la borne atteinte, 1 sur un `STOP` ou un arrêt de canal.

Une nuit coupée (NUI8, sous `--nuit` seulement). Avant chaque session, une `note` `depart <rôle>` (canal, chantier, fiche,
session : l'id de `--session-id`) ; sans ligne de session au même id, la session a été coupée. Une session sans ligne
`result` (issues `timeout` et `coupure` : l'issue tient à cette absence, jamais au code de sortie — 143 sous POSIX, 1 sous
win32) est mesurée dans sa transcription par `mesure-tokens.py` (`mesure_kit` : `resoudre`, puis `mesurer`) : `usd_kit` et
`tours_kit` sur sa ligne, `usd_cli` et `tours_cli` à null, jamais 0 ; transcription introuvable : la `garde` le dit, et le pot
du carnet compte le plafond de son rôle (`plafonds`, pris dans `ROLES`). Son travail n'est pas à croire : le chantier se met
de côté, que ce soit le jeu, la relance, la relecture, le découpage ou la clôture qui ait été coupé.
`--reprendre` (avec `--nuit`, `--canal`, `--carnet` ; sans `--chantier` ; la date est celle du nom du carnet, jamais de
l'horloge), lancé dans le worktree du canal après un terminal fermé, une veille ou un redémarrage, fait dans l'ordre :
(a) chaque `depart` du canal sans fin reçoit sa ligne `coupure`, coût relu comme ci-dessus ; (b) le chantier en cours du canal
— une ligne au carnet, ni clos (une session `clore` jouée) ni mis de côté — : session coupée ou arbre sale, il est mis de côté
(WIP, jamais commité en fiche) ; sinon il reprend dans sa branche `nuit/…`, jamais recréée, sans repasser par `découper`
s'il est découpé ; (c) la boucle d'un canal continue sur le reste du plan, depuis le dernier chantier réussi (la note
`base <sha>` écrite au départ du canal sinon). Dossier absent ou sans Git : `GARDE:`, sort 1. Une reprise ne détecte pas un
canal encore vivant : elle suit un terminal fermé, l'humain sait que le canal est mort. Rien à reprendre : rien d'écrit.
Éveil (win32 seulement) : `SetThreadExecutionState` par `ctypes`, `ES_CONTINUOUS | ES_SYSTEM_REQUIRED` au départ de `--nuit`,
`ES_CONTINUOUS` à la fin ; la ligne `ÉVEIL tenu`, ou `ÉVEIL non tenu` (retour 0) et une note au carnet.

Lancer une nuit (NUI9, sous `--nuit` seulement) : `py -3 <kit>/scripts/boucle.py --nuit --lancer <projet>`, la ligne du soir.
`--nuit` sans `--lancer` reste un canal ; `--lancer` refuse `--canal`, `--chantier` et `--reprendre` (une nuit lancée se reprend
par `--reprendre`, NUI8). `--plafond`, `--date`, `--carnet`, `--borne-usd`, `--borne-chantiers`, `--permission-mode` valent pour les
deux canaux ; `--traces` est leur dossier de traces, par défaut celui du carnet (hors Git). Dans l'ordre, sans rien créer avant la
dernière garde : `claude` trouvé une fois (`GARDE: claude introuvable`), passé en `--claude` aux deux canaux ; le projet — branche
`main`, arbre propre, fichier des nuits non ignoré par Git (ignoré, il n'est dans aucun worktree : un tel projet ne se lance pas),
aucun worktree `nuit-<date>-*` ni branche `nuit/<date>-*`, un plan à la date (`vlp.py plan lire`, sa borne lue une fois) ; sinon une
`GARDE:` qui nomme la cause, sortie 1. Puis `.claude/worktrees/` ajouté à `info/exclude` du dépôt commun s'il n'est pas ignoré,
deux worktrees détachés sur `main`, et deux `boucle.py --nuit --canal A|B <worktree>` en parallèle, même carnet. Imprime `DÉPART
<canal> · pid <n> · <worktree>`, chaque ligne des filles préfixée `[A] ` ou `[B] ` (un fil de lecture par fille), `FIN <canal> ·
code <n>` quand l'une sort, puis `RIEN FUSIONNÉ, RIEN POUSSÉ — /vlp:chef le matin`. Sort 0 si les deux sortent 0, sinon 1. Ctrl+C :
`terminate()` aux deux, sort 1. Git n'y est lu que par `branch`, `status`, `check-ignore`, `rev-parse` et `worktree list`, écrit
que par `worktree add` : ni merge, ni push, ni commit, ni checkout.
"""
import argparse
import datetime
import functools
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from typing import Any

import carnet

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
VLP = os.path.join(ICI, "vlp.py")
VLP_COEUR = os.path.join(ICI, "vlp_coeur.py")    # le code de vlp.py, chargé comme module par `kit()` (VIT5)
# Variables de la session qui lance la boucle : la session fille a les siennes.
HERITEES = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID")
# En `auto`, `vlp.py` passe déjà ; `git add` et `git commit` sont refusés (essai du bac,
# 2026-09-26). Seuls ces deux-là s'ajoutent : ni push, ni reset, ni checkout, ni clean.
AUTORISES = [outil + "(git %s:*)" % c for outil in ("Bash", "PowerShell") for c in ("add", "commit")]
# Réécrire le commit d'avant, ou sauter le hook : refusés, écrits en tête de commande.
INTERDITS = [outil + "(git commit %s:*)" % o for outil in ("Bash", "PowerShell")
             for o in ("--amend", "--no-verify", "-n")]
# Découper et relire n'écrivent jamais dans Git : `git add` et `git commit` leur restent refusés.
NON_GIT = [outil + "(git %s:*)" % c for outil in ("Bash", "PowerShell") for c in ("add", "commit")]

OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
REPLI_OPUS = "claude-opus-5,claude-sonnet-5-5"   # socle de NUI, « Modèles par rôle » : pointé, pas décidé ici
# 60 min pour tous les rôles : 4,9 × 735 s (TAU1, `context AI/08-etat.md:2378`) et 2 × 29,3 min/fiche
# (BTN, `context AI/92-essai-parallele.md:87`).
TIMEOUT_S = 60 * 60
REFUS_MAX = 2   # refus d'une même fiche au bout desquels la nuit s'arrête (`refus-max`) — seul endroit du nombre
COUPEES = ("timeout", "coupure")   # issues d'une session sans ligne `result` (NUI4, NUI8) : son travail n'est pas à croire

# Éveil (NUI8) : valeurs de la doc de SetThreadExecutionState, lue le 2026-10-01 :
# https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate
# ES_CONTINUOUS (0x80000000) : l'état posé reste jusqu'au prochain appel qui l'emploie ; ES_SYSTEM_REQUIRED (0x00000001) :
# remet à zéro le minuteur d'inactivité du système. Retour : l'état d'avant, NULL (0) si l'appel échoue.
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

# Les réglages d'une session `--nuit`, un rôle par entrée. `tours` : un entier (non mesuré), ou le fichier
# d'agent dont `lire_max_turns` de vlp.py lit `maxTurns` — jamais recopié. `git` : le rôle commite-t-il.
ROLES = {
    "découper": {
        "prompt": "/vlp:chantier {fiche}", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": False,
        "tours": 150,   # non mesuré
        "usd": 20,      # ≈ 3 × 6,60 $ (PAR5, `context AI/08-etat.md:2379`) : plafond haut, ce 6,60 $ compte du hors-fiche
        "timeout": TIMEOUT_S},
    "jouer": {
        "prompt": "/vlp:tache {fiche}", "agent": None, "modele": SONNET, "repli": None,
        "effort": "low", "git": True,
        "tours": "agents/fiche.md",
        "usd": 5,       # ≈ 2,9 × 1,74 $ (max de PAR7 en `-p`, `context AI/08-etat.md:2373`)
        "timeout": TIMEOUT_S},
    "relire": {
        # d'après l'essai `--agent` de NUI1 (`context AI/08-etat.md`, section NUI1, essai 5) : le modèle
        # est l'ID demandé, pas le `model: opus` de l'agent ; NUI5 ajoute ` --sha HEAD` au prompt (`suite`)
        "prompt": "{fiche}", "agent": "vlp:relecture", "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": False,
        "tours": "agents/relecture.md",
        "usd": 3,       # non mesuré
        "timeout": TIMEOUT_S},
    "relance": {
        "prompt": "/vlp:tache {fiche}", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": "medium", "git": True,
        "tours": "agents/fiche.md",
        "usd": 5,       # comme jouer ; Opus medium jamais mesuré
        "timeout": TIMEOUT_S},
    "clore": {
        # sans fiche, `/vlp:tache` voit `PROCHAINE=aucune` et applique sa clôture (`skills/tache/SKILL.md`, étapes 0 et 7)
        "prompt": "/vlp:tache", "agent": None, "modele": OPUS, "repli": REPLI_OPUS,
        "effort": None, "git": True,   # `cloture.md:72` : la session commite la clôture
        "tours": 60,    # non mesuré
        "usd": 5,       # non mesuré
        "timeout": TIMEOUT_S},
}

# Limite d'usage : forme prise de la doc, https://code.claude.com/docs/en/errors (lue le 2026-10-01 par
# WebFetch, qui résume la page) : « You've hit your session limit · resets 3:45pm », « … weekly limit ·
# resets Mon 12:00am », « … Opus limit · resets 3:45pm » (« Sonnet limit » existe aussi : `stop`).
# Non vérifiée sur le vrai CLI : NUI20 la confirme.
LIMITE_RE = re.compile(r"\s*You've hit your (\w+) limit", re.I)
RESET_RE = re.compile(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)\b", re.I)
FIN = float("inf")   # « fin de la nuit » : un reset illisible
BASCULE = {"jusqu": 0.0}   # instant jusqu'où les rôles Opus tournent en SONNET
_KIT: list[Any] = []   # vlp.py chargé comme module, une fois (`scripts/test-vlp.py:29`)


def kit():
    """Charger une fois le code de vlp.py (`vlp_coeur.py`) comme module : `VERDICTS`, `git_texte`, `lire_max_turns`."""
    if not _KIT:
        spec = importlib.util.spec_from_file_location("vlp_coeur", VLP_COEUR)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _KIT.append(mod)
    return _KIT[0]


def max_tours(role):
    """`--max-turns` du rôle : l'entier de la table, ou le `maxTurns` de son fichier d'agent."""
    t = ROLES[role]["tours"]
    if isinstance(t, int):
        return t
    n = kit().lire_max_turns(os.path.join(ICI, os.pardir, t))
    if n is None:
        raise ValueError("maxTurns illisible dans %s" % t)
    return n


def modele_de(role):
    """Le modèle du rôle : celui de la table, sauf un rôle Opus pendant une bascule."""
    m = ROLES[role]["modele"]
    return SONNET if m == OPUS and time.time() < BASCULE["jusqu"] else m


def reset_de(texte):
    """L'instant du prochain reset lu dans `texte` (heure locale), ou `FIN` s'il est illisible."""
    m = RESET_RE.search(texte)
    if not m:
        return FIN
    heure = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
    maintenant = time.time()
    an, mois, jour = time.localtime(maintenant)[:3]
    cible = time.mktime((an, mois, jour, heure, int(m.group(2) or 0), 0, 0, 0, -1))
    return cible if cible > maintenant else cible + 86400


def vlp(argv, dossier):
    """Rendre (code, sortie) de `vlp.py <argv>` lancé dans `dossier`, comme un sous-processus l'aurait rendu, mais
    appelé dans ce processus (VIT6) : `main` du module de `kit()`, sa sortie capturée, ses fins de ligne traduites
    comme par un tube en mode texte. Dossier courant et environnement sont remis après l'appel ; `SystemExit` rend son
    code, une exception rend 1 et la sortie écrite jusque-là — le traceback, sur stderr, n'était pas lu non plus."""
    import contextlib
    k, sortie, ici, env = kit(), io.StringIO(), os.getcwd(), dict(os.environ)
    os.chdir(dossier)
    try:
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(io.StringIO()):
            code = k.main(argv, sortie, erreur=io.StringIO()) or 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except Exception:   # un traceback : le sous-processus sortait 1
        code = 1
    finally:
        os.chdir(ici)
        os.environ.clear()
        os.environ.update(env)
    texte = sortie.getvalue().replace("\n", "\r\n") if os.name == "nt" else sortie.getvalue()
    return code, texte.replace("\r\n", "\n").replace("\r", "\n")


def trouver_claude(choix):
    if choix:
        return choix
    _, s = vlp(["claude"], os.getcwd())
    return s[len("CLAUDE "):].strip() if s.startswith("CLAUDE ") else None


def claude_de(choix):
    """Le chemin de `claude`, ou None après la GARDE imprimée — celle de `main` et celle du lanceur (NUI9)."""
    claude = trouver_claude(choix)
    if not claude:
        # Le Python du Store (shebang lu par `py`) voit un AppData virtualisé : ni le
        # dossier ni le `.exe`, même par chemin exact. `py -3` lance le vrai (essai, 2026-09-26).
        print("GARDE: claude introuvable — --claude, VLP_CLAUDE ou le PATH ; sous Windows, "
              "lancer par `py -3` (Python : %s)" % sys.executable)
    return claude


class CarteGardee(Exception):
    """La carte a trouvé le projet sans pouvoir dire son chantier — `PROJET=` puis `GARDE:`, sans ligne `COURANT=`
    (plusieurs ouverts, `courant_de`). Ni « aucun » ni un fichier : la boucle ne la prend jamais pour l'un d'eux
    (NUI25) ; le message est la ligne `GARDE:`."""


def lire_carte(dossier):
    """(racine, fichier de fiches, prochaine, retard) — None là où la carte ne dit rien ; `retard` : le nombre
    de commits de la ligne `PLUGIN_RETARD=`, None sans elle. Projet trouvé sans ligne `COURANT=` : `CarteGardee`."""
    _, s = vlp(["carte", dossier], dossier)
    racine = fichier = prochaine = retard = garde = None
    vu_courant = False
    for ligne in s.split("\n"):
        if ligne.startswith("GARDE:") and garde is None:
            garde = ligne.strip()
        if ligne.startswith("PROJET="):
            racine = ligne[len("PROJET="):].strip()
        elif ligne.startswith("PROCHAINE="):
            prochaine = ligne[len("PROCHAINE="):].strip()
        elif ligne.startswith("PLUGIN_RETARD="):
            m = re.match(r"PLUGIN_RETARD=(\d+)", ligne)
            retard = int(m.group(1)) if m else None
        elif ligne.startswith("COURANT=") and not vu_courant:
            # Le chantier du dossier, calculé par `courant_de` seul — jamais la ligne brute de CHANTIER.md (NUI22).
            vu_courant = True
            valeur = ligne[len("COURANT="):].strip()
            fichier = None if valeur == "aucun" else valeur
    if racine and not vu_courant:
        raise CarteGardee(garde or "GARDE: la carte de %s ne dit pas son chantier (pas de ligne COURANT=)" % racine)
    return racine, fichier, prochaine, retard


def carte_dit(racine, ouvert):
    """Le contrôle des sessions `découper` (`ouvert` vrai : la carte nomme un chantier) et `clore` (faux : elle n'en
    nomme aucun). Une carte gardée ne passe ni l'un ni l'autre ; la lecture qui suit la session la rend (NUI25)."""
    try:
        return (lire_carte(racine)[1] is not None) == ouvert
    except CarteGardee:
        return False


def ligne_carnet(a, **champs):
    """Une ligne du carnet de la nuit : nuit, canal, chantier et `plugin_retard` (celui de la dernière carte lue)
    sont communs à toutes celles de la boucle ; `champs` : le reste."""
    carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=a.chantier,
                   plugin_retard=getattr(a, "plugin_retard", None), **champs)


def plafonds():
    """`{rôle: $}` : le `--max-budget-usd` de chaque rôle de `ROLES`, que le pot du carnet compte pour une session
    sans coût mesuré (NUI8) — jamais recopié."""
    return {role: r["usd"] for role, r in ROLES.items()}


def mesure_kit(session):
    """`(usd_kit, tours_kit, garde)` d'une session sans ligne `result`, mesurés dans sa transcription par
    `mesure-tokens.py` (`resoudre` de l'id, puis `mesurer`) : le `usd_exact` en flottant, les tours de la grille.
    Transcription introuvable ou illisible, modèle hors grille : `(None, None, garde)` — jamais 0 —, et le pot
    du carnet compte alors le plafond du rôle."""
    m = kit().mesure()
    chemin, err = m.resoudre(session)
    if chemin is None:
        return None, None, "transcription introuvable pour la session %s — coût non mesuré, le pot compte le plafond du rôle" % session
    r, err = m.mesurer(chemin)
    if r is None:
        return None, None, "transcription illisible (%s) — coût non mesuré, le pot compte le plafond du rôle" % err
    if r["usd_exact"] is None:
        return None, r["tours"], "modèle hors grille (%s) — coût non mesuré, le pot compte le plafond du rôle" % ", ".join(r["inconnus"])
    return float(r["usd_exact"]), r["tours"], None


def appel_eveil(drapeaux):
    """`SetThreadExecutionState(drapeaux)` : l'état d'avant, ou 0 si l'appel échoue (doc Microsoft, en tête du fichier).
    `argtypes` et `restype` en DWORD : `ES_CONTINUOUS | ES_SYSTEM_REQUIRED` (0x80000001) déborde un `c_int`."""
    if sys.platform != "win32":
        return 0
    import ctypes
    from ctypes import wintypes
    try:
        f = ctypes.windll.kernel32.SetThreadExecutionState
        f.argtypes, f.restype = [wintypes.DWORD], wintypes.DWORD
        return int(f(drapeaux))
    except (AttributeError, OSError):
        return 0


def eveil(a, poser=True):
    """Garde la machine éveillée pendant `--nuit`, sous win32 seulement (NUI8). `poser` : `ES_CONTINUOUS |
    ES_SYSTEM_REQUIRED` et la ligne `ÉVEIL tenu` — ou `ÉVEIL non tenu` et une note au carnet, si l'appel rend 0 ;
    sinon `ES_CONTINUOUS` seul, qui rend l'état à la fin, sans rien imprimer."""
    if sys.platform != "win32":
        return
    avant = appel_eveil(ES_CONTINUOUS | ES_SYSTEM_REQUIRED if poser else ES_CONTINUOUS)
    if not poser:
        return
    if avant == 0:
        print("ÉVEIL non tenu", flush=True)
        carnet.noter(a.carnet, a.canal, "ÉVEIL non tenu : SetThreadExecutionState a rendu 0")
    else:
        print("ÉVEIL tenu", flush=True)


def commande(claude, role, fiche, a, modele, session, suite=""):
    """La ligne de commande d'une session. Sans `--nuit` : celle d'avant les rôles (REG).
    `suite` : ce qui s'ajoute au prompt du rôle (` --sha HEAD` pour relire)."""
    cmd = [sys.executable, claude] if claude.endswith(".py") else [claude]
    commun = ["--output-format", "stream-json", "--verbose", "--permission-mode", a.permission_mode]
    if not a.nuit:  # sans --nuit : la commande d'aujourd'hui, la table ne sert pas
        cmd += ["-p", "/vlp:tache %s" % fiche] + commun
        cmd += ["--allowedTools"] + AUTORISES + ["--disallowedTools"] + INTERDITS
        if a.model:
            cmd += ["--model", a.model]
        if a.effort:
            cmd += ["--effort", a.effort]
        if a.budget:
            cmd += ["--max-budget-usd", a.budget]
        return cmd
    r = ROLES[role]
    cmd += ["-p", r["prompt"].format(fiche=fiche) + suite] + commun
    if r["agent"]:
        cmd += ["--agent", r["agent"]]
    if r["git"]:
        if role != "jouer":     # NUI5 : la boucle commite, après la relecture ; `jouer` n'a ni `git add` ni `git commit`
            cmd += ["--allowedTools"] + AUTORISES
        cmd += ["--disallowedTools"] + INTERDITS
    else:
        cmd += ["--disallowedTools"] + NON_GIT
    cmd += ["--model", modele]
    if r["repli"] and modele == r["modele"]:
        cmd += ["--fallback-model", r["repli"]]
    if r["effort"]:
        cmd += ["--effort", r["effort"]]
    return cmd + ["--max-turns", str(max_tours(role)), "--max-budget-usd", str(r["usd"]),
                  "--session-id", session, "--permission-prompts", "none"]


def lire_trace(trace):
    """Ce que dit la trace : `result`, modèles vus, un message `assistant`, id de session."""
    s: dict[str, Any] = {"result": None, "modeles": [], "assistant": False, "session": None}

    def voir(m):
        if isinstance(m, str) and m not in s["modeles"]:
            s["modeles"].append(m)

    with open(trace, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            try:
                d = json.loads(ligne)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") == "system" and d.get("subtype") == "init" and s["session"] is None:
                s["session"] = d.get("session_id")
            elif d.get("type") == "assistant":
                s["assistant"] = True
                message = d.get("message")
                voir(message.get("model") if isinstance(message, dict) else None)
            elif d.get("type") == "result":
                s["result"] = d
                usage = d.get("modelUsage")
                for m in usage if isinstance(usage, dict) else ():
                    voir(m)
    return s


def classer(s, ok):
    """L'issue d'une session, dans cet ordre : timeout, coupure, plafond, limite, pas partie, ratée, jouée."""
    r = s["result"]
    if s["timeout"]:
        return "timeout"
    if r is None:
        return "coupure"
    if str(r.get("subtype") or "").startswith("error_max_"):
        return "plafond"
    if LIMITE_RE.match(str(r.get("result") or "")):
        return "limite"
    if r.get("is_error") or not s["assistant"]:
        return "pas partie"
    return "jouée" if ok else "ratée"


def jouer(claude, fiche, racine, a, trace, role="jouer", controle=None, suite="", apres=None, session=None):
    """Joue une session neuve du rôle `role` (sans `--nuit` : toujours le rôle jouer).

    `controle()` dit si le contrôle du rôle passe (jouer : la case est cochée) ; sans, il passe.
    `session` : l'id de son `--session-id`, quand l'appelant l'a déjà écrit (clore) — la première session seule,
    une relance après la limite Opus en prend un neuf.
    `suite` s'ajoute au prompt. `apres(texte, issue, session)` : une fois par session venue au bout — ni
    limite ni pas partie —, avant sa ligne du carnet ; il rend les clés de plus de cette ligne (`refus_n`,
    `cause`, `garde`). Rend un dict : `tours` et `cout` (cumulés si une limite Opus relance), `texte`,
    `issue`, `ok` (rendu de `controle`), `stop` (la raison écrite au carnet, ou None), `session` (celle
    de la dernière), `coupee` (sous `--nuit`, session sans ligne `result` : `apres` n'est pas appelé, la ligne du
    carnet porte `usd_kit` et `tours_kit`). Sous `--nuit`, une note `depart` avant chaque session, une ligne du carnet après.
    """
    env = {k: v for k, v in os.environ.items() if k not in HERITEES}
    if a.nuit:
        env[carnet.ENV_CARNET], env[carnet.ENV_CANAL], env["VLP_NUIT"] = a.carnet, a.canal, "1"
    tours, cout, rejoue = 0, 0.0, False
    while True:
        modele = modele_de(role) if a.nuit else a.model
        demande = session if session and not rejoue else str(uuid.uuid4())
        cmd = commande(claude, role, fiche, a, modele, demande, suite)
        delai = ROLES[role]["timeout"] if a.nuit else None
        if a.nuit:   # avant la session, jamais pendant : sans ligne de session au même id, elle a été coupée (NUI8)
            ligne_carnet(a, fiche=fiche, note="depart %s" % role, session=demande)
        fini, t0 = True, time.time()
        with open(trace, "w", encoding="utf-8") as f:
            try:
                subprocess.run(cmd, cwd=racine, env=env, stdin=subprocess.DEVNULL, stdout=f,
                               stderr=subprocess.STDOUT, timeout=delai)
            except subprocess.TimeoutExpired:
                fini = False
        s = lire_trace(trace)
        s["timeout"] = not fini
        r = s["result"] or {}
        texte = str(r.get("result") or "") if s["result"] else "(aucune ligne result dans la trace)"
        ok = controle() if controle else True
        issue = classer(s, ok)
        tours, cout = tours + (r.get("num_turns") or 0), cout + (r.get("total_cost_usd") or 0.0)
        duree = int(time.time() - t0)
        coupee = a.nuit and issue in COUPEES   # sans ligne `result` : son travail n'est pas à croire (NUI8)
        if a.nuit:
            refus = len(r.get("permission_denials") or [])
            usd_kit, tours_kit, garde_kit = mesure_kit(demande) if coupee else (None, None, None)
            plus = apres(texte, issue, s["session"] or demande) \
                if apres and issue not in ("limite", "pas partie") + COUPEES else {}
            gardes = ["permission_denials : %d" % refus if refus else None, plus.get("garde"), garde_kit]
            ligne_carnet(a, role=role, fiche=fiche, modele_demande=modele, modeles_vus=s["modeles"],
                         tours_cli=r.get("num_turns") if s["result"] else None,
                         usd_cli=r.get("total_cost_usd") if s["result"] else None,
                         usd_kit=usd_kit, tours_kit=tours_kit,
                         duree_s=duree, issue=issue, garde=" ; ".join(g for g in gardes if g) or None,
                         session=s["session"] or demande, **{k: v for k, v in plus.items() if k != "garde"})
        stop = None
        if a.nuit and issue == "limite":
            m = LIMITE_RE.match(texte)
            genre = m.group(1).lower() if m else ""
            if genre == "opus" and not rejoue and ROLES[role]["modele"] == OPUS:
                BASCULE["jusqu"] = reset_de(texte)
                quand = "la fin de la nuit" if BASCULE["jusqu"] == FIN else time.strftime("%H:%M", time.localtime(BASCULE["jusqu"]))
                carnet.noter(a.carnet, a.canal, "bascule Opus → %s jusqu'à %s : %s" % (SONNET, quand, texte))
                rejoue, trace = True, os.path.splitext(trace)[0] + "-2.jsonl"
                continue
            stop = "limite %s — %s" % (genre, texte)
        elif a.nuit and issue == "pas partie":
            stop = "session pas partie — %s" % texte.split("\n")[0]
        if stop:
            carnet.stop(a.carnet, a.canal, stop)
        return {"tours": tours, "cout": cout, "texte": texte, "issue": issue, "ok": ok, "stop": stop,
                "session": s["session"] or demande, "coupee": coupee}


def etat_case(fichier, fiche, racine):
    """(case cochée, sha de la `TÊTE` ou None) selon `cocher --verifier`."""
    _, verif = vlp(["cocher", fichier, fiche, "--verifier"], racine)
    m = re.search(r"^TÊTE (\S+)", verif, re.M)
    return ("CASE %s [x]" % fiche) in verif, m.group(1) if m else None


def case_cochee(fichier, fiche, racine):
    """Vrai si `cocher --verifier` voit la case de `fiche` cochée."""
    return etat_case(fichier, fiche, racine)[0]


def verdict_de(texte):
    """(verdict, cause) lus dans le `result` de la relecture : le premier mot s'il est dans `VERDICTS`
    (sinon `None` : aucun verdict vaut `REFUSÉE`, `enchainement.md`), et le mot entre `<verdict> — ` et
    ` :` — `aucun-verdict` quand il n'y en a pas de lisible."""
    t = texte.lstrip()
    m = re.match(r"\w+", t)
    mot = m.group(0) if m and m.group(0) in kit().VERDICTS else None
    if mot is None:
        return None, "aucun-verdict"
    c = re.match(re.escape(mot) + r"\s*—\s*(\w+)\s*:", t)
    return mot, c.group(1) if c else "aucun-verdict"


def commiter(racine, sujet, fichier=None):
    """(ok, erreur) : `git add -A` puis `git commit -m <sujet>` ; avec `fichier`, ce fichier seul."""
    git = kit().git_texte
    code, err = git(["add", "--", fichier] if fichier else ["add", "-A"], racine)
    if code == 0:
        code, err = git(["commit", "-q", "-m", sujet] + (["--", fichier] if fichier else []), racine)
    return code == 0, err


def relire(claude, fiche, titre, fichier, racine, a, trace, tete=None):
    """La relecture d'une fiche cochée, sous `--nuit` (chantier NUI) : la session du rôle `relire`, puis
    ce que son verdict commande. `tete` : le sha d'un commit que le jeu a fait lui-même (`--sha HEAD`).
    ACCEPTÉE : la ligne `**Session**` du relecteur, puis le commit (de la fiche ; de cette ligne seule si
    `tete`). REFUSÉE : `git revert` d'abord si `tete`, puis `cocher --refuser` et la ligne `**Session**` ;
    l'arbre reste tel quel. Rend `tours`, `cout`, `stop`, `arret` (la raison d'un arrêt — commit ou revert
    impossible —, ou None), `verdict`, et pour un refus `refuse`, `motif`, `refus_n` (celui de `cocher`),
    `cause`, `reecriture`, `erreur_avant` : ce que `relire_et_relancer` en fait (NUI6)."""
    accepte = kit().VERDICTS[0]
    out: dict[str, Any] = {"verdict": None, "arret": None, "refus_n": None, "cause": None, "erreur_avant": None,
                           "refuse": False, "motif": None, "reecriture": None, "coupee": False}

    def suite(texte, issue, session):
        mot, cause = verdict_de(texte)
        out["verdict"], plus = mot, {}
        gardes = ["TÊTE %s : la session de jeu a commité" % tete] if tete else []
        noter = ["cocher", fichier, fiche, "--session", session, "--role", "relire"]
        if mot == accepte:
            code, sortie = vlp(noter, racine)
            if code:
                gardes.append("cocher --session : %s" % sortie.strip())
            ok, err = commiter(racine, "%s : session de relecture" % fiche if tete else "%s : %s" % (fiche, titre),
                               fichier if tete else None)
            if not ok:
                out["arret"] = "%s : commit refusé — %s" % (fiche, err)
                gardes.append(out["arret"])
        else:
            _, ex = vlp(["extraire", fichier, fiche], racine)
            out["erreur_avant"] = next((l for l in ex.splitlines() if l.startswith("Erreur :")), None)
            motif = (texte.strip().splitlines() or [""])[0] or "aucun verdict rendu par le relecteur"
            revert = git_revert(racine) if tete else None
            if revert:
                out["arret"] = "%s : revert impossible — %s" % (fiche, revert)
                gardes.append(out["arret"])
            else:
                _, sortie = vlp(["cocher", fichier, fiche, "--refuser", motif], racine)
                vu = re.search(r"refus (\d+)", sortie)
                ree = next((l.strip() for l in texte.splitlines() if l.strip().startswith("RÉÉCRITURE :")), None)
                out.update(refus_n=int(vu.group(1)) if vu else None, cause=cause, refuse=True, motif=motif,
                           reecriture=ree)
                vlp(noter, racine)
                plus.update(refus_n=out["refus_n"], cause=cause, reecriture=ree)
        if gardes:
            plus["garde"] = " ; ".join(gardes)
        return plus

    s = jouer(claude, fiche, racine, a, trace, role="relire", suite=" --sha HEAD" if tete else "", apres=suite)
    out.update(tours=s["tours"], cout=s["cout"], stop=s["stop"], texte=s["texte"], coupee=s["coupee"])
    return out


def git_revert(racine):
    """None si `git revert --no-edit HEAD` passe, sinon sa première ligne d'erreur."""
    code, err = kit().git_texte(["revert", "--no-edit", "HEAD"], racine)
    return None if code == 0 else err


def tentatives(extrait):
    """Le bloc **Tentatives** de la fiche dans `extrait` : `None` sans bloc, sinon `(refus_seuls, n, motif)` —
    `refus_seuls` si toutes ses lignes numérotées valent `ESSAI_REFUSE` (au moins une), `n` leur nombre,
    `motif` la ligne `Erreur :` du bloc (sans son préfixe) ou None."""
    lignes = extrait.splitlines()
    debut = next((i for i, l in enumerate(lignes) if l.startswith("**Tentatives**")), None)
    if debut is None:
        return None
    bloc = []
    for l in lignes[debut + 1:]:
        if not l.strip() or l.startswith("**"):
            break
        bloc.append(l)
    essais = [l.split(". ", 1)[1].strip() for l in bloc if re.match(r"[0-9]+\. ", l)]
    motif = next((l[len("Erreur :"):].strip() for l in bloc if l.startswith("Erreur :")), None)
    return bool(essais) and all(e == kit().ESSAI_REFUSE for e in essais), len(essais), motif


def garde_de(n, dernier, motif, cause):
    """La garde qui arrête la fiche au refus n° `n` (motif `motif`, cause `cause`, `dernier` : le motif
    d'avant), ou None : la cause est `copie`, la relance joue. Dans cet ordre : `meme-erreur`, `refus-max`,
    puis la cause — `copie` relance, `fiche` arrête (`cause-fiche`), toute autre arrête (`sans-cause`)."""
    if motif == dernier:
        return "meme-erreur"
    if n >= REFUS_MAX:
        return "refus-max"
    if cause == "copie":
        return None
    return "cause-fiche" if cause == "fiche" else "sans-cause"


def noter_arret(a, fiche, garde, n=None, cause=None, reecriture=None):
    """La ligne du carnet d'un arrêt de la nuit : la garde, et pour un refus son n, sa cause, sa réécriture.
    Sans `role` : le carnet ne la compte pas comme une session."""
    ligne_carnet(a, fiche=fiche, garde=garde, refus_n=n, cause=cause, reecriture=reecriture)


def verification_de(racine):
    """La commande du libellé `- **vérification de nuit** : <commande>` de CHANTIER.md, ou None."""
    try:
        return kit().champ(kit().lignes_de(os.path.join(racine, "CHANTIER.md")), "vérification de nuit")
    except OSError:
        return None


def verifier_nuit(commande, racine):
    """None si la vérification de nuit passe (code 0), sinon la raison, lue par le shell dans `racine`
    et bornée par `TIMEOUT_S`."""
    try:
        r = subprocess.run(commande, cwd=racine, shell=True, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "dépasse le délai de %d s" % TIMEOUT_S
    if r.returncode:
        return "sort %d" % r.returncode
    return None


def hors_role(a, racine, fiche):
    """Vrai — et une ligne `cloture-hors-role` au carnet — si la session de `fiche` a fermé le chantier : la carte
    ne donne plus de fichier de fiches courant. Sous `--nuit`, `clore` seul clôt (NUI7)."""
    _, fichier, _, a.plugin_retard = lire_carte(racine)
    if fichier is not None:
        return False
    ligne_carnet(a, fiche=fiche, garde="cloture-hors-role")
    return True


def relire_et_relancer(claude, fiche, titre, fichier, racine, a, traces, n_refus, dernier, tot, canal=False):
    """Relit la fiche jouée, puis suit le verdict (NUI5, NUI6) : ACCEPTÉE rend None. REFUSÉE : `n_refus` (celui
    de la boucle, `dernier` : le motif d'avant) augmente, `garde_de` tranche ; arrêt → une ligne du carnet et
    `(1, raison, genre)` ; sinon (cause `copie`) une session du rôle `relance` sur l'arbre tel quel, puis une
    relecture de plus. `tot` : `[tours, coût]` du lancement, tenus à jour. `canal` : la boucle d'un canal (NUI7),
    où une relance qui clôt le chantier l'arrête (`hors_role`). Rend None ou `(code, raison, genre)` : `genre`
    vaut `stop` (le canal s'arrête), `canal` (commit ou revert impossible : le canal s'arrête) ou `chantier`."""
    k = 1
    r = relire(claude, fiche, titre, fichier, racine, a, os.path.join(traces, "%s-relire.jsonl" % fiche),
               etat_case(fichier, fiche, racine)[1])
    while True:
        tot[0], tot[1] = tot[0] + r["tours"], tot[1] + r["cout"]
        print("RELIT %s · %s · tours %d · %.4f $" % (fiche, r["verdict"] or "aucun verdict", r["tours"], r["cout"]))
        for ligne in r["texte"].strip().split("\n"):
            print("    " + ligne)
        print(flush=True)
        if r["stop"]:
            return 1, "STOP — %s" % r["stop"], "stop"
        if r["arret"]:
            return 1, r["arret"], "canal"
        if r["coupee"]:   # NUI8 : pas de verdict, et le travail de la fiche n'est pas à croire
            return 1, "%s : la relecture a été coupée — son travail n'est pas cru" % fiche, "chantier"
        if not r["refuse"]:
            return None
        n_refus += 1
        cause = r["cause"] if r["cause"] in ("fiche", "copie") else "aucune"
        garde = garde_de(n_refus, dernier, r["motif"], cause)
        dernier = r["motif"]
        if garde:
            noter_arret(a, fiche, garde, n_refus, cause, r["reecriture"])
            return 1, "%s refusée à la relecture — refus %d, cause %s — garde %s" % (fiche, n_refus, cause, garde), "chantier"
        k += 1
        trace = os.path.join(traces, "%s-relance%d.jsonl" % (fiche, k - 1))
        print("RELANCE %s — refus %d, cause %s — trace %s" % (fiche, n_refus, cause, trace), flush=True)
        t0 = time.time()
        s = jouer(claude, fiche, racine, a, trace, role="relance",
                  controle=functools.partial(case_cochee, fichier, fiche, racine),
                  apres=lambda texte, issue, session: {"refus_n": n_refus, "cause": cause})
        tot[0], tot[1] = tot[0] + s["tours"], tot[1] + s["cout"]
        print("FICHE %s · CASE [%s] · tours %d · %.4f $ · %d s (relance)"
              % (fiche, "x" if s["ok"] else " ", s["tours"], s["cout"], int(time.time() - t0)))
        for ligne in s["texte"].strip().split("\n"):
            print("    " + ligne)
        print(flush=True)
        if s["stop"]:
            return 1, "STOP — %s" % s["stop"], "stop"
        if s["coupee"]:
            return 1, "%s : la relance a été coupée — son travail n'est pas cru" % fiche, "chantier"
        if canal and hors_role(a, racine, fiche):
            return 1, "%s : la relance a clos le chantier — clôture hors rôle" % fiche, "chantier"
        if not s["ok"]:
            return 1, "%s non cochée après la relance — lire sa trace" % fiche, "chantier"
        r = relire(claude, fiche, titre, fichier, racine, a, os.path.join(traces, "%s-relire%d.jsonl" % (fiche, k)),
                   etat_case(fichier, fiche, racine)[1])


def fiches_du_chantier(claude, a, racine, fichier, traces, verif, etat, canal=False):
    """Joue les fiches du chantier ouvert, une session `claude -p` neuve chacune : la boucle de `main` d'avant
    NUI7, qu'une boucle de canal reprend pour chaque chantier. `etat` : `jouees`, `tours`, `cout`, `verifiee`,
    tenus à jour. Rend `(code, raison, genre)` : `fini` (plus de fiche à jouer), `borne` et `plafond` (le canal
    s'arrête, chantier ouvert), `stop` (idem, sortie 1), `canal` (commit ou revert impossible : le canal s'arrête)
    ou `chantier` (le chantier s'arrête, le canal non). `canal` : la boucle d'un canal, où une session de jeu qui
    clôt le chantier l'arrête (`hors_role`)."""
    while a.plafond is None or etat["jouees"] < a.plafond:
        if a.nuit:
            lignes = carnet.lire(a.carnet)
            arret = carnet.stop_de(lignes)
            if arret is not None:
                return 1, "STOP — %s" % arret, "stop"
            arret = carnet.borne(lignes, a.chantier, a.borne_usd, a.borne_chantiers, plafonds())
            if arret is not None:
                return 0, "borne atteinte — %s" % arret, "borne"
        _, _, fiche, a.plugin_retard = lire_carte(racine)
        if not fiche or fiche == "aucune":
            return 0, "aucune fiche à jouer", "fini"
        _, extrait = vlp(["extraire", fichier, fiche], racine)
        bloc = tentatives(extrait) if a.nuit else None
        if "**Tentatives**" in extrait and not (bloc and bloc[0]):   # sous --nuit, des refus seuls ne l'arrêtent pas
            return 1, "%s porte un bloc Tentatives — à lire avant de rejouer" % fiche, "chantier"
        n_refus, dernier = (bloc[1], bloc[2]) if bloc else (0, None)
        if a.nuit and verif and not etat["verifiee"]:
            etat["verifiee"], echec = True, verifier_nuit(verif, racine)
            print("VERIF avant %s · %s" % (fiche, echec or "sort 0"), flush=True)
            if echec:
                noter_arret(a, fiche, "verification")
                return 1, "%s : garde verification — la vérification de nuit %s avant la fiche" % (fiche, echec), "chantier"
        visuel = "ARRÊT:" in extrait
        trace = os.path.join(traces, "%s.jsonl" % fiche)
        print("JOUE %s — trace %s" % (fiche, trace), flush=True)
        t0 = time.time()
        s = jouer(claude, fiche, racine, a, trace, controle=functools.partial(case_cochee, fichier, fiche, racine))
        duree = int(time.time() - t0)
        cochee = s["ok"]
        etat["jouees"] += 1
        etat["tours"] += s["tours"]
        etat["cout"] += s["cout"]
        print("FICHE %s · CASE [%s] · tours %d · %.4f $ · %d s"
              % (fiche, "x" if cochee else " ", s["tours"], s["cout"], duree))
        for ligne in s["texte"].strip().split("\n"):
            print("    " + ligne)
        print(flush=True)
        if s["stop"]:
            return 1, "STOP — %s" % s["stop"], "stop"
        if s["coupee"]:   # NUI8 : la case a pu être cochée avant la coupure — le travail n'est pas cru pour autant
            return 1, "%s : session de jeu coupée (%s) — son travail n'est pas cru" % (fiche, s["issue"]), "chantier"
        if canal and hors_role(a, racine, fiche):
            return 1, "%s a clos le chantier — clôture hors rôle" % fiche, "chantier"
        if visuel:
            return 0, "%s est (visuel) — à regarder" % fiche, "chantier"
        if not cochee:
            return 1, "%s non cochée — lire sa trace" % fiche, "chantier"
        if a.nuit:
            titre = re.search(r"^## %s \[[ x]\] — (.+?)\s*$" % re.escape(fiche), extrait, re.M)
            tot = [etat["tours"], etat["cout"]]
            fin = relire_et_relancer(claude, fiche, titre.group(1) if titre else fiche, fichier, racine, a,
                                     traces, n_refus, dernier, tot, canal)
            etat["tours"], etat["cout"] = tot
            if fin:
                return fin
            if verif:
                echec = verifier_nuit(verif, racine)
                print("VERIF après %s · %s" % (fiche, echec or "sort 0"), flush=True)
                if echec:
                    noter_arret(a, fiche, "verification")
                    return 1, "%s : garde verification — la vérification de nuit %s après son commit" % (fiche, echec), "chantier"
    return 0, "plafond de %d fiches" % a.plafond, "plafond"


def lire_plan(racine, a):
    """`(plan, erreur)` : `plan` = `(borne en $, borne en chantiers, codes du canal dans l'ordre de leur rang)`, lu
    par `vlp.py plan lire --date --canal` (sans canal : tous, pour le lanceur) — jamais à la main. `erreur` : la 1re ligne
    de sa sortie."""
    code, s = vlp(["plan", "lire", racine, "--date", a.date] + (["--canal", a.canal] if a.canal else []), racine)
    borne = re.search(r"^BORNE (\S+) \$ · (\d+) chantiers$", s, re.M)
    liste = sorted((int(m.group(2)), m.group(1)) for l in s.splitlines()
                   for m in [re.match(r"CHANTIER (\S+) · canal \S+ · rang (\d+) · préfixe \S+$", l)] if m)
    if code or not borne or not liste:
        return None, (s.strip().splitlines() or ["plan illisible"])[0]
    return (float(borne.group(1)), int(borne.group(2)), [c for _, c in liste]), None


def lire_todo(racine):
    """`(todo, erreur)` : `todo` = `(rangs, codes, lettres closes)` — la TODO du fichier d'état (`todo_du_fichier`),
    le code de chaque rang (`codes_todo`) et les lettres de « Lettres de fiche déjà prises » —, lue une fois au départ
    du canal ; None sans fichier d'état lisible, et `valider` seul juge alors. `erreur` : le `ValueError` d'une ligne
    mal formée (une barre verticale dans une cellule, PIP) : tout chantier se met de côté."""
    k = kit()
    try:
        carte = k.lignes_de(os.path.join(racine, "CHANTIER.md"))
        etat = k.champ(carte, "fichier d'état")
        rangs = k.todo_du_fichier(k.lignes_du_projet(racine, etat, "fichier d'état")) if etat else None
    except (k.Absent, OSError):
        return None, None
    except ValueError as e:
        return None, str(e)
    if rangs is None:
        return None, None
    return (rangs, k.codes_todo(rangs), set(k.lettres_prises(carte))), None


def bloquant(code, todo, plan, de_cote):
    """Le code mis de côté ou sauté dont `code` dépend (cellule « Dépend de » de sa ligne TODO), ou None : le motif
    de `est_bloque` — les lettres closes, plus celles du plan, moins celles des chantiers de côté ; un numéro de
    rang d'un chantier de côté bloque aussi. Sans TODO, sans ligne pour `code`, ou rien de côté : None."""
    if not todo or not de_cote or code not in todo[1]:
        return None
    k = kit()
    rangs, codes, closes = todo
    depend = rangs[codes.index(code)][4]
    ok = (closes | {k.lettre_de(c) for c in plan}) - {k.lettre_de(c) for c in de_cote}
    if not k.est_bloque(depend, ok, {rangs[codes.index(c)][0] for c in de_cote if c in codes}):
        return None
    dep_codes, dep_rangs = k.dependances(depend)
    return (next((c for c in dep_codes if k.lettre_de(c) not in ok), None)
            or next((c for c in de_cote if c in codes and rangs[codes.index(c)][0] in dep_rangs), None) or "?")


def tete_de(racine):
    """Le sha de `HEAD` dans `racine`, ou None."""
    code, sha = kit().git_texte(["rev-parse", "HEAD"], racine)
    return sha.strip() if code == 0 else None


def arbre_propre(racine):
    """Vrai si `git status --porcelain` ne rend rien ; None si Git ne répond pas."""
    code, s = kit().git_texte(["status", "--porcelain"], racine)
    return None if code != 0 else not s.strip()


def brancher(racine, branche, base):
    """None si `git switch -c <branche> <base>` passe, sinon sa première ligne d'erreur."""
    code, err = kit().git_texte(["switch", "-q", "-c", branche, base], racine)
    return None if code == 0 else err


def mettre_de_cote(racine, a, code, raison):
    """Met le chantier `code` de côté — seul endroit où la boucle le fait : une ligne `mis-de-cote:<raison>` au
    carnet ; arbre propre, rien de plus ; sinon `git add -A` et le commit WIP (`WIP_SUJET` de vlp.py), hors
    `COMMIT_FICHE`. Rend None, ou la raison d'arrêt du canal : commit refusé par un hook (ligne `wip-refuse`, arbre tel
    quel — jamais `--no-verify`) ou Git muet."""
    raison = " ".join(raison.split())[:200]
    ligne_carnet(a, garde="mis-de-cote:%s" % raison)
    propre = arbre_propre(racine)
    if propre is None:
        return "%s : git status impossible" % code
    if propre:
        return None
    ok, err = commiter(racine, kit().WIP_SUJET % (code, raison))
    if ok:
        return None
    ligne_carnet(a, garde="wip-refuse")
    return "%s : commit WIP refusé — %s" % (code, err)


def juger_decoupe(racine, fichier, code, todo):
    """`(raison, n)` : `raison` — None si le découpage passe — dit pourquoi le chantier se met de côté : `vlp.py valider`
    rend un écart ou un avertissement, ou plus de fiches que 2 × la borne haute du coût de sa ligne TODO (sans
    nombre, ou sans ligne : `valider` seul juge). `n` : le nombre de fiches lu par `valider`."""
    _, s = vlp(["valider", fichier], racine)
    lignes = s.strip().splitlines() or [""]
    m = re.match(r"(?:VALIDE|INVALIDE) (\d+) fiches · socle \d+ lignes · (\d+) écarts · (\d+) avertissements", lignes[-1])
    if not m:
        return "vlp.py valider illisible : %s" % lignes[-1], 0
    n, ecarts, avert = (int(g) for g in m.groups())
    if ecarts or avert:
        return "vlp.py valider : %d écarts, %d avertissements — %s" % (ecarts, avert, lignes[0]), n
    if todo and code in todo[1]:
        cout = todo[0][todo[1].index(code)][3]
        borne = kit().borne_haute_cout(cout)
        if borne is not None and n > 2 * borne:
            return "%d fiches : plus de 2 × %g, la borne haute du coût « %s » de la TODO" % (n, borne, cout), n
    return None, n


def session_de(claude, a, racine, traces, etat, role, code, fiche, controle, session=None):
    """Une session d'un rôle hors fiche (découper, clore) : sa trace, ses lignes imprimées, les compteurs de `etat`."""
    trace = os.path.join(traces, "%s-%s.jsonl" % (code, role))
    print("%s %s — trace %s" % (role.upper(), code, trace), flush=True)
    t0 = time.time()
    s = jouer(claude, fiche, racine, a, trace, role=role, controle=controle, session=session)
    etat["tours"] += s["tours"]
    etat["cout"] += s["cout"]
    print("%s %s · tours %d · %.4f $ · %d s" % (role.upper(), code, s["tours"], s["cout"], int(time.time() - t0)))
    for ligne in s["texte"].strip().split("\n"):
        print("    " + ligne)
    print(flush=True)
    return s


def decouper_chantier(claude, a, racine, traces, etat, code, todo):
    """Le découpage du chantier `code` : la session `découper`, `juger_decoupe`, le commit d'ouverture. Rend
    `(fichier, None)`, ou `(None, (genre, sortie, raison))` — le `un_chantier` qui s'arrête là. « Découpé » : `COURANT=`
    nomme un fichier, donc ajouté par la branche — `courant_de` écarte le chantier hérité de main (NUI25)."""
    s = session_de(claude, a, racine, traces, etat, "découper", code, code, lambda: carte_dit(racine, True))
    if s["stop"]:
        return None, ("fin", 1, "STOP — %s" % s["stop"])
    if s["coupee"]:   # NUI8 : ce qu'elle a écrit n'est pas à croire
        return None, ("de-cote", 0, "le découpage a été coupé (%s) — son travail n'est pas cru" % s["issue"])
    _, fichier, _, a.plugin_retard = lire_carte(racine)
    if fichier is None:
        return None, ("de-cote", 0, "le découpage n'a ouvert aucun chantier")
    raison, n = juger_decoupe(racine, fichier, code, todo)
    if raison:
        return None, ("de-cote", 0, raison)
    ok, err = commiter(racine, "Chantier %s ouvert (nuit) : %d fiches" % (code, n))
    if not ok:
        ligne_carnet(a, garde="commit-refuse")
        return None, ("fin", 1, "%s : commit du découpage refusé — %s" % (code, err))
    print("OUVERT %s : %d fiches — %s" % (code, n, fichier), flush=True)
    return fichier, None


def un_chantier(claude, a, racine, traces, etat, code, todo, erreur_todo, reprise=False):
    """Un chantier du plan, du découpage à la clôture. Rend `(genre, sortie, raison)` : `clos` ; `de-cote` (`raison` :
    pourquoi — le canal appelle `mettre_de_cote`) ; `fin` (le canal s'arrête, `sortie` est son code). `reprise` : le
    chantier est repris après une coupure (NUI8) — s'il est déjà découpé (un fichier de fiches courant), il ne repasse
    pas par `découper`. Une carte gardée en route le met de côté (NUI25) : ni découpé, ni clos."""
    try:
        return chantier_du_canal(claude, a, racine, traces, etat, code, todo, erreur_todo, reprise)
    except CarteGardee as e:
        return "de-cote", 0, "carte gardée — %s" % e


def chantier_du_canal(claude, a, racine, traces, etat, code, todo, erreur_todo, reprise):
    """Le corps d'`un_chantier`, qui garde ses `CarteGardee`. « Clos » : `COURANT=` ne nomme plus aucun fichier —
    le chantier hérité de main n'y est jamais (`courant_de`, NUI25)."""
    if erreur_todo:
        return "de-cote", 0, "TODO illisible — %s" % erreur_todo
    fichier = lire_carte(racine)[1] if reprise else None
    if fichier is None:
        fichier, fin = decouper_chantier(claude, a, racine, traces, etat, code, todo)
        if fin:
            return fin
    assert fichier
    etat["verifiee"] = False
    sortie, raison, genre = fiches_du_chantier(claude, a, racine, fichier, traces, verification_de(racine), etat, canal=True)
    if genre == "chantier":
        print("ARRÊT %s" % raison, flush=True)
        return "de-cote", 0, raison
    if genre != "fini":
        return "fin", sortie, raison
    titres = [m.group(1) for l in kit().lignes_de(os.path.join(racine, fichier))
              for m in [re.match(r"## ([A-Z]{1,3}[0-9]+) \[", l)] if m]
    if not titres:
        return "de-cote", 0, "aucune fiche à nommer pour la ligne Session de la clôture"
    session = str(uuid.uuid4())
    # La ligne `**Session** … (clore)` entre au commit de la clôture : elle s'écrit avant la session.
    noter, ecrit = vlp(["cocher", fichier, titres[-1], "--session", session, "--role", "clore"], racine)
    if noter:
        return "de-cote", 0, "cocher --session --role clore : %s" % ecrit.strip()
    s = session_de(claude, a, racine, traces, etat, "clore", code, None, lambda: carte_dit(racine, False), session)
    if s["stop"]:
        return "fin", 1, "STOP — %s" % s["stop"]
    if s["coupee"]:   # NUI8
        return "de-cote", 0, "la clôture a été coupée (%s) — son travail n'est pas cru" % s["issue"]
    _, ouvert, _, a.plugin_retard = lire_carte(racine)
    if ouvert is not None:
        return "de-cote", 0, "la clôture n'a pas fermé le chantier — fichier de fiches courant : %s" % ouvert
    if not arbre_propre(racine):
        return "de-cote", 0, "arbre non propre après la clôture"
    return "clos", 0, None


def lire_reprise(a, racine, codes):
    """`(reprise, erreur)` de `--reprendre` (NUI8), lu dans le carnet du canal. D'abord, seule écriture : chaque `depart`
    sans ligne de session au même id reçoit sa ligne `coupure` (coût de `mesure_kit`). Puis, dans l'ordre du plan, le
    sort de chaque chantier qui a des lignes : `saute` et `de-cote` (garde `saute:…`, `mis-de-cote:…`), `clos` (une
    session `clore` jouée), sinon `en_cours` — le dernier seulement : un autre est de côté. `reprise` : `faits`
    (`{code: genre}`), `en_cours` (le code, ou None), `coupe` (il a une session coupée), `coupees` (le nombre de lignes
    écrites) et `base` — la pointe de la branche du dernier chantier clos, sinon la note `base <sha>` du départ du canal.
    `erreur` : la base ou la branche manque."""
    def du_canal():
        return [d for d in carnet.lire(a.carnet) if d.get("canal") == a.canal]

    lignes = du_canal()
    fins = {d.get("session") for d in lignes if carnet.est_session(d)}
    coupees = 0
    for d in lignes:
        m = re.match(r"depart (\S+)$", str(d.get("note") or ""))
        if not m or not d.get("session") or d["session"] in fins:
            continue
        usd, tours, garde = mesure_kit(d["session"])
        carnet.ajouter(a.carnet, nuit=carnet.nuit_de(a.carnet), canal=a.canal, chantier=d.get("chantier"),
                       role=m.group(1), fiche=d.get("fiche"), issue="coupure", usd_kit=usd, tours_kit=tours,
                       garde=" ; ".join(g for g in ("reprise : session sans fin", garde) if g), session=d["session"])
        coupees += 1
    lignes = du_canal()

    def garde_dit(d, debut):
        return str(d.get("garde") or "").startswith(debut)

    faits, en_cours, coupe = {}, None, False
    vus = [c for c in codes if any(d.get("chantier") == c for d in lignes)]
    for c in vus:
        ls = [d for d in lignes if d.get("chantier") == c]
        if any(garde_dit(d, "saute:") for d in ls):
            faits[c] = "saute"
        elif any(garde_dit(d, "mis-de-cote:") for d in ls):
            faits[c] = "de-cote"
        elif any(d.get("role") == "clore" and d.get("issue") == "jouée" and carnet.est_session(d) for d in ls):
            faits[c] = "clos"
        elif c == vus[-1]:
            en_cours = c
            coupe = any(carnet.est_session(d) and d.get("issue") in COUPEES for d in ls)
        else:
            faits[c] = "de-cote"
    clos = [c for c in codes if faits.get(c) == "clos"]
    if clos:
        branche = "nuit/%s-%s-%s" % (a.date, a.canal, clos[-1])
        code, sha = kit().git_texte(["rev-parse", "--verify", "--quiet", "refs/heads/%s" % branche], racine)
        if code != 0 or not sha.strip():
            return None, "branche %s absente — la base du chantier suivant est introuvable" % branche
        base = sha.strip()
    else:
        bases = [str(d["note"]).split(" ", 1)[1] for d in lignes if str(d.get("note") or "").startswith("base ")]
        if not bases:
            return None, "aucune note « base <sha> » au carnet pour le canal %s — la base du plan est introuvable" % a.canal
        base = bases[-1]
    return {"faits": faits, "en_cours": en_cours, "coupe": coupe, "coupees": coupees, "base": base}, None


def boucle_canal(claude, a, racine, traces, etat, codes, todo, erreur_todo, reprise=None):
    """La boucle d'un canal : chaque chantier du plan, dans l'ordre. Rend `(code, raison)`. Avant chacun : `STOP`,
    borne et plafond (le canal s'arrête) ; un dépendant de ce qui est de côté est sauté, sans session ; sinon sa
    branche part du dernier chantier réussi (`HEAD` au départ, noté au carnet : `base <sha>`), puis `un_chantier`.
    `reprise` (`lire_reprise`, NUI8) : la base vient d'elle ; un chantier de ses `faits` n'est ni rejoué ni recompté
    à l'écran ; le chantier `en_cours` reprend dans sa branche (jamais recréée) — de côté si une session a été coupée
    ou si l'arbre est sale, sinon `un_chantier` sans `découper` s'il est déjà découpé."""
    if reprise:
        base = reprise["base"]
    else:
        base = tete_de(racine)
        if base is None:
            return 1, "HEAD illisible — Git ne répond pas dans %s" % racine
        carnet.noter(a.carnet, a.canal, "base %s" % base)
    de_cote, bilan = [], {"clos": 0, "de côté": 0, "sautés": 0}
    for code in codes:
        a.chantier = code
        fait = reprise["faits"].get(code) if reprise else None
        if fait:   # déjà traité avant la coupure : rien à rejouer, mais ses dépendants le savent
            if fait != "clos":
                de_cote.append(code)
            bilan["clos" if fait == "clos" else "sautés" if fait == "saute" else "de côté"] += 1
            continue
        lignes = carnet.lire(a.carnet)
        arret = carnet.stop_de(lignes)
        if arret is not None:
            return 1, "STOP — %s" % arret
        arret = carnet.borne(lignes, code, a.borne_usd, a.borne_chantiers, plafonds())
        if arret is not None:
            return 0, "borne atteinte — %s" % arret
        if a.plafond is not None and etat["jouees"] >= a.plafond:
            return 0, "plafond de %d fiches" % a.plafond
        reprend = bool(reprise) and code == reprise["en_cours"]
        cause = None if reprend else bloquant(code, todo, codes, de_cote)
        if cause:
            print("SAUTÉ %s — dépend de %s, mis de côté ou sauté" % (code, cause), flush=True)
            ligne_carnet(a, issue="pas partie", garde="saute:%s" % cause)
            de_cote.append(code)
            bilan["sautés"] += 1
            continue
        branche = "nuit/%s-%s-%s" % (a.date, a.canal, code)
        if reprend:   # la branche existe : on y revient, on ne la recrée jamais
            assert reprise
            code_git, err = kit().git_texte(["switch", "-q", branche], racine)
            if code_git != 0:
                return 1, "%s : retour à la branche %s impossible — %s" % (code, branche, err)
            propre = arbre_propre(racine)
            if propre is None:
                return 1, "%s : git status impossible" % code
            print("REPRISE %s — branche %s" % (code, branche), flush=True)
            if reprise["coupe"] or not propre:
                genre, sortie, raison = "de-cote", 0, ("une session a été coupée" if reprise["coupe"] else "arbre sale à la reprise")
            else:
                genre, sortie, raison = un_chantier(claude, a, racine, traces, etat, code, todo, erreur_todo, reprise=True)
        else:
            err = brancher(racine, branche, base)
            if err:
                return 1, "%s : branche %s impossible — %s" % (code, branche, err)
            print("CHANTIER %s — branche %s, depuis %s" % (code, branche, base[:9]), flush=True)
            genre, sortie, raison = un_chantier(claude, a, racine, traces, etat, code, todo, erreur_todo)
        if genre == "fin":
            return sortie, raison
        if genre == "clos":
            base = tete_de(racine)
            if base is None:
                return 1, "HEAD illisible — Git ne répond pas dans %s" % racine
            bilan["clos"] += 1
            print("CLOS %s — pointe %s" % (code, base[:9]), flush=True)
            continue
        print("MIS DE CÔTÉ %s — %s" % (code, raison), flush=True)
        arret = mettre_de_cote(racine, a, code, raison)
        de_cote.append(code)
        bilan["de côté"] += 1
        if arret:
            return 1, arret
    return 0, "plan terminé — %s" % ", ".join("%d %s" % (n, nom) for nom, n in bilan.items())


def cause_de_refus(racine, date):
    """La cause pour laquelle la nuit `date` ne se lance pas depuis `racine`, ou None (NUI9). Rien ne s'écrit : Git est
    lu (`branch`, `status`, `check-ignore`, `worktree list`), dans l'ordre — branche `main`, arbre propre (un plan non
    commité manquerait aux worktrees), fichier des nuits non ignoré (ignoré, il n'est dans aucun worktree), aucun
    worktree ni branche de cette nuit (une nuit lancée se reprend par `--reprendre`)."""
    k = kit()
    code, courante = k.git_texte(["branch", "--show-current"], racine)
    if code != 0:
        return "git branch impossible — %s" % courante
    if courante.strip() != "main":
        return "la branche courante est %s, pas main : les canaux partent de main" % (courante.strip() or "aucune (HEAD détachée)")
    propre = arbre_propre(racine)
    if propre is None:
        return "git status impossible"
    if not propre:
        return "l'arbre n'est pas propre (git status --porcelain) : un plan non commité manquerait aux worktrees"
    try:
        nuits = k.fichier_nuits(racine)
    except ValueError as e:
        return str(e)
    if nuits:
        code, err = k.git_texte(["check-ignore", "-q", nuits], racine)
        if code == 0:
            return ("le fichier des nuits (%s) est ignoré par Git : il n'est dans aucun worktree"
                    % os.path.relpath(nuits, racine).replace("\\", "/"))
        if code != 1:
            return "git check-ignore impossible — %s" % err
    code, liste = k.git_texte(["worktree", "list", "--porcelain"], racine)
    if code != 0:
        return "git worktree list impossible — %s" % liste
    deja = [l[len("worktree "):] for l in liste.splitlines()
            if l.startswith("worktree ") and l.replace("\\", "/").rsplit("/", 1)[-1].startswith("nuit-%s-" % date)]
    if deja:
        return "un worktree de nuit existe déjà (%s) — une nuit lancée se reprend par --reprendre" % deja[0]
    code, branches = k.git_texte(["branch", "--list", "nuit/%s-*" % date], racine)
    if code != 0:
        return "git branch --list impossible — %s" % branches
    if branches.strip():
        return ("une branche de cette nuit existe déjà (%s) — une nuit lancée se reprend par --reprendre"
                % branches.strip().splitlines()[0].lstrip("*+ "))
    return None


def exclure_worktrees(racine, date):
    """None, ou la raison de l'échec. `.claude/worktrees/` non ignoré (`check-ignore` sur le worktree du canal A) : sa
    ligne entre dans `info/exclude` du dépôt commun (`rev-parse --git-common-dir`) — jamais `.gitignore` ni un fichier
    suivi —, sans quoi le worktree d'un canal salirait le `git status` de `main`."""
    k = kit()
    code, err = k.git_texte(["check-ignore", "-q", ".claude/worktrees/nuit-%s-A" % date], racine)
    if code == 0:
        return None
    if code != 1:
        return "git check-ignore impossible — %s" % err
    code, commun = k.git_texte(["rev-parse", "--path-format=absolute", "--git-common-dir"], racine)
    if code != 0:
        return "git rev-parse impossible — %s" % commun
    exclure = os.path.join(commun.strip(), "info", "exclude")
    try:
        os.makedirs(os.path.dirname(exclure), exist_ok=True)
        existant = ""
        if os.path.isfile(exclure):
            with open(exclure, encoding="utf-8", errors="replace") as h:
                existant = h.read()
        with open(exclure, "a", encoding="utf-8", newline="") as h:
            h.write(("\n" if existant and not existant.endswith("\n") else "") + ".claude/worktrees/\n")
    except OSError as e:
        return "info/exclude non écrit — %s" % e
    return None


def ecrire_ligne(verrou, texte):
    """Une ligne à la fois sur la sortie commune : les fils des deux canaux n'entremêlent pas les leurs."""
    with verrou:
        print(texte, flush=True)


def suivre(canal, proc, verrou):
    """Le fil d'un canal (NUI9) : chaque ligne de sa fille, préfixée `[canal] `, puis `FIN <canal> · code <n>` dès qu'elle sort."""
    assert proc.stdout
    for ligne in proc.stdout:
        ecrire_ligne(verrou, "[%s] %s" % (canal, ligne.rstrip("\r\n")))
    ecrire_ligne(verrou, "FIN %s · code %d" % (canal, proc.wait()))


def lanceur(a):
    """`--nuit --lancer <projet>` (NUI9) : la ligne que l'utilisateur tape le soir. Dans l'ordre, sans rien créer avant la
    dernière garde : `claude` (une fois, passé aux deux canaux), `cause_de_refus`, le plan à la date (`vlp.py plan lire`,
    sa borne lue une fois), `exclure_worktrees` ; puis deux worktrees détachés sur `main` et deux `boucle.py --nuit --canal`
    en parallèle, un fil de lecture par fille. Sort 0 si les deux canaux sortent 0, 1 sinon (garde, Ctrl+C compris)."""
    claude = claude_de(a.claude)
    if not claude:
        return 1
    print("CLAUDE=%s" % claude)
    # Le projet seul : le chantier de main n'est pas celui des canaux, et une carte gardée n'empêche pas la nuit (NUI25).
    racine = kit().trouver(os.path.abspath(a.dossier))
    if not racine:
        print("GARDE: aucun projet équipé (CHANTIER.md) depuis %s" % os.path.abspath(a.dossier))
        return 1
    cause = cause_de_refus(racine, a.date)
    plan = None
    if cause is None:
        plan, erreur = lire_plan(racine, a)
        cause = None if plan else "pas de plan utilisable à la date %s — %s" % (a.date, erreur)
    a.carnet = a.carnet or carnet.du_jour(racine, a.date)
    if cause is None and not a.carnet:
        cause = "pas de dépôt Git pour le carnet de nuit"
    if cause is None:
        cause = exclure_worktrees(racine, a.date)
    if cause:
        print("GARDE: %s" % cause)
        return 1
    assert plan and a.carnet
    borne_usd = plan[0] if a.borne_usd is None else a.borne_usd
    borne_chantiers = plan[1] if a.borne_chantiers is None else a.borne_chantiers
    k = kit()
    worktrees = {}
    for canal in k.CANAUX:
        dossier = os.path.join(racine, ".claude", "worktrees", "nuit-%s-%s" % (a.date, canal))
        code, err = k.git_texte(["worktree", "add", "--detach", dossier, "main"], racine)
        if code != 0:
            print("GARDE: le worktree du canal %s n'a pas pu se créer — %s" % (canal, err))
            return 1
        worktrees[canal] = dossier
    traces_de = a.traces or os.path.dirname(a.carnet)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    verrou, procs, fils = threading.Lock(), {}, []
    for canal, dossier in worktrees.items():
        traces = os.path.join(traces_de, "traces-%s-%s" % (a.date, canal))
        os.makedirs(traces, exist_ok=True)
        cmd = [sys.executable, "-u", os.path.join(ICI, "boucle.py"), dossier, "--nuit", "--canal", canal, "--date", a.date,
               "--carnet", a.carnet, "--claude", claude, "--borne-usd", str(borne_usd),
               "--borne-chantiers", str(borne_chantiers), "--traces", traces, "--permission-mode", a.permission_mode]
        if a.plafond is not None:
            cmd += ["--plafond", str(a.plafond)]
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        procs[canal] = proc
        ecrire_ligne(verrou, "DÉPART %s · pid %d · %s" % (canal, proc.pid, dossier))
        fil = threading.Thread(target=suivre, args=(canal, proc, verrou), daemon=True)
        fil.start()
        fils.append(fil)
    try:
        while any(f.is_alive() for f in fils):
            time.sleep(0.2)
    except KeyboardInterrupt:
        for proc in procs.values():
            proc.terminate()
        ecrire_ligne(verrou, "ARRÊT Ctrl+C — terminate() aux deux canaux ; la reprise est --reprendre")
        return 1
    ecrire_ligne(verrou, "RIEN FUSIONNÉ, RIEN POUSSÉ — /vlp:chef le matin")
    codes = [proc.wait() for proc in procs.values()]
    return 0 if not any(codes) else 1


def main(argv):
    p = argparse.ArgumentParser(description="Une session claude -p neuve par fiche.")
    p.add_argument("dossier", nargs="?", default=".")
    p.add_argument("--plafond", type=int)
    p.add_argument("--claude")
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--permission-mode", default="auto")
    p.add_argument("--budget")
    p.add_argument("--traces")
    p.add_argument("--nuit", action="store_true")
    p.add_argument("--canal")
    p.add_argument("--chantier")
    p.add_argument("--date")
    p.add_argument("--borne-usd", type=float)
    p.add_argument("--borne-chantiers", type=int)
    p.add_argument("--carnet")
    p.add_argument("--reprendre", action="store_true")
    p.add_argument("--lancer", action="store_true")
    a = p.parse_args(argv)
    if a.nuit:
        if a.lancer:
            if a.canal or a.chantier or a.reprendre:
                p.error("--lancer ouvre les deux canaux lui-même : il refuse --canal, --chantier et --reprendre")
        elif not a.canal:
            p.error("--nuit exige --canal, ou --lancer pour les deux canaux")
        if a.carnet and not os.path.isabs(a.carnet):
            p.error("--carnet doit être un chemin absolu")
        if a.reprendre:
            if not a.carnet or a.chantier or a.date:
                p.error("--reprendre exige --carnet (la date vient de son nom) et refuse --chantier et --date")
            a.date = carnet.nuit_de(a.carnet)   # jamais de l'horloge : la reprise est celle de la nuit du carnet
        else:
            a.date = a.date or time.strftime("%Y-%m-%d")   # lue une fois : une nuit passe minuit
        try:
            datetime.date.fromisoformat(a.date)
        except ValueError:
            p.error("%s : AAAA-MM-JJ attendu" % ("le nom du carnet %s" % a.date if a.reprendre else "--date %s" % a.date))
    else:
        if a.plafond is None:
            p.error("--plafond est exigé sans --nuit")
        if a.canal or a.chantier or a.date or a.borne_usd is not None or a.borne_chantiers is not None or a.carnet \
                or a.reprendre or a.lancer:
            p.error("--canal, --chantier, --date, --borne-usd, --borne-chantiers, --carnet, --reprendre et --lancer exigent --nuit")
    if a.lancer:
        return lanceur(a)
    canal = bool(a.nuit and not a.chantier)   # la boucle d'un canal (NUI7), sinon un seul chantier ouvert
    if a.reprendre and (not os.path.isdir(a.dossier) or tete_de(os.path.abspath(a.dossier)) is None):
        print("GARDE: le worktree du canal est absent, ou n'est pas un dépôt Git avec un commit — %s" % os.path.abspath(a.dossier))
        return 1

    claude = claude_de(a.claude)
    if not claude:
        return 1
    print("CLAUDE=%s" % claude)
    try:
        # Le chantier du dossier lancé — pour un canal, son worktree, jamais la ligne de main (NUI25).
        racine, fichier, _, a.plugin_retard = lire_carte(os.path.abspath(a.dossier))
    except CarteGardee as e:
        print(e)
        return 1
    if not racine or (not fichier and not canal):
        print("ARRÊT aucun projet ou aucun fichier de fiches courant")
        return 1
    print("PROJET=%s · FICHIER=%s" % (racine, fichier or "aucun"))
    if a.nuit:
        a.carnet = a.carnet or carnet.du_jour(racine, a.date)
        if not a.carnet:
            print("GARDE: pas de dépôt Git pour le carnet de nuit — --carnet <chemin absolu>")
            return 1
        print("CARNET=%s · CANAL=%s · %s" % (a.carnet, a.canal, "DATE=%s" % a.date if canal else "CHANTIER=%s" % a.chantier))
        try:
            for role in ROLES:
                max_tours(role)
        except ValueError as e:
            print("GARDE: %s" % e)
            return 1
    traces = a.traces or tempfile.mkdtemp(prefix="vlp-boucle-")
    etat = {"jouees": 0, "tours": 0, "cout": 0.0, "verifiee": False}
    t_debut = time.time()
    if a.nuit:
        eveil(a)
    try:
        if not canal:
            verif = verification_de(racine) if a.nuit else None
            try:
                code, raison, _ = fiches_du_chantier(claude, a, racine, fichier, traces, verif, etat)
            except CarteGardee as e:
                code, raison = 1, "carte gardée — %s" % e
        elif fichier and not a.reprendre:   # le `COURANT=` du worktree du canal : un hérité de main n'y est pas
            code, raison = 1, "un chantier est déjà ouvert au départ (%s) — rien à découper" % fichier
        else:
            plan, erreur = lire_plan(racine, a)
            reprise = None
            if plan is not None and a.reprendre:
                reprise, erreur = lire_reprise(a, racine, plan[2])
            if plan is None or (a.reprendre and reprise is None):
                code, raison = 1, "plan illisible — %s" % erreur if plan is None else erreur
            else:
                a.borne_usd = plan[0] if a.borne_usd is None else a.borne_usd
                a.borne_chantiers = plan[1] if a.borne_chantiers is None else a.borne_chantiers
                todo, erreur_todo = lire_todo(racine)
                print("PLAN %s · canal %s · %d chantiers : %s · borne %s $ · %d chantiers"
                      % (a.date, a.canal, len(plan[2]), ", ".join(plan[2]), a.borne_usd, a.borne_chantiers), flush=True)
                if reprise:
                    print("REPRISE canal %s · %d sessions coupées · en cours : %s · base %s"
                          % (a.canal, reprise["coupees"], reprise["en_cours"] or "aucun", reprise["base"][:9]), flush=True)
                code, raison = boucle_canal(claude, a, racine, traces, etat, plan[2], todo, erreur_todo, reprise)
    finally:
        if a.nuit:
            eveil(a, False)

    print("ARRÊT %s" % raison)
    print("TOTAL %d fiches · %d tours · %.4f $ · %d s"
          % (etat["jouees"], etat["tours"], etat["cout"], int(time.time() - t_debut)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
