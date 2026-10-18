"""Le bac d'essai, et l'aperçu local des pages (REF47 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import glob
import hashlib
import json
import os
import re
import noyau.relecture   # `noyau.relecture.<nom>` : un test remplace ce nom là (REF46)

import carnet

from noyau.page import (mesure)
from noyau.hooks import (lire_max_turns)

__all__ = [
    "BAC_FICHES", "BAC_CHANTIER", "BAC_FICHIER", "BAC_COMMANDES", "CLAUDE_ABSENT", "CLAUDE_SANS_EXE", "CLAUDE_APP",
    "dossiers_claude_code", "version_claude", "trouver_claude", "cmd_claude", "cmd_bac", "KIT_EXCLUS",
    "MUTANT_EXCLUS", "EMPREINTE_EXCLUS", "SUITE_VERTE", "empreinte_kit", "chemin_suite_verte", "noter_suite_verte",
    "MARQUE_SUITE", "est_kit", "commande_suite", "suite_manquante", "cmd_kit_essai", "cmd_transcription", "TYPES_APERCU", "LARGEUR_TELEPHONE",
    "PORT_APERCU", "PAGE_SERVIE", "faire_serveur", "cmd_servir", "lire_arg", "cmd_nuits_noter",
]


# --- bac ---------------------------------------------------------------------

# Le bac d'essai de FIL3 (journal du 2026-09-24) : fixe, en constantes.
# Le fichier de fiches porte la marque d'ouverture, dans le dossier de contexte : `courant_de` le trouve (NUI31).
BAC_FICHES = "ctx/fiches.md"
BAC_CHANTIER = """# Chantier courant — bac d'essai

- **contexte** : ctx/
- **artefact du chantier** : aucun
- **livraison** : aucune
- **vérification** : aucune — lire le statut rendu

Lettres de fiche déjà prises : F (Deux fiches factices). Un nouveau chantier en choisit un autre.
"""
BAC_FICHIER = """# Chantier F — bac d'essai, deux fiches factices

**Ouvert.** le 2026-09-24.

## Le socle commun

Un bac d'essai : rien à écrire, rien à commiter.

## L'ordre des fiches

F1, puis F2.

---

<!-- FICHE:F1 -->
## F1 [ ] — Lire douze fichiers

**Prompt**
Lis `n01.txt`, `n02.txt`, … jusqu'à `n12.txt`, dans l'ordre, par l'outil `Read` :
un appel par message, d'affilée, dans cette même exécution.

**Critère de fin**
Les douze fichiers lus.
<!-- /FICHE -->

---

<!-- FICHE:F2 -->
## F2 [ ] — Lancer douze fois exit 3

**Prompt**
Lance douze fois `exit 3` par l'outil `Bash` : un appel par message, d'affilée,
dans cette même exécution.

**Critère de fin**
Douze appels lancés.
<!-- /FICHE -->
"""
BAC_COMMANDES = (
    'claude -p "Appelle l\'outil Skill avec skill \\"vlp:jouer\\" et args \\"F1\\", puis recopie son'
    ' resultat tel quel. Rien d\'autre." --model haiku --max-budget-usd 1 --permission-mode acceptEdits'
    ' --allowedTools "Skill" --output-format stream-json --verbose',
    'claude -p "Appelle l\'outil Skill avec skill \\"vlp:jouer\\" et args \\"F2\\", puis recopie son'
    ' resultat tel quel. Rien d\'autre." --model haiku --max-budget-usd 1 --permission-mode acceptEdits'
    ' --allowedTools "Skill" "Bash" --output-format stream-json --verbose < /dev/null',
)


CLAUDE_ABSENT = "GARDE: claude.exe introuvable — PATH, Packages et APPDATA vus\n"
# Le pre-commit refuse le commit sur ce début de ligne, et laisse passer sur celui de CLAUDE_ABSENT (VIT19).
CLAUDE_SANS_EXE = "GARDE: claude.exe absent de l'app Claude — cherché à */ et à */*/ sous %s\n"
# L'app Claude : Packages d'abord — l'app du Store, vue d'un terminal comme de l'app —, puis `%APPDATA%`, vue de
# l'app seule (REG3).
CLAUDE_APP = (("LOCALAPPDATA", ("Packages", "Claude_*", "LocalCache", "Roaming", "Claude")), ("APPDATA", ("Claude",)))


def dossiers_claude_code():
    """Rendre les dossiers `claude-code` de l'app Claude, une liste par racine de `CLAUDE_APP`, dans son ordre ; une
    variable absente ou une app absente rend une liste vide (VIT19)."""
    return [glob.glob(os.path.join(os.environ[v], *parties, "claude-code")) if os.environ.get(v) else []
            for v, parties in CLAUDE_APP]


def version_claude(dossier, chemin):
    """Rendre la version de `chemin`, lue au dossier juste sous `dossier` (`claude-code/<version>/…`), en nombres :
    2.1.99 passe avant 2.1.280 (CLI) ; l'empreinte que l'app range dessous (VIT19) n'y compte pas."""
    nom = os.path.relpath(chemin, dossier).split(os.sep)[0]
    return [int(x) if x.isdigit() else 0 for x in nom.split(".")]


def trouver_claude():
    """Rendre le `claude` du kit (chantier CLI) : `VLP_CLAUDE`, le PATH, puis la plus haute version de l'app, racine
    par racine (`CLAUDE_APP`) — à `claude-code/<version>/` comme à `claude-code/<version>/<empreinte>/` (VIT19) —,
    sinon None."""
    import shutil
    if os.environ.get("VLP_CLAUDE"):
        return os.environ["VLP_CLAUDE"]
    sur_path = shutil.which("claude")
    if sur_path:
        return sur_path
    for dossiers in dossiers_claude_code():
        trouves = [(d, p) for d in dossiers for motif in ("*", os.path.join("*", "*"))
                   for p in glob.glob(os.path.join(d, motif, "claude.exe"))]
        if trouves:
            return max(trouves, key=lambda t: version_claude(*t))[1]
    return None


def cmd_claude(sortie):
    """Imprimer `CLAUDE <chemin>` et rendre 0 ; sinon une `GARDE:` et rendre 1 — `CLAUDE_SANS_EXE` si l'app est là
    sans son `claude.exe`, que le pre-commit refuse, `CLAUDE_ABSENT` sinon, qu'il laisse passer (VIT19)."""
    chemin = trouver_claude()
    if chemin:
        sortie.write("CLAUDE %s\n" % chemin)
        return 0
    app = [d for dossiers in dossiers_claude_code() for d in dossiers]
    sortie.write(CLAUDE_SANS_EXE % " et ".join(app) if app else CLAUDE_ABSENT)
    return 1


def cmd_bac(dossier, sortie):
    """Pose le bac d'essai de FIL3 dans `dossier`, vide ou absent, et imprime ses commandes `claude -p`."""
    if os.path.exists(dossier) and (not os.path.isdir(dossier) or os.listdir(dossier)):
        sortie.write("GARDE: %s existe et n'est pas un dossier vide — rien d'écrit\n" % dossier)
        return 1
    os.makedirs(dossier, exist_ok=True)
    fichiers = {"CHANTIER.md": BAC_CHANTIER, BAC_FICHES: BAC_FICHIER}
    fichiers.update(("n%02d.txt" % k, "fichier %02d\n" % k) for k in range(1, 13))
    os.makedirs(os.path.join(dossier, os.path.dirname(BAC_FICHES)), exist_ok=True)
    for nom, texte in fichiers.items():
        with open(os.path.join(dossier, nom), "w", encoding="utf-8", newline="") as f:
            f.write(texte)
    sortie.write("BAC %s\n" % dossier)
    for c in BAC_COMMANDES:
        sortie.write(c + "\n")
    chemin = trouver_claude()
    if not chemin:
        sortie.write(CLAUDE_ABSENT)
    sortie.write('SESSION Set-Location "%s"; & "%s"\n' % (os.path.abspath(dossier), chemin or "claude"))
    return 0


KIT_EXCLUS = (".git", ".claude", "context AI", "__pycache__", "relais-python.err", ".venv", ".couverture",
              ".ruff_cache")  # atelier (REF3, REF8) ; le cache de ruff, écrit après la suite, la rendait périmée (REF59)
# La copie d'un mutant garde `context AI/` : la suite y lit la carte du kit (NIV1) et la pièce de JUG2 (VIT2).
MUTANT_EXCLUS = tuple(n for n in KIT_EXCLUS if n != "context AI")
# L'empreinte d'une suite verte (VIT11) laisse aussi ce que la clôture d'une fiche écrit après la suite (`sante --base`)
# et les sorties des evals, ignorées par Git ; elle vit dans le dossier Git du kit, hors suivi, une par worktree.
EMPREINTE_EXCLUS = KIT_EXCLUS + ("sante-base.json", "results")
SUITE_VERTE = "vlp-suite-verte"


def empreinte_kit(racine):
    """Rendre le sha256 des fichiers du kit `racine` tels qu'ils sont sur disque, commités ou non : chemins relatifs
    et contenus, dans l'ordre, sans `EMPREINTE_EXCLUS` (VIT11)."""
    h = hashlib.sha256()
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = sorted(s for s in sous if s not in EMPREINTE_EXCLUS)
        for nom in sorted(f for f in fichiers if f not in EMPREINTE_EXCLUS):
            chemin = os.path.join(dossier, nom)
            with open(chemin, "rb") as f:
                h.update(os.path.relpath(chemin, racine).replace(os.sep, "/").encode("utf-8") + b"\0" + f.read() + b"\0")
    return h.hexdigest()


def chemin_suite_verte(racine):
    """Rendre `<dossier Git de racine>/vlp-suite-verte`, ou `None` hors dépôt (la copie d'un mutant)."""
    code, dossier = noyau.relecture.git_texte(["rev-parse", "--absolute-git-dir"], racine)
    return os.path.join(dossier.strip(), SUITE_VERTE) if code == 0 and dossier.strip() else None


def noter_suite_verte(racine, empreinte):
    """Écrire `empreinte` comme celle de la dernière suite entière verte du kit `racine` ; hors dépôt, rien (VIT11)."""
    chemin = chemin_suite_verte(racine)
    if chemin:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(empreinte + "\n")


MARQUE_SUITE = ("tests", "conftest.py")   # la suite du kit, pytest (REF59) ; sa présence dit le kit


def est_kit(racine):
    """Vrai si `racine` est le kit vlp lui-même — son plugin et sa suite —, pas un projet équipé (VIT11)."""
    return all(os.path.isfile(os.path.join(racine, *p)) for p in ((".claude-plugin", "plugin.json"), MARQUE_SUITE))


def commande_suite(projet, parallele=True):
    """La commande de la suite du kit, à lancer depuis le dossier dont on joue les tests (le kit, ou la copie d'un
    mutant) : pytest par `uv`, dans l'environnement de `projet` — le kit qui a son `.venv` (REF59). `parallele` : sur
    4 processus (`-n 4`, REF19). Un test la remplace ici par son faux script."""
    import shutil
    return ([shutil.which("uv") or "uv", "run", "--frozen", "--project", projet, "pytest", "-q"]
            + (["-n", "4"] if parallele else []))


def suite_manquante(fichier):
    """Rendre le kit dont `fichier` fait partie si sa dernière suite verte n'a pas joué ses fichiers d'aujourd'hui,
    sinon `None` — et `None` hors du kit : un projet équipé a ses propres tests (VIT11)."""
    code, racine = noyau.relecture.git_texte(["rev-parse", "--show-toplevel"], os.path.dirname(os.path.abspath(fichier)))
    racine = racine.strip()
    if code != 0 or not racine or not est_kit(racine):
        return None
    chemin = chemin_suite_verte(racine)
    try:
        with open(chemin or "", encoding="utf-8") as f:
            notee = f.read().strip()
    except OSError:
        notee = ""
    return None if notee == empreinte_kit(racine) else racine


def cmd_kit_essai(dossier, max_turns, source, sortie):
    """Une copie jetable du kit à plafond bas (EVF2) : l'eval se lance sur elle, le vrai kit ne bouge pas."""
    import shutil
    source = os.path.abspath(source or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))   # scripts/noyau/ → le kit
    if os.path.exists(dossier) and (not os.path.isdir(dossier) or os.listdir(dossier)):
        sortie.write("GARDE: %s existe et n'est pas un dossier vide — rien d'écrit\n" % dossier)
        return 1
    fiche = os.path.join(source, "agents", "fiche.md")
    avant = lire_max_turns(fiche)
    if avant is None:
        sortie.write("GARDE: pas de ligne maxTurns dans %s — rien d'écrit\n" % fiche)
        return 1

    def exclus(racine, noms):
        rel = os.path.relpath(racine, source).replace(os.sep, "/")
        return [n for n in noms if n in KIT_EXCLUS or (rel == "evals" and n == "results")]

    if os.path.isdir(dossier):
        os.rmdir(dossier)
    shutil.copytree(source, dossier, ignore=exclus)
    copie = os.path.join(dossier, "agents", "fiche.md")
    with open(copie, encoding="utf-8", newline="") as f:
        texte = f.read()
    texte = re.sub(r"(?m)^maxTurns:.*$", "maxTurns: %d" % max_turns, texte, count=1)
    with open(copie, "w", encoding="utf-8", newline="") as f:
        f.write(texte)
    sortie.write("KIT %s · maxTurns %d → %d\n" % (dossier, avant, max_turns))
    return 0


def cmd_transcription(chemin, sortie):
    """Compte la transcription d'un sous-agent (chantier BAC) : tours comme `comptoir_tours`,
    appels, avertissements du filet et l'appel qui les précède, erreurs de hook, dernier message."""
    tours, appels, erreurs_outil, avertis = [], {}, {}, []
    hook_erreurs, dernier_id, stop, textes = 0, None, None, {}
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
                if isinstance(att, dict):
                    if att.get("type") == "hook_additional_context":
                        avertis.append(att)
                    elif att.get("type") == "hook_non_blocking_error":
                        hook_erreurs += 1
                message = d.get("message")
                if not isinstance(message, dict):
                    continue
                contenu = message.get("content")
                blocs = contenu if isinstance(contenu, list) else []
                if d.get("type") == "user":
                    for b in blocs:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            erreurs_outil[b.get("tool_use_id")] = bool(b.get("is_error"))
                    continue
                mid = message.get("id")
                if d.get("type") != "assistant" or not mid or not isinstance(message.get("usage"), dict):
                    continue
                if mid not in tours:
                    tours.append(mid)
                if mid != dernier_id:
                    dernier_id, stop = mid, None
                stop = message.get("stop_reason") or stop
                for b in blocs:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        appels[b.get("id")] = (len(tours), b.get("name") or "?")
                    elif b.get("type") == "text":
                        textes.setdefault(mid, []).append(b.get("text") or "")
    except (OSError, UnicodeDecodeError) as e:
        sortie.write("GARDE: transcription illisible : %s — %s\n" % (chemin, e))
        return 1
    par_outil = {}
    for _, nom in appels.values():
        par_outil[nom] = par_outil.get(nom, 0) + 1
    sortie.write("TOURS=%d\n" % len(tours))
    sortie.write("APPELS=%d — %s\n" % (len(appels), ", ".join("%s %d" % o for o in par_outil.items()) or "aucun"))
    sortie.write("AVERTISSEMENTS=%d\n" % len(avertis))
    par_tour = {}
    for a in avertis:
        tour = appels.get(a.get("toolUseID"), ("?", "?"))[0]
        par_tour[tour] = par_tour.get(tour, 0) + 1
    sortie.write("AVERTIS_PAR_TOUR=%s\n" % (",".join("%s:%d" % t for t in par_tour.items()) or "aucun"))
    if avertis:
        a = avertis[0]
        uid = a.get("toolUseID")
        tour, outil = appels.get(uid, ("?", "?"))
        is_error = erreurs_outil.get(uid)
        sortie.write("PREMIER_AVERTISSEMENT tour=%s outil=%s is_error=%s hook=%s\n" % (
            tour, outil, "?" if is_error is None else ("oui" if is_error else "non"), a.get("hookName")))
        texte = a.get("content")
        if isinstance(texte, list):
            texte = " ".join(str(t) for t in texte)
        sortie.write("TEXTE=%s\n" % " ".join(str(texte or "").split()))
    else:
        sortie.write("PREMIER_AVERTISSEMENT aucun\n")
    sortie.write("HOOK_ERREURS=%d pour %d appels\n" % (hook_erreurs, len(appels)))
    texte = "\n".join(textes.get(dernier_id, [])) if dernier_id else ""
    mots = texte.split()
    sortie.write("DERNIER mot=%s stop_reason=%s\n" % (mots[0] if mots else "", stop))
    non_vides = [l.strip() for l in texte.splitlines() if l.strip()]
    sortie.write("DERNIERE_LIGNE=%s\n" % (non_vides[-1] if non_vides else ""))
    return 0


# --- aperçu local (chantier LOC) --------------------------------------------

TYPES_APERCU = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml; charset=utf-8"}
LARGEUR_TELEPHONE = 375
PORT_APERCU = 8790      # le premier port qu'`apercu` essaie ; +1 tant qu'une autre entrée le prend
PAGE_SERVIE = re.compile(r"[\w.\- ]+(/[\w.\- ]+)*$")    # relatif ; `..` se rejette à part


def faire_serveur(dossier, port):
    """Le serveur de `servir`, lié à 127.0.0.1 (port 0 : un port libre) ; `serve_forever` le lance."""
    import functools
    import html
    import http.server
    import urllib.parse

    class Apercu(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, **TYPES_APERCU}

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            if url.path != "/_telephone":
                return super().do_GET()
            page = urllib.parse.parse_qs(url.query).get("page", [""])[0]
            if not PAGE_SERVIE.match(page) or ".." in page.split("/"):
                return self.send_error(400, "page=<page> : un chemin relatif au dossier servi")
            cadre = ('<!doctype html><html lang="fr"><meta charset="utf-8"><title>Téléphone</title>'
                     '<body style="margin:0;background:#f4ede4"><iframe src="/%s" title="%s" '
                     'style="display:block;margin:0 auto;border:0;width:%dpx;height:100vh"></iframe>'
                     % (html.escape(urllib.parse.quote(page)), html.escape(page), LARGEUR_TELEPHONE))
            corps = cadre.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

    return http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Apercu, directory=dossier))


def cmd_servir(dossier, port, sortie):
    if not os.path.isdir(dossier):
        sortie.write("GARDE: dossier introuvable : %s\n" % dossier)
        return 1
    try:
        serveur = faire_serveur(dossier, port)
    except (OSError, OverflowError) as e:
        sortie.write("GARDE: port %s inutilisable : %s\n" % (port, e))
        return 1
    sortie.write("SERVIR http://127.0.0.1:%d/ · %s\n" % (serveur.server_port, dossier))
    sortie.flush()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serveur.server_close()
    return 0


def lire_arg(x):
    """`@chemin` : le contenu du fichier, tel quel ; sinon le texte même."""
    if x.startswith("@"):
        with open(x[1:], encoding="utf-8", newline="") as f:
            return f.read()
    return x


def cmd_nuits_noter(texte, canal, arret, sortie, dossier=None, sorte=None):
    """Une ligne `note` (ou `stop`, avec `arret`) au carnet de nuit : `VLP_CARNET`, sinon celui du jour
    du dépôt de `dossier` (défaut : le dossier courant). Sans l'un ni l'autre : `GARDE:`, sort 1. `sorte` (une de
    `carnet.SORTES`) : ce que le matin fait de la note ; avec `arret`, `GARDE:` — un `stop` n'a pas de sorte."""
    if arret and sorte:
        print("GARDE: --sorte ne va pas avec --stop — un stop n'est pas une note du matin", file=sortie)
        return 1
    chemin = os.environ.get(carnet.ENV_CARNET) or carnet.du_jour(dossier or os.getcwd())
    if not chemin:
        print("GARDE: pas de dépôt Git ni de VLP_CARNET — pas de carnet de nuit où écrire", file=sortie)
        return 1
    canal = canal or os.environ.get(carnet.ENV_CANAL) or None
    if arret:
        carnet.stop(chemin, canal, texte)
    else:
        carnet.noter(chemin, canal, texte, sorte)
    print("NOTÉ %s" % chemin, file=sortie)
    return 0
