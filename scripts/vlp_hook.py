"""Le tampon « une fois » des hooks, sans rien d'autre (VIT8) : `hooks.json` lance chaque hook deux fois,
par `python3` et par `py` — partout l'un ou l'autre manque, ou les deux tournent. Le lanceur `vlp.py`
trie l'entrée ici, avant de charger `vlp_coeur` : le second lanceur sort en un import léger, au lieu
de charger tout le cœur pour se taire. Importé par le lanceur et par le cœur ; rien d'autre."""
import hashlib
import io
import os
import sys
import time


def dossier_temporaire():
    """Rendre le dossier de `tempfile.gettempdir()` sans importer `tempfile` (46 ms sous `-X importtime`, plus un
    fichier d'essai écrit, VIT8) quand `TMPDIR`, `TEMP` ou `TMP` le nomme : ses trois variables, dans son ordre
    (`_candidate_tempdir_list`, CPython 3.14). Un dossier nommé mais non inscriptible, que `tempfile` aurait
    sauté, rend le tampon impossible : `tampon_neuf` dit vrai, les deux lanceurs agissent."""
    for variable in ("TMPDIR", "TEMP", "TMP"):
        if os.environ.get(variable):
            return os.path.abspath(os.environ[variable])
    import tempfile
    return tempfile.gettempdir()


TAMPON = dossier_temporaire()

# Les formes exactes de `hooks.json` (`args` après le script), et le nom de la commande du cœur
# qu'elles appellent : le tampon porte ce nom, car `filet` et `hook` reçoivent la même entrée (PYT2).
HOOKS = {("hook",): "cmd_hook", ("filet",): "cmd_filet", ("gardien",): "cmd_gardien",
         ("vigile",): "cmd_vigile_hook", ("attente", "hook"): "cmd_attente_hook"}


class Triee(io.StringIO):
    """Une entrée de hook déjà passée par le tampon : `une_fois` du cœur ne la re-trie pas."""


def nom_tampon(texte, nom):
    """Rendre le nom du tampon d'une entrée de hook : `vlp-hook-<sha1 de nom + entrée>`."""
    return "vlp-hook-" + hashlib.sha1((nom + "\n" + texte).encode("utf-8")).hexdigest()


def menage(dossier, ages):
    """Retirer de `dossier` chaque fichier dont le nom commence par un préfixe de `ages` — des paires (préfixe, âge
    en secondes) — et plus vieux que cet âge (ARP4). Une `OSError` sur un fichier (pris par un autre processus,
    déjà retiré, dossier) passe au suivant ; un dossier illisible : rien."""
    try:
        noms = os.listdir(dossier)
    except OSError:
        return
    maintenant = time.time()
    for nom in noms:
        age = next((a for prefixe, a in ages if nom.startswith(prefixe)), None)
        if age is None:
            continue
        chemin = os.path.join(dossier, nom)
        try:
            if maintenant - os.path.getmtime(chemin) > age:
                os.unlink(chemin)
        except OSError:
            continue


def tampon_neuf(nom, dossier):
    """Vrai si `<dossier>/<nom>` se crée en exclusif — les deux lanceurs partent ensemble, un tampon
    daté les laisserait passer tous deux. Retire au passage (`menage`) les tampons `vlp-hook-` et `vlp-filet-`
    de plus de 60 s. `dossier` à `None` (tests) ou `VLP_SANS_TAMPON` non vide (rejeu à la main, SON) :
    toujours vrai ; une autre `OSError` : vrai — mieux vaut deux fois que zéro."""
    if dossier is None or os.environ.get("VLP_SANS_TAMPON"):
        return True
    menage(dossier, (("vlp-hook-", 60), ("vlp-filet-", 60)))
    try:
        os.close(os.open(os.path.join(dossier, nom), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return False
    except OSError:
        pass
    return True


def trier(argv, entree=None):
    """Lire l'entrée d'un hook de `hooks.json` et la trier : `None` si `argv` n'est pas une de ses
    formes (rien lu) ; sinon l'entrée en `Triee` si ce lancement est le premier à la traiter, ou `""`
    si un autre lanceur l'a déjà prise — l'appelant sort alors 0, muet."""
    nom = HOOKS.get(tuple(argv))
    if nom is None:
        return None
    texte = (entree or sys.stdin).read()
    return Triee(texte) if tampon_neuf(nom_tampon(texte, nom), TAMPON) else ""
