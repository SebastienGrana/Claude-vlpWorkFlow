"""Les hooks du kit : hook, filet, et le contrat du sous-agent (REF47 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import argparse
import fnmatch
import glob
import io
import json
import os
import re
import time
import unicodedata

import noyau.relecture  # `noyau.relecture.git_texte` : un test le remplace là
from noyau import etat
from noyau.carte import trouver
from noyau.commun import Absent, lignes_de, tampon_neuf
from noyau.facade import coeur
from noyau.fiches import cmd_cocher, rapport
from noyau.page import mesure

# Ce que la façade ré-exporte : les noms d'avant la découpe (photo de `tests/test_noms_publics.py`). Les décisions
# sorties de Git par REF47 — `heure_d_ajout` — se lisent ici seulement.
__all__ = [
    "APPEL_GIT", "ECHO_DONNEE", "EMOJIS_JAUGE", "ESSAI_REFUSE", "FICHE_A_JOUER", "FICHE_NOMMEE", "HEREDOC",
    "INTERROMPU", "JAUGE", "LECTURE_GIT", "MARQUE", "REFUS_GIT", "REFUS_GIT_AVANT", "REGLE", "REGLES",
    "SEUIL_FILET", "STATUTS", "SUITE_JAUGE", "VERDICTS", "cmd_contrat", "cmd_filet", "cmd_forme", "cmd_gardien",
    "cmd_hook", "comptoir_tours", "ecrit_git", "est_fichier_de_fiches", "fiche_jouee", "forme_texte",
    "lire_contrat", "lire_forme", "lire_max_turns", "ouverture", "ouvre", "sans_echo", "sans_heredoc", "type_agent",
    "verdict_fin",
]


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


# --- figer : les tests existants, en lecture seule pendant une fiche (REF10) ---------------------------------------

# Le corps de `/vlp:tache` que Claude Code injecte à chaque appel, tapé ou par l'outil `Skill` : ses arguments suivent.
TACHE = re.compile(r"Base directory for this skill: [^\n]*[\\/]skills[\\/]tache[ \t]*\n[ \t]*\n"
                   r"Arguments reçus :[ \t]*\n[ \t]*\n([^\n]*)")
CODE_FICHE = re.compile(r"\b[A-Z]{1,3}[0-9]+\b")
TITRE_FICHE = re.compile(r"^## ([A-Z]{1,3}[0-9]+) \[([ x])\]")
TESTS_DECLARES = re.compile(r"^\*\*Tests\*\* : modifiés — \S")
REFUS_TESTS = ("La fiche %s est en cours, et %s est un test existant : il ne se modifie pas pendant une fiche (REF10, "
               "choix Q2 : un agent qui ne touche pas aux tests ne triche plus). Ajoute plutôt un test neuf, ou un Edit "
               "d'ajout pur (old_string repris entier dans new_string). Si la fiche doit vraiment changer ce test, "
               "elle le déclare dès son cadrage, commitée, par une ligne « **Tests** : modifiés — <raison> » : "
               "demande-le à l'utilisateur, ne l'écris pas toi-même.\n")


def est_test(rel):
    """Vrai si `rel` (chemin relatif à la racine du projet, barres obliques) est un test : sous `tests/`, ou un
    `scripts/test-*.py` d'avant `REF52`."""
    return rel.startswith("tests/") or (os.path.dirname(rel) == "scripts" and fnmatch.fnmatch(
        os.path.basename(rel), "test-*.py"))


def texte_utilisateur(d):
    """Le texte d'une ligne de transcription si c'est un message utilisateur, sinon None : la chaîne, ou ses blocs
    `text` mis bout à bout — jamais un `tool_result`, qui citerait une transcription sans en être une."""
    m = d.get("message") if isinstance(d, dict) else None
    if not isinstance(m, dict) or m.get("role") != "user":
        return None
    c = m.get("content")
    if isinstance(c, str):
        return c
    return "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text") \
        if isinstance(c, list) else None


def fiche_de_transcription(lignes):
    """La fiche que joue une transcription (ses lignes JSON) : celle de `Fiche à jouer :` dans son premier message
    utilisateur (un sous-agent), sinon le dernier code de fiche des arguments du dernier `/vlp:tache` — `""` si
    l'appel n'en nomme pas (la prochaine fiche) —, sinon None. Ne lance rien."""
    fiche, premier = None, True
    for ligne in lignes:
        try:
            texte = texte_utilisateur(json.loads(ligne))
        except ValueError:
            continue
        if texte is None:
            continue
        jouee = FICHE_A_JOUER.search(texte) if premier else None
        if jouee:
            return jouee.group(1)
        premier = False
        for m in TACHE.finditer(texte):
            codes = CODE_FICHE.findall(m.group(1))
            fiche = codes[-1] if codes else ""
    return fiche


def fiche_en_cours(lignes, fiche):
    """Le code de la fiche en cours dans un fichier de fiches : `fiche` si sa case est vide, la première non cochée si
    `fiche` vaut `""`, None si elle est cochée ou absente."""
    for l in lignes:
        m = TITRE_FICHE.match(l)
        if m and (m.group(1) == fiche or (fiche == "" and m.group(2) == " ")):
            return m.group(1) if m.group(2) == " " else None
    return None


def tests_declares(lignes, fiche):
    """Vrai si la fiche `fiche` porte une ligne `**Tests** : modifiés — <raison>`, entre son titre et le suivant."""
    dedans = False
    for l in lignes:
        m = TITRE_FICHE.match(l)
        if m:
            dedans = m.group(1) == fiche
        elif dedans and TESTS_DECLARES.match(l):
            return True
    return False


def ajout_pur(entree):
    """Vrai si l'entrée d'un `Edit` n'ajoute que du texte : son `old_string` se retrouve entier dans son
    `new_string`. Un `Write` (`content`) n'en est jamais un."""
    old, new = entree.get("old_string"), entree.get("new_string")
    return isinstance(old, str) and isinstance(new, str) and old in new


def cible_test(d):
    """(racine, chemin relatif) du test existant que l'entrée de hook `d` veut modifier, ou None : pas d'outil lisible,
    fichier neuf, ajout pur, hors d'un projet équipé, ou pas un test. La racine est le projet équipé le plus proche du
    fichier visé, pas de `cwd` : un test d'un worktree écrit depuis le dossier principal se juge au worktree (REF22)."""
    ti = d.get("tool_input") if isinstance(d, dict) else None
    chemin = ti.get("file_path") if isinstance(ti, dict) else None
    cwd = d["cwd"] if isinstance(d.get("cwd"), str) else os.getcwd()
    if not isinstance(chemin, str) or not os.path.isfile(os.path.join(cwd, chemin)) or ajout_pur(ti):
        return None
    racine = trouver(os.path.dirname(os.path.join(cwd, chemin)))
    if racine is None:
        return None
    try:
        rel = os.path.relpath(os.path.join(cwd, chemin), racine).replace(os.sep, "/")
    except ValueError:   # un autre disque que le projet
        return None
    return (racine, rel) if est_test(rel) else None


def lignes_transcription(d):
    """Les lignes de la transcription de qui écrit : celle du sous-agent (`subagents/agent-<id>.jsonl` à côté de celle
    de la session, comme `cmd_filet`) s'il y en a un, sinon celle de la session ; [] si elle ne se lit pas."""
    chemin = d.get("transcript_path")
    if not isinstance(chemin, str):
        return []
    if d.get("agent_id"):
        sous = os.path.join(os.path.splitext(chemin)[0], "subagents", "agent-%s.jsonl" % d["agent_id"])
        chemin = sous if os.path.isfile(sous) else chemin
    try:
        with open(chemin, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


def cmd_figer(entree, sortie, erreur):
    """Le hook `PreToolUse` (`Write|Edit`) qui fige les tests existants pendant une fiche (REF10, choix Q2) : sort 2,
    la raison sur stderr, si l'outil modifie un test existant (`est_test`) autrement que par un ajout pur, pendant
    qu'une fiche est en cours et qu'elle ne déclare pas `**Tests** : modifiés — <raison>`. Muet et 0 sinon.

    La fiche en cours se lit dans la transcription (`fiche_de_transcription`) : le dernier `/vlp:tache <fiche>` de la
    session, ou le `Fiche à jouer :` du sous-agent — et elle n'est en cours que si sa case est vide dans le fichier de
    fiches courant (`courant_de`) : `cocher` la clôt. La déclaration se lit dans ce fichier tel que `HEAD` le garde —
    une ligne écrite pendant la fiche ne compte pas ; sans Git, dans l'arbre de travail. Limite : une écriture par
    un script ou une commande (`sed`, Python) ne passe pas par `Write|Edit` et n'est pas vue. `sortie` reste muette."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    cible = cible_test(d) if isinstance(d, dict) else None
    if cible is None:
        return 0
    racine, rel = cible
    fiche = fiche_de_transcription(lignes_transcription(d))
    try:
        courant = coeur.courant_de(racine) if fiche is not None else None
    except Absent:
        return 0
    if not courant:
        return 0
    lignes = lignes_de(os.path.join(racine, courant))
    code = fiche_en_cours(lignes, fiche)
    if code is None:
        return 0
    rc, texte = noyau.relecture.git_texte(["show", "HEAD:" + courant.replace("\\", "/")], racine)
    if tests_declares(texte.replace("\r\n", "\n").split("\n") if rc == 0 else lignes, code):
        return 0
    erreur.write(REFUS_TESTS % (code, rel))
    return 2


# --- filet -------------------------------------------------------------------

SEUIL_FILET = 3  # Tours restants à partir desquels on avertit le sous-agent


def cmd_filet(entree, sortie, erreur):
    """Avertit quand le sous-agent approche du plafond de tours.

    Lit le JSON du hook sur stdin — `PostToolUse` ou `PostToolUseFailure`, après
    tout outil. Si nous sommes dans un sous-agent (agent_type contient 'fiche'
    et agent_id existe), compte les tours déjà rendus et avertit si
    tours_restants <= SEUIL_FILET, au nom de l'événement reçu.
    Une fois par tour : le tampon `vlp-filet-<agent_id>-<tours>` (`tampon_neuf`) tait les suivants (TOU2).
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
    kit_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # scripts/noyau/ → le kit
    fiche_path = os.path.join(kit_root, "agents", "fiche.md")

    max_turns = lire_max_turns(fiche_path)
    if max_turns is None:
        return 0

    tours_restants = max_turns - tours
    if 0 < tours_restants <= SEUIL_FILET and tampon_neuf(f"vlp-filet-{agent_id}-{tours}"):
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
    Windows, dès 260 caractères, isfile et open disent absent un fichier présent (FIL1).
    Un octet non UTF-8 se lit remplacé (`errors="replace"`) : sa ligne compte encore,
    le compte n'est jamais coupé à mi-fichier (REF22)."""
    tours = set()
    try:
        with mesure().ouvrir(chemin) as f:
            f.reconfigure(errors="replace")
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


# --- contrat (chantier CON) ----------------------------------------------------

# Les verbes Git qui ne font que lire : tout autre verbe écrit, inconnu compris (chantier VRB).
LECTURE_GIT = frozenset(("diff", "status", "log", "show", "rev-parse", "ls-files", "blame", "grep"))
# Un appel Git : `git` en position de commande — début de ligne, après `;` `&` `|` `(` `)` `{` un
# accent grave, une quote ouvrante (`ssh h 'git …'`) ou au bout d'un chemin (`…/git.exe`), derrière
# d'éventuels `VAR=val`, `sudo`, `if`… —, ses options globales, puis son verbe (`verbe`). Ancré
# pour que `grep -c git f` ne lise pas le verbe `f`.
APPEL_GIT = re.compile(
    r"""(?:^|(?<=[;&|(){`'"/\\]))[ \t]*"""
    r"""(?:(?:\w+=\S*|sudo|env|time|command|nohup|exec|xargs|if|then|else|do|while|until|!)[ \t]+)*"""
    r"""git(?:\.exe)?['"]?(?![\w.-])"""
    r"""(?:[ \t]+(?:-[Cc][ \t]+(?:"[^"]*"|'[^']*'|\S+)|--no-pager|-P|--(?:git-dir|work-tree|namespace)=\S+))*"""
    r"""(?:[ \t]+(?P<verbe>-\S*|[A-Za-z][\w-]*))?""", re.M)
# Un heredoc `<<[-]MOT` (mot nu ou cité) : sa ligne d'ouverture, dont la suite (groupe 3), son
# corps (groupe 4), sa fin.
HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_]\w*)\1([^\n]*)\n(.*?)\n[ \t]*\2[ \t]*$", re.S | re.M)
STATUTS = ("FAITE", "RETOUR", "BLOQUÉE")
# Le cœur du refus du gardien (chantier ENQ) : `cmd_gardien` le met dans sa raison, `lire_contrat`
# le retrouve dans le `tool_result` d'un appel qui écrit dans Git pour le compter en bloqué plutôt
# qu'en écrit — indépendant de l'agent (`vlp:fiche`/`vlp:relecture`) et de la fin de phrase.
# `REFUS_GIT_AVANT`, celui d'avant VRB, se reconnaît encore dans les vieilles transcriptions.
REFUS_GIT = "retire tout appel Git hors lecture (diff, status, log, show…), le chef commite après"
REFUS_GIT_AVANT = "retire git commit/add/reset, le chef commite après"
# Un message utilisateur qui commence ainsi, après le dernier texte de l'assistant, marque le
# sous-agent interrompu plutôt que sans statut en tête (chantier ENQ).
INTERROMPU = "[Request interrupted by user"


def sans_heredoc(commande):
    """La commande, le corps des heredocs qui ne font qu'écrire un fichier tu : reçus par `cat`
    ou `tee`, hors `$(…)` et accents graves, sans `|` derrière — un heredoc reçu par `py`,
    `bash`… s'exécute, il reste lu ; les chaînes citées aussi (`ssh '…'`) (chantiers ECH, ECA)."""
    def taire(m):
        avant = commande[:m.start()]
        mots = [w for w in re.split(r"[;&|(\n`]", avant)[-1].split() if not re.match(r"\w+=", w)]
        recoit = os.path.basename(mots[0].strip("'\"")).lower() if mots else ""
        dans_sous = re.search(r"(?:\$\(|`)[^;&|()\n`]*$", avant)
        if recoit not in ("cat", "tee") or dans_sous or "|" in m.group(3):
            return m.group(0)
        return commande[m.start():m.start(4)] + commande[m.end(4):m.end()]
    return HEREDOC.sub(taire, commande)


ECHO_DONNEE = re.compile(r"""\b(?:echo|printf)\b(?P<args>[^\n;&|`]*?)"""
                         r"""(?:(?P<redir>>{1,2})[ \t]*(?:"[^"]*"|'[^']*'|\S+)|(?=[\n;&]|$))""", re.M)


def sans_echo(commande):
    """La commande, le texte cité d'un `echo`/`printf` dont la sortie va dans un fichier (`>`/`>>`)
    ou à l'écran tu : sans `|` dans le même segment, hors `$(…)` et accents graves — comme
    `sans_heredoc` pour `cat`/`tee` (chantier ENQ ; l'écran, dette VRB). Un `"…$(…)…"` reste lu :
    il s'exécute. Limite acceptée : `echo 'git add' > s.sh` puis `sh s.sh` passe — le
    gardien arrête une habitude, pas un attaquant."""
    def taire(m):
        avant = commande[:m.start()]
        dans_sous = re.search(r"(?:\$\(|`)[^;&|()\n`]*$", avant)
        if dans_sous:
            return m.group(0)
        args = re.sub(r"'[^']*'", "''", m.group("args"))
        args = re.sub(r'"[^"]*"', lambda q: q.group(0) if "$(" in q.group(0) else '""', args)
        return commande[m.start():m.start("args")] + args + commande[m.end("args"):m.end()]
    return ECHO_DONNEE.sub(taire, commande)


# Un chercheur de texte en tête de segment (`grep`, `rg`, `Select-String`…) et ses arguments jusqu'au `;` `&` `|`
# suivant hors quotes (`args`) ; ou la valeur citée d'un `--grep` (`valeur`) — des motifs, pas des appels (REF22).
MOTIF_CITE = re.compile(
    r"""(?:(?:^|(?<=[;&|(){\n`]))[ \t]*(?:\S*[/\\])?(?i:grep|egrep|fgrep|rg|select-string|sls|findstr)(?:\.exe)?"""
    r"""(?![\w.-])(?P<args>(?:"[^"]*"|'[^']*'|[^\n;&|`'"])*)"""
    r"""|--grep[= ][ \t]*(?P<valeur>"[^"]*"|'[^']*'))""", re.M)


def sans_motif(commande):
    """La commande, les chaînes citées d'un `grep`/`rg`/`Select-String`/`sls`/`findstr` en tête de segment, et la
    valeur citée d'un `--grep=`, vidées : `grep "git push" f` cherche un texte, il n'appelle pas Git (REF22). Un
    `"…$(…)…"` reste lu (il s'exécute), comme tout ce qui suit un `;` `&` `|` hors quotes ; un chercheur dans
    `$(…)` ou entre accents graves aussi, comme `sans_echo`. Rend la commande telle quelle sans chercheur."""
    def vider(q):
        """La chaîne citée `q` vidée (`""` ou `''`) ; telle quelle si elle porte un `$(`."""
        return q.group(0) if "$(" in q.group(0) else q.group(0)[0] * 2

    def taire(m):
        """Le chercheur ou le `--grep` de `m`, ses chaînes vidées ; tel quel dans un `$(…)` ou entre accents graves."""
        if re.search(r"(?:\$\(|`)[^;&|()\n`]*$", commande[:m.start()]):
            return m.group(0)
        nom = "args" if m.group("args") is not None else "valeur"
        dedans = re.sub(r""""[^"]*"|'[^']*'""", vider, m.group(nom))
        return commande[m.start():m.start(nom)] + dedans + commande[m.end(nom):m.end()]
    return MOTIF_CITE.sub(taire, commande)


def ecrit_git(commande):
    """Vrai si un `APPEL_GIT` de la commande a un verbe hors `LECTURE_GIT` — une option inconnue
    en tient lieu, `git` seul n'écrit pas (chantier VRB). Lu sur la commande `sans_heredoc`, `sans_echo`
    puis `sans_motif` : un heredoc ou un `echo`/`printf` qui ne font qu'écrire les mots `git commit` dans
    un fichier, ou un `grep "git commit"` qui les cherche, n'écrivent pas dans Git (chantiers ECH, ENQ, REF22)."""
    return any(m.group("verbe") not in (None, *LECTURE_GIT)
               for m in APPEL_GIT.finditer(sans_motif(sans_echo(sans_heredoc(commande)))))


def lire_contrat(chemin):
    """(premier mot du dernier message texte, appels qui écrivent dans Git, ceux que le gardien a
    bloqués (`REFUS_GIT` dans leur `tool_result`), interrompu) d'une transcription. Un appel qui
    écrit dans Git compte d'abord en écrit ; si son `tool_result` porte `REFUS_GIT`, il bascule en
    bloqué — sans `tool_result` (transcription coupée), il reste écrit. (None, 0, 0, False) si
    elle ne s'ouvre pas."""
    mot, git, bloque, interrompu = "", 0, 0, False
    en_attente = {}
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    d = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                m = d.get("message") if isinstance(d, dict) else None
                if not isinstance(m, dict):
                    continue
                contenu = m.get("content")
                if m.get("role") == "user":
                    for b in contenu if isinstance(contenu, list) else []:
                        if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                            continue
                        tid = b.get("tool_use_id")
                        if tid not in en_attente:
                            continue
                        texte_res = b.get("content")
                        if isinstance(texte_res, list):
                            texte_res = " ".join(x.get("text", "") for x in texte_res if isinstance(x, dict))
                        if isinstance(texte_res, str) and (REFUS_GIT in texte_res or REFUS_GIT_AVANT in texte_res):
                            git -= 1
                            bloque += 1
                        del en_attente[tid]
                    texte = contenu if isinstance(contenu, str) else None
                    if texte is None and isinstance(contenu, list):
                        textes = [x.get("text", "") for x in contenu if isinstance(x, dict) and x.get("type") == "text"]
                        texte = textes[0] if textes else None
                    if mot and isinstance(texte, str) and texte.startswith(INTERROMPU):
                        interrompu = True
                    continue
                if m.get("role") != "assistant" or not isinstance(contenu, list):
                    continue
                for b in contenu:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and b.get("text", "").strip():
                        mot, interrompu = b["text"].split()[0], False
                    elif b.get("type") == "tool_use" and b.get("name") in ("Bash", "PowerShell"):
                        commande = (b.get("input") or {}).get("command")
                        if isinstance(commande, str) and ecrit_git(commande):
                            git += 1
                            en_attente[b.get("id")] = True
    except (OSError, UnicodeDecodeError):
        return None, 0, 0, False
    return mot, git, bloque, interrompu


def type_agent(chemin):
    """L'`agentType` du `.meta.json` voisin ; `?` s'il manque ou ne se lit pas."""
    try:
        with mesure().ouvrir(chemin[:-len(".jsonl")] + ".meta.json") as f:
            return json.load(f).get("agentType") or "?"
    except (OSError, ValueError, AttributeError):
        return "?"


def ouverture(chemin):
    """(heure, None) : l'heure d'auteur du plus ancien commit qui ajoute le fichier de fiches —
    « Chantier X ouvert » pour 69 fichiers sur 80 ; le premier commit qui nomme le préfixe est
    souvent l'ajout à la TODO (chantier CHK). (None, raison) sans git ou sans ce commit."""
    import subprocess
    try:
        r = subprocess.run([etat.GIT, "log", "--diff-filter=A", "--format=%at", "--", os.path.basename(chemin)],
                           cwd=os.path.dirname(os.path.abspath(chemin)), capture_output=True, encoding="utf-8",
                           errors="replace", timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git ne se lance pas : %s" % e
    return heure_d_ajout(r.returncode, r.stdout)


def heure_d_ajout(code, texte):
    """(heure, None) : la dernière ligne — le plus ancien commit — d'une sortie de `git log --diff-filter=A
    --format=%at` ; (None, raison) si `git` a échoué ou n'a rien rendu. Ne lance rien (REF47)."""
    heures = texte.split()
    if code or not heures or not heures[-1].isdigit():
        return None, "aucun commit n'ajoute ce fichier : l'ouverture n'est pas commitée"
    return int(heures[-1]), None


def cmd_contrat(a, sortie):
    """Une ligne par transcription de sous-agent : id, type, départ de la session parente, dernier
    mot (`(interrompu)` sinon), appels qui écrivent dans Git, ceux que le gardien a bloqués ; puis
    le bilan. Un interrompu ne compte pas en sans-statut (chantier ENQ). `--ouverture` :
    ceux partis — leur heure à eux, pas celle de la session parente — depuis l'ajout du fichier."""
    m = mesure()
    depuis = ouvert = None
    if a.depuis:
        depuis, err = m.borne(a.depuis)
        if err:
            sortie.write("GARDE: --depuis %s : %s\n" % (a.depuis, err))
            return 1
    if a.ouverture:
        ouvert, err = ouverture(a.ouverture)
        if err:
            sortie.write("GARDE: --ouverture %s : %s\n" % (a.ouverture, err))
            return 1
        sortie.write("DEPUIS %s · ouverture de %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ouvert)),
                                                        a.ouverture))
    chemins = a.transcriptions
    if not chemins:
        motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", "*", *m.SOUS_AGENTS)
        chemins = [c for c in sorted(glob.glob(motif)) if type_agent(c) == "vlp:fiche"]
    n = commitent = bloques = sans_statut = interrompus = 0
    for c in chemins:
        parent = os.path.dirname(os.path.dirname(c)) + ".jsonl"
        t, _ = m.depart(parent)     # absente ou illisible : t None
        if depuis is not None and (t is None or t < depuis):
            continue
        if ouvert is not None and (m.depart(c)[0] or 0) < ouvert:
            continue
        mot, git, bloque, interrompu = lire_contrat(c)
        if mot is None:
            sortie.write("ILLISIBLE %s\n" % c)
            continue
        heure_ = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t is not None else "?"
        id_ = os.path.basename(c)[len("agent-"):-len(".jsonl")]
        affiche = "(interrompu)" if interrompu else (mot or "(vide)")
        sortie.write("%s %s %s %s git %d bloqué %d\n" % (id_, type_agent(c), heure_, affiche, git, bloque))
        n += 1
        commitent += git > 0
        bloques += bloque > 0
        if interrompu:
            interrompus += 1
        elif mot not in STATUTS:
            sans_statut += 1
    sortie.write("CONTRAT %d sous-agents · %d écrivent dans Git · %d bloqués par le gardien · "
                 "%d sans statut en tête · %d interrompus\n" % (n, commitent, bloques, sans_statut, interrompus))
    return 0


VERDICTS = ("ACCEPTÉE", "REFUSÉE")     # les mots de tête de `vlp:relecture`
ESSAI_REFUSE = "FAITE refusée à la relecture."   # la ligne numérotée que `cocher --refuser` écrit ; boucle.py l'importe
JAUGE = ("Tout va bien", "Ça tient, mais", "Imprévu", "Pas bon", "Grosse erreur")
# La forme d'une jauge (chantier OUV) : un de ces émojis en tête, ou le mot suivi de `—`, `…`
# ou de la fin de ligne — `- Imprévu : j'ai dû…` est une puce, pas une jauge.
EMOJIS_JAUGE = ("✅", "🟢", "⚠", "❌", "🔥")
SUITE_JAUGE = re.compile(r"\*{0,2}\.?\*{0,2}[ \t]*(?:—|–|…|$)")


REGLES = ("tout", "tiret", "deux", "tete")     # la partie du texte que juge `forme_texte` (chantier JUG)
REGLE = "tete"     # retenue en JUG1 : le défaut du gardien et de `forme` ; `tout` rejoue l'ancienne mesure


def ouvre(ligne):
    """La ligne sans ses marques de tête — espaces, `#`, `*`, `-`, `>` et émojis ; `«` reste."""
    i = 0
    while i < len(ligne) and (ligne[i] in " \t#*->" or unicodedata.category(ligne[i]) in ("So", "Mn", "Cf")):
        i += 1
    return ligne[i:]


def forme_texte(texte, regle=REGLE):
    """(resume 0|1, jauge 0|1) de la partie du texte que juge `regle` ; (0, 0) si vide ou absent.
    `tete` (défaut, celle du gardien) : le mot doit ouvrir une ligne, marques retirées — une
    citation en milieu de phrase ne compte pas — et une jauge en avoir la forme, `EMOJIS_JAUGE`
    en tête ou `SUITE_JAUGE` derrière (chantier OUV) ; `tout` : le texte entier ; `tiret` : après la
    dernière ligne `---`, sinon tout ; `deux` : les deux dernières lignes non vides."""
    if not isinstance(texte, str):
        return 0, 0
    lignes = texte.splitlines()
    if regle == "tete":
        tetes = [(l[:len(l) - len(ouvre(l))], ouvre(l)) for l in lignes]
        return (int(any(t.startswith("En résumé") for _, t in tetes)),
                int(any(re.match(re.escape(j) + r'\b', t) and (any(e in marques for e in EMOJIS_JAUGE)
                                                               or SUITE_JAUGE.match(t[len(j):]))
                        for marques, t in tetes for j in JAUGE)))
    if regle == "tiret":
        tirets = [i for i, l in enumerate(lignes) if l.strip() == "---"]
        if tirets:
            texte = "\n".join(lignes[tirets[-1] + 1:])
    elif regle == "deux":
        texte = "\n".join([l for l in lignes if l.strip()][-2:])
    resume = int("En résumé" in texte)
    # Mots entiers, pas sous-chaîne : « Pas bon » ne matche pas « Pas bonne » ; `tete` borne de même
    jauge = int(any(re.search(r'\b' + re.escape(j) + r'\b', texte) for j in JAUGE))
    return resume, jauge


def lire_forme(chemin, regle=REGLE):
    """(caractères par type User/Project/AutoMem, resume 0|1, jauge 0|1, tete 0|1) d'une
    transcription, resume et jauge selon `regle` ; (None, 0, 0, 0) si elle ne s'ouvre pas. Les fichiers d'instructions sont
    ceux du premier attachment `instructions` — une entrée de premier niveau
    `{"attachment": {"type": "instructions", "files": […]}}`, pas un champ de `message`."""
    chars = {"User": 0, "Project": 0, "AutoMem": 0}
    vu, dernier = False, ""
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    d = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                if not isinstance(d, dict):
                    continue
                att = d.get("attachment")
                if not vu and isinstance(att, dict) and att.get("type") == "instructions":
                    vu = True
                    for fi in att.get("files") or []:
                        if isinstance(fi, dict) and fi.get("type") in chars and isinstance(fi.get("content"), str):
                            chars[fi["type"]] += len(fi["content"])
                m = d.get("message")
                if not isinstance(m, dict) or m.get("role") != "assistant" or not isinstance(m.get("content"), list):
                    continue
                for b in m["content"]:
                    if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                        dernier = b["text"].strip()
    except (OSError, UnicodeDecodeError):
        return None, 0, 0, 0
    resume, jauge = forme_texte(dernier, regle)
    tete = int(bool(dernier) and dernier.split()[0] in STATUTS + VERDICTS)
    return chars, resume, jauge, tete


def cmd_forme(a, sortie):
    """Une ligne par transcription de sous-agent : id, type, départ, et caractères
    d'instructions par type, plus resume, jauge, tete ; puis le bilan."""
    m = mesure()
    depuis = None
    if a.depuis:
        depuis, err = m.borne(a.depuis)
        if err:
            sortie.write("GARDE: --depuis %s : %s\n" % (a.depuis, err))
            return 1
    chemins = a.transcriptions
    if not chemins:
        motif = os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", "*", *m.SOUS_AGENTS)
        chemins = [c for c in sorted(glob.glob(motif)) if type_agent(c) in ("vlp:fiche", "vlp:relecture")]
    n = resume_total = jauge_total = tete_total = user_total = 0
    for c in chemins:
        t, _ = m.depart(c)
        if depuis is not None and (t is None or t < depuis):
            continue
        chars, resume, jauge, tete = lire_forme(c, a.regle)
        if chars is None:
            sortie.write("ILLISIBLE %s\n" % c)
            continue
        heure_ = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t is not None else "?"
        id_ = os.path.basename(c)[len("agent-"):-len(".jsonl")]
        sortie.write("%s %s %s user %d projet %d memoire %d resume %d jauge %d tete %d\n" % (
            id_, type_agent(c), heure_, chars["User"], chars["Project"], chars["AutoMem"], resume, jauge, tete))
        n += 1
        user_total += chars["User"]
        resume_total += resume
        jauge_total += jauge
        tete_total += tete
    user_moyenne = user_total // n if n > 0 else 0
    sortie.write("FORME %d sous-agents · user %d car. · resume %d · jauge %d · tete %d\n"
                 % (n, user_moyenne, resume_total, jauge_total, tete_total))
    return 0


FICHE_A_JOUER = re.compile(r"Fiche à jouer :\s*(\S+)")
# Jouer ou relire : les prompts de `/vlp:enchainer` et de `vlp:relire` (« Fiche à relire, et le commit… : »).
FICHE_NOMMEE = re.compile(r"Fiche à (?:jouer|relire)[^:\n]*:\s*(\S+)")


def fiche_jouee(chemin, motif=FICHE_A_JOUER):
    """La fiche que `vlp:jouer` a donnée au sous-agent : `motif` (`Fiche à jouer :` d'office) suivi de
    son id, dans le premier message utilisateur de sa transcription ; None si rien ne se lit."""
    try:
        with mesure().ouvrir(chemin) as f:
            for ligne in f:
                try:
                    m = json.loads(ligne).get("message")
                except (ValueError, AttributeError):
                    continue
                if not isinstance(m, dict) or m.get("role") != "user":
                    continue
                c = m.get("content")
                texte = c if isinstance(c, str) else " ".join(
                    b.get("text", "") for b in c if isinstance(b, dict)) if isinstance(c, list) else ""
                t = motif.search(texte)
                return t.group(1) if t else None
    except (OSError, UnicodeDecodeError):
        return None
    return None


def verdict_fin(d, deja_renvoye=False):
    """La raison de renvoyer au travail un sous-agent `vlp:fiche` qui s'arrête, ou None.
    `deja_renvoye` (`stop_hook_active`) : la tête n'est plus jugée — un troisième renvoi ne la
    corrigerait pas —, un `FAITE` l'est encore (chantier GAR)."""
    message = d.get("last_assistant_message")
    if not isinstance(message, str):
        return None
    mot = message.split()[0] if message.strip() else "(vide)"
    if mot not in STATUTS:
        return None if deja_renvoye else (
            "Ton dernier message commence par « %s » : son premier mot doit être FAITE, RETOUR ou "
            "BLOQUÉE (agents/fiche.md). Réécris-le, statut en tête." % mot)
    if mot != "FAITE" or not isinstance(d.get("agent_transcript_path"), str):
        return None
    fiche = fiche_jouee(d["agent_transcript_path"])
    racine = trouver(d.get("cwd") or os.getcwd())
    if fiche is None or racine is None:
        return None
    try:
        courant = coeur.courant_de(racine)
    except Absent:
        return None
    if courant is None:
        return None
    o = io.StringIO()
    cmd_cocher(argparse.Namespace(fichier=os.path.join(racine, courant), fiche=fiche, verifier=True), o)
    s = o.getvalue()
    if "TÊTE " in s:
        return ("Le dernier commit du dépôt nomme %s : tu as commité, contre agents/fiche.md. N'y touche "
                "pas ; rends RETOUR en le disant, le chef décidera." % fiche)
    if "CASE %s [ ]" % fiche in s:
        return ("FAITE, mais la case de %s est vide : coche-la par vlp.py cocher, puis rends FAITE." % fiche)
    return None


def cmd_gardien(entree, sortie):
    """Le contrat d'`agents/fiche.md` tenu à la sortie du sous-agent (chantier CON), le refus
    de l'écriture Git étendu à `vlp:relecture` (chantier RLG), et le filtrage de la forme (résumé
    et jauge) pour les deux agents — renvoi si une ligne du dernier message s'ouvre par « En
    résumé » ou un mot de JAUGE, selon `forme_texte` et sa règle par défaut (chantiers FOR, JUG). Muet hors de ces deux agents et sur une entrée illisible : il ne
    bloque jamais sur ce qu'il ne lit pas."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict):
        return 0
    agent_type = d.get("agent_type")
    if not isinstance(agent_type, str):
        return 0
    relecteur = "relecture" in agent_type
    if "fiche" not in agent_type and not relecteur:
        return 0
    ev = d.get("hook_event_name")
    if ev == "PreToolUse" and d.get("tool_name") in ("Bash", "PowerShell"):
        outil = d.get("tool_input")
        commande = outil.get("command") if isinstance(outil, dict) else None
        if isinstance(commande, str) and ecrit_git(commande):
            agent, fin = ("relecture", "ton verdict") if relecteur else ("fiche", "ton statut")
            sortie.write(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": ("Un sous-agent vlp:%s n'écrit pas dans Git (agents/%s.md) : %s %s."
                                            % (agent, agent, REFUS_GIT, fin))}},
                ensure_ascii=False) + "\n")
    elif ev == "SubagentStop":
        dernier_msg = d.get("last_assistant_message", "")
        resume, jauge = forme_texte(dernier_msg)
        stop_hook_active = bool(d.get("stop_hook_active"))

        # Pour vlp:fiche : d'abord verdict_fin (statut, case, commit), puis forme si aucune raison et pas déjà renvoyé
        if not relecteur:
            try:
                raison = verdict_fin(d, deja_renvoye=stop_hook_active)
            except (Absent, OSError, ValueError):
                raison = None
            if raison:
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
            elif (resume or jauge) and not stop_hook_active:
                raison = "Ton dernier message porte un « En résumé » ou une jauge : ton lecteur est le chef (agents/fiche.md). Réécris-le sans eux, statut en tête."
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
        # Pour vlp:relecture : seulement forme
        else:
            if (resume or jauge) and not stop_hook_active:
                raison = "Ton dernier message porte un « En résumé » ou une jauge : ton lecteur est le chef (agents/relecture.md). Réécris-le sans eux, statut en tête."
                sortie.write(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=False) + "\n")
    return 0
