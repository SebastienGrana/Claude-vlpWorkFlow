"""Les sessions d'un chantier : essais, coût, découpe aux commits, compteur (REF45 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import datetime
import fnmatch
import glob
import json
import os
import re
import time

from noyau import etat
from noyau.facade import coeur
from noyau.commun import (SESSION, TITRE, chemin_garde, lignes_de)
from noyau.carte import (trouver)

__all__ = [
    "sessions_de",
    "sessions_entete",
    "essais_de",
    "registre_essais",
    "motif_sur",
    "declarations",
    "essais_declares",
    "cmd_essai",
    "MARQUE_DEPUIS",
    "NUIT_DOSSIER",
    "origine_de",
    "fenetres_du_chantier",
    "essais_hors_bac",
    "cmd_sessions",
    "cmd_cout",
    "lignes_a_clore",
    "bornes_du_cout",
    "TETE_SEGMENT",
    "INTERPRETE",
    "appel_python",
    "APPEL_CLORE",
    "lance_clore",
    "heure_clore",
    "totaux_a_clore",
    "decouper",
    "decoupe_et_heures",
    "totaux",
    "SORTES_OUTIL",
    "SUITES",
    "COMMANDES",
    "GARDE_FOUS",
    "NUMERO_READ",
    "CODE_SORTIE",
    "ENTETE_COMPTEUR",
    "TOTAUX_COUT",
    "seul_lance",
    "sorte_outil",
    "relances_de",
    "verdict_suite",
    "garde_fous",
    "lire_sortie",
    "mesure_vide",
    "ajouter_mesure",
    "compter_sorties",
    "compter_plage",
    "minutes_reparties",
    "texte_garde_fous",
    "ligne_compteur",
    "manques",
    "lire_journaux",
    "dixiemes",
    "ligne_recoupe",
    "recoupe",
    "rangs_compteur",
    "cmd_compteur",
]


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


def essais_de(session):
    """Les transcripts des essais `claude -p` de `session`, triés : ceux d'un bac de son scratchpad,
    `~/.claude/projects/<projet>-<session>-scratchpad-<bac>/<essai>.jsonl` (ESS1 : 39 dossiers de
    cette forme), et ceux que le registre déclare pour elle (`essais_declares`, MET2). Leurs
    sous-agents n'y sont pas ; [] sans dossier."""
    projets = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    motifs = ["*-" + glob.escape(session) + "-scratchpad-*"] + essais_declares(session)
    return sorted({e for m in motifs for e in glob.glob(os.path.join(projets, m, "*.jsonl"))})


def registre_essais():
    """Le registre des essais lancés hors d'un bac (MET2) : `~/.claude/vlp-essais.txt`, une ligne
    `<session> <motif>` par déclaration (`vlp.py essai`)."""
    return os.path.join(os.path.expanduser("~"), ".claude", "vlp-essais.txt")


def motif_sur(motif):
    """Vrai si `motif` nomme des dossiers de `~/.claude/projects/` sans en sortir : ni séparateur, ni
    `..`, ni blanc — le registre se lit en deux champs (MET2)."""
    return bool(motif) and not re.search(r"[\\/\s]|\.\.", motif)


def declarations():
    """Les paires (session, motif) du registre ; [] sans registre. Une ligne qui n'a pas deux
    champs, ou un motif qui sortirait du dossier, ne compte pas (`motif_sur`)."""
    if not os.path.isfile(registre_essais()):
        return []
    with open(registre_essais(), encoding="utf-8") as f:
        paires = [l.split() for l in f]
    return [(p[0], p[1]) for p in paires if len(p) == 2 and motif_sur(p[1])]


def essais_declares(session):
    """Les motifs de dossier de `~/.claude/projects/` que le registre déclare pour `session`
    (`declarations`)."""
    return [motif for s, motif in declarations() if s == session]


def cmd_essai(a, sortie):
    """Déclarer au registre un essai lancé hors d'un bac, une fois : `ESSAI <session> <motif> ·
    <n> dossier(s) · <m> transcript(s)` — 0 et 0 avant son lancement. La session : `--session`,
    sinon `CLAUDE_CODE_SESSION_ID` ; aucune, ou un motif refusé par `motif_sur` : `GARDE:`,
    rien d'écrit, sort 1 (MET2)."""
    session = a.session or os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not session or len(session.split()) != 1 or not motif_sur(a.motif):
        sortie.write("GARDE: essai non déclaré — session %r, motif %r : il faut une session (--session ou "
                     "CLAUDE_CODE_SESSION_ID) et un nom de dossier de ~/.claude/projects/, sans / ni \\ ni .. "
                     "ni blanc\n" % (session, a.motif))
        return 1
    if a.motif not in essais_declares(session):
        os.makedirs(os.path.dirname(registre_essais()), exist_ok=True)
        with open(registre_essais(), "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (session, a.motif))
    projets = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    sortie.write("ESSAI %s %s · %d dossier(s) · %d transcript(s)\n"
                 % (session, a.motif, len(glob.glob(os.path.join(projets, a.motif))),
                    len(glob.glob(os.path.join(projets, a.motif, "*.jsonl")))))
    return 0


# La marque `turnOrigin` de la première ligne `user` qui en porte une : "sdk" pour `claude -p`, "human" pour l'app ou
# le terminal, "peer" pour le message d'une autre séance. Interne, non documentée ; lue le 2026-10-12 sur 1 278
# transcripts : 148 "sdk", tous des `claude -p` — `entrypoint` ne la remplace pas, 100 d'entre eux, lancés depuis l'app,
# y portent `claude-desktop`. Vue d'abord le 2026-09-22 : avant, son absence ne dit rien (chantier ESH).
MARQUE_DEPUIS = datetime.datetime(2026, 9, 22, tzinfo=datetime.timezone.utc).timestamp()
NUIT_DOSSIER = "-claude-worktrees-nuit-"    # le dossier de transcripts d'un worktree `nuit-<date>-<canal>` (boucle.py)


def origine_de(chemin, jusqu_au_bout=False):
    """(marque `turnOrigin`, départ, fin) d'un transcript : la marque de la première ligne `user` qui en porte une, None
    sans ; l'heure UTC de sa première ligne horodatée, None sans. La lecture s'arrête dès les deux trouvés ; la fin —
    l'heure de la dernière ligne horodatée — ne se lit qu'avec `jusqu_au_bout`, None sinon. Illisible : trois None."""
    m, marque, debut, fin = coeur.mesure(), None, None, None
    try:
        with m.ouvrir(chemin) as f:
            for ligne in f:
                if debut is not None and not jusqu_au_bout and '"turnOrigin"' not in ligne:
                    continue
                try:
                    d = json.loads(ligne)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                t = m.heure(d)
                if t is not None:
                    debut, fin = (t if debut is None else debut), t
                if marque is None and d.get("type") == "user" and isinstance(d.get("turnOrigin"), str):
                    marque = d["turnOrigin"]
                if marque is not None and debut is not None and not jusqu_au_bout:
                    break
    except OSError:
        return None, None, None
    return marque, debut, fin if jusqu_au_bout else None


def fenetres_du_chantier(comptes, bornes):
    """([(début, fin, session)], marque vue, session récente) : la fenêtre de chaque session de `comptes` (sorte 0),
    de sa première à sa dernière ligne horodatée, coupée à `bornes` ; vrai si l'une porte une marque `turnOrigin`, vrai
    si l'une est partie après `MARQUE_DEPUIS`."""
    fenetres, marquee, recente = [], False, False
    for chemin, sorte in comptes:
        marque, debut, fin = origine_de(chemin, jusqu_au_bout=True) if sorte == 0 else (None, None, None)
        marquee = marquee or marque is not None
        if debut is None or fin is None:
            continue
        recente = recente or debut >= MARQUE_DEPUIS
        lo, hi = max(debut, bornes[0]), min(fin, bornes[1])
        if lo <= hi:
            fenetres.append((lo, hi, os.path.splitext(os.path.basename(chemin))[0]))
    return fenetres, marquee, recente


def essais_hors_bac(ids, bornes=None):
    """Les `GARDE:` d'un essai `claude -p` lancé hors d'un bac et pas déclaré (chantier ESH). Un transcript de
    `~/.claude/projects/*/` marqué "sdk" (`origine_de`), parti pendant une session de `ids` et dans `bornes` — la
    plage du chantier, en secondes UTC —, est un essai ; une ligne pour chacun que rien ne compte : ni transcript du
    chantier (`transcripts_du_fichier`), ni dossier d'un bac (`-scratchpad-`), ni dossier que le registre déclare
    (`declarations`), ni worktree de nuit (`NUIT_DOSSIER`). Elle dit la commande qui le déclare. Puis, si une session
    de `ids` est partie après `MARQUE_DEPUIS` et qu'aucun transcript vu ne porte de marque, une ligne qui le dit : le
    contrôle ne verrait plus rien. Le chiffre de `cout` n'en change pas. Sans `bornes` : rien ne coupe. Limite : la
    séance `claude -p` d'un autre chantier (`enchainer clear` hors nuit) dans la même plage se signale à tort ; aucune
    sur 1 278 transcripts, et écarter celles qui s'ouvrent par `/vlp:tache` cacherait 36 essais réels (2026-10-12)."""
    from decimal import ROUND_HALF_UP, Decimal
    m = coeur.mesure()
    comptes = coeur.transcripts_du_fichier([], ids, [])
    vus = {os.path.normcase(os.path.abspath(c)) for c, _ in comptes}
    fenetres, marquee, recente = fenetres_du_chantier(comptes, bornes or (-coeur.INFINI, coeur.INFINI))
    projets = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    motifs, plus_tot, gardes = [motif for _, motif in declarations()], min((f[0] for f in fenetres), default=coeur.INFINI), []
    for chemin in sorted(glob.glob(os.path.join(projets, "*", "*.jsonl"))):
        try:
            if os.path.normcase(os.path.abspath(chemin)) in vus or os.path.getmtime(chemin) < plus_tot:
                continue    # écrit pour la dernière fois avant la première fenêtre : parti avant elle
        except OSError:
            continue
        marque, debut, _ = origine_de(chemin)
        session = next((s for lo, hi, s in fenetres if debut is not None and lo <= debut <= hi), None)
        if session is None:
            continue
        marquee = marquee or marque is not None
        dossier = os.path.basename(os.path.dirname(chemin))
        if marque != "sdk" or "-scratchpad-" in dossier or NUIT_DOSSIER in dossier \
                or any(fnmatch.fnmatch(dossier, motif) for motif in motifs):
            continue
        r, erreur = m.mesurer(chemin)
        usd = None if erreur or r["usd_exact"] is None else r["usd_exact"].quantize(Decimal("0.01"), ROUND_HALF_UP)
        n = len(glob.glob(os.path.join(glob.escape(os.path.dirname(chemin)), "*.jsonl")))
        gardes.append("GARDE: essai claude -p hors bac, non déclaré : %s · parti le %s · %s · dossier %s%s — le "
                      "déclarer : vlp.py essai %s --session %s (ESH)"
                      % (os.path.splitext(os.path.basename(chemin))[0], time.strftime("%Y-%m-%d %H:%M", time.localtime(debut)),
                         "non mesuré (%s)" % erreur if erreur else coeur.ligne_cout(r["total"], r["tours"], usd), dossier,
                         " (%d transcripts : le motif les compte tous)" % n if n > 1 else "", dossier, session))
    if recente and not marquee:
        gardes.append("GARDE: aucune séance de la plage ne porte la marque turnOrigin — un essai claude -p hors bac n'y "
                      "serait pas vu (marque interne, non documentée ; ESH)")
    return gardes


def cmd_sessions(chemin, sortie):
    for s in sessions_de(lignes_de(chemin)):
        sortie.write(s + "\n")
    return 0


def cmd_cout(chemin, session, sortie, a_clore=False):
    """Le coût du fichier de fiches, coupé aux commits comme la page : une ligne par fiche
    (`ligne_parts`), puis hors fiches, puis `TOTAL`. Sans heures de commit, les tables
    brutes de `mesure-tokens.py` sur les sessions entières, sous une ligne qui dit pourquoi.
    `--session` met d'abord la table de la session courante, pour `/vlp:tache`. `a_clore` : deux
    lignes après `TOTAL`, `à clore` et `après clore` (chantier APC). Sans `tr` ni
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
            code = coeur.mesure().main([s]) or 0
        ids = [s] + [i for i in ids if i != s]
    elif not ids:
        sortie.write("SESSIONS 0 — pas de total\n")
        return 0
    decoupe, pourquoi, gardes, (fiches_, heures, fin) = decoupe_et_heures(chemin, lignes)
    for g in gardes:
        sortie.write(g + "\n")
    if not decoupe:
        sortie.write("DÉCOUPE aucune — %s : sessions entières, sous-agents compris\n" % pourquoi[0])
        with contextlib.redirect_stdout(sortie):
            code = coeur.mesure().main(ids) or code
        gardes, zero = [], (0, 0, 0, 0)
        essais = coeur.essais_entiers(ids, gardes)
        for g in gardes:
            sortie.write(g + "\n")
        if essais[1]:
            sortie.write(coeur.ligne_parts("essais", zero, zero, essais) + "\n")
        if a_clore:
            sortie.write("GARDE: --a-clore sans découpe — pas de ligne à clore\n")
        sortie.writelines(g + "\n" for g in essais_hors_bac(ids))
        return code
    parts, hors = decoupe
    sortie.write("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                 "un sous-agent compte à la fiche que nomme son prompt, sinon à son départ\n")
    for ident, *r in parts:
        sortie.write(coeur.ligne_parts(ident, *r) + "\n")
    sortie.write(coeur.ligne_parts("hors fiches", *hors) + "\n")
    sortie.write(coeur.ligne_parts("TOTAL (fiches + hors fiches)", *totaux(decoupe)) + "\n")
    if a_clore:
        sortie.writelines(l + "\n" for l in lignes_a_clore(chemin, lignes, decoupe))
    sortie.writelines(g + "\n" for g in essais_hors_bac(ids, bornes_du_cout(fiches_, heures, fin)))
    return code


def lignes_a_clore(chemin, lignes, decoupe):
    """Les lignes de `cout --a-clore` après `TOTAL` : `à clore` et `après clore`, ou la `GARDE:` d'une dernière plage
    hors fiches sans appel `vlp.py clore` (chantier APC)."""
    avant = totaux_a_clore(chemin, lignes)
    if avant is None:
        return ["GARDE: aucun appel « vlp.py clore » dans la dernière plage hors fiches — pas de ligne à clore"]
    return [coeur.ligne_parts("à clore", *avant),
            coeur.ligne_parts("après clore", *[(a[0] - b[0], a[1] - b[1], coeur.moins(a[2], b[2]), a[3] - b[3])
                                         for a, b in zip(totaux(decoupe), avant)])]


def bornes_du_cout(fiches_, heures, fin):
    """(début, fin) en secondes UTC de toutes les plages de `cout` — fiches et hors fiches —, ou None sans plage : ce
    que `essais_hors_bac` regarde (chantier ESH)."""
    par_fiche, trous = coeur.plages_du_cout(fiches_, heures, [], fin)
    bornes = [p for _, p in par_fiche] + trous
    return (min(b[0] for b in bornes), max(b[1] for b in bornes)) if bornes else None


# Un appel qui lance un script Python : en tête d'un segment (début, `;`, `&`, `|`, `(`, fin de ligne), après
# d'éventuels `X=y` ou `$x =`, un interprète Python (`py`, `python`, `python3`, chemin, `.exe` et
# guillemets permis), ses options, puis un chemin qui finit par le script (chantier ECA ; `compteur`, VIT17).
TETE_SEGMENT = r"""(?:^|[;&|(\n])[ \t]*(?:\w+=\S*[ \t]+)*(?:\$\w+[ \t]*=[ \t]*)?"""
INTERPRETE = (r"""(?:"(?:[^"\n]*[/\\])?(?:py|python3?)(?:\.exe)?"|'(?:[^'\n]*[/\\])?(?:py|python3?)(?:\.exe)?'"""
              r"""|(?:[^\s"';&|]*[/\\])?(?:py|python3?)(?:\.exe)?)(?:[ \t]+-(?:[XW][ \t]+)?\S+)*[ \t]+""")


def appel_python(script, suite=""):
    """Compiler le motif d'un appel qui lance `script` — une regex —, puis `suite` : `TETE_SEGMENT`, `INTERPRETE`,
    et un chemin, cité ou nu, qui finit par le script."""
    chemin = r"""(?:"[^"\n]*%s"|'[^'\n]*%s'|[^\s"';&|]*%s)""" % ((script,) * 3)
    return re.compile(TETE_SEGMENT + INTERPRETE + chemin + suite, re.M)


APPEL_CLORE = appel_python(r"vlp\.py", r"[ \t]+clore\b")    # un appel qui lance `clore`


def lance_clore(commande):
    """Vrai si la commande lance `vlp.py clore` (`APPEL_CLORE`), le corps des heredocs qui ne font
    qu'écrire un fichier tu (`sans_heredoc`) : un texte qui cite l'appel — la ligne de bilan qu'un
    `echo` ou un `cat <<EOF` écrit, un `git commit -m`, un `--resultat` — n'en est pas un (chantier ECA)."""
    return bool(APPEL_CLORE.search(coeur.sans_heredoc(commande)))


def heure_clore(chemin, lignes):
    """L'heure, en secondes UTC, du dernier `tool_use` dont la commande lance `vlp.py clore`
    (`lance_clore`), dans les sessions du fichier et dans sa dernière plage hors fiches — celle
    que le commit de clôture ferme ; None sans lui. Ce que `clore` a vu en inscrivant son chiffre
    (chantier APC)."""
    fiches_ = coeur.fiches_du_fichier(lignes)
    heures = coeur.heures_commits(chemin, [f[0] for f in fiches_], [], any(l.startswith("**CLOS**") for l in lignes),
                             {f[0]: f[1] for f in fiches_})
    trous = coeur.plages(fiches_, heures, [], clos=True)[1] if heures else []
    if not trous:
        return None
    debut, fin = trous[-1]
    m, vu, sessions = coeur.mesure(), None, []
    for groupe in [f[3] for f in fiches_] + [sessions_entete(lignes)]:
        sessions += [s for s in groupe if s not in sessions]
    for s in sessions:
        transcript, erreur = m.resoudre(s)
        if erreur:
            continue
        with m.ouvrir(transcript) as f:
            for ligne in f:
                if "clore" not in ligne:
                    continue
                try:
                    d = json.loads(ligne)
                except ValueError:
                    continue
                contenu = (d.get("message") or {}).get("content") if isinstance(d, dict) else None
                appel = isinstance(contenu, list) and any(
                    isinstance(c, dict) and c.get("type") == "tool_use"
                    and lance_clore(str((c.get("input") or {}).get("command", ""))) for c in contenu)
                t = m.heure(d) if appel else None
                if t is not None and debut < t <= fin:
                    vu = t if vu is None else max(vu, t)
    return vu


def totaux_a_clore(chemin, lignes):
    """Les `totaux` de la découpe dont la dernière plage hors fiches s'arrête à `heure_clore`, ou
    None sans appel `clore` : le calcul de `cout --a-clore` et de `recompter --a-clore`."""
    t = heure_clore(chemin, lignes)
    return None if t is None else totaux(decouper(chemin, lignes, t)[0])


def decouper(chemin, lignes=None, fin=None):
    """(découpe, pourquoi, gardes) d'un fichier de fiches : `parts_aux_commits` sur les heures de
    `heures_commits`, ou None — `pourquoi` dit alors la raison. `cout` l'imprime, `recompter` en
    tire le total (`totaux`) : une découpe, deux lecteurs. `fin` : voir `parts_aux_commits`. Un
    fichier clos s'arrête, sans `fin`, au dernier appel `clore` (`heure_clore`), où `clore` a pris
    son chiffre : ce qui le suit — republications, commit — sort du coût (chantier APC, choix b)."""
    return decoupe_et_heures(chemin, lignes, fin)[:3]


def decoupe_et_heures(chemin, lignes=None, fin=None):
    """Rendre (découpe, pourquoi, gardes, (fiches, heures, fin)) : `decouper`, puis ce qu'elle a lu pour couper — les
    fiches, les heures de commit et la fin du coût —, que `compteur` reprend sans relancer Git (VIT17)."""
    lignes = lignes_de(chemin) if lignes is None else lignes
    fiches_ = coeur.fiches_du_fichier(lignes)
    pourquoi, gardes = [], []
    clos = any(l.startswith("**CLOS**") for l in lignes)
    heures = coeur.heures_commits(chemin, [f[0] for f in fiches_], pourquoi, clos, {f[0]: f[1] for f in fiches_})
    if fin is None and clos and heures:
        fin = heure_clore(chemin, lignes)
    decoupe = heures and coeur.parts_aux_commits(fiches_, heures, gardes, sessions_entete(lignes), fin)
    if not decoupe and heures:
        pourquoi.append("aucune session de fiche mesurée")
    return decoupe or None, pourquoi, gardes, (fiches_, heures, fin)


def totaux(decoupe):
    """(session, sous-agents, essais) d'une découpe, fiches et hors fiches sommées : la ligne
    `TOTAL` de `cout`, dont `plus(*totaux(d))[0]` est le nombre."""
    parts, hors = decoupe
    return tuple(coeur.plus(*[p[k + 1] for p in parts], hors[k]) for k in range(3))


# Ce que `compteur` lit d'une sortie d'outil (VIT17). La sorte de son appel : la suite entière, `--seul`,
# `test-boucle`, le mutant, pyright, Git, la publication — l'outil Artifact —, et le reste. Une commande Bash ou
# PowerShell se reconnaît à ce qu'elle lance en tête d'un segment, le corps des heredocs tu (`sans_heredoc`) :
# `mutant` d'abord, son `--test` cite la suite ; un script de mesure qui lance la suite par `subprocess` est du reste.
# Les garde-fous sont des débuts de ligne, chacun lu là seulement où il dit vrai — le même ordre que `GARDE_FOUS` :
# `ÉCART:` dans la sortie d'une suite (ceux d'un mutant sont à lui), `MUTANT ATTRAPÉ` dans celle d'un mutant, `GARDE:`
# dans celle d'un Bash ou d'un PowerShell, le verdict du relecteur au retour d'un `Agent` ou dans le message d'une
# autre session. Une sortie relue — la boucle qui attend une tâche de fond, puis un `Read` du même fichier — compte
# chaque fois.
SORTES_OUTIL = ("suite", "--seul", "test-boucle", "mutant", "pyright", "Git", "publication", "relance", "reste")
SUITES = SORTES_OUTIL[:3]
COMMANDES = (("mutant", appel_python(r"vlp\.py", r"[ \t]+mutant\b")), ("suite", appel_python(r"test-vlp\.py")),
             ("test-boucle", appel_python(r"test-boucle\.py")),
             ("pyright", re.compile(TETE_SEGMENT + r"pyright\b", re.M)),
             ("Git", re.compile(TETE_SEGMENT + r"git\b", re.M)))
GARDE_FOUS = ("ÉCART:", "MUTANT ATTRAPÉ", "GARDE:", "ACCEPTÉE", "REFUSÉE")
NUMERO_READ = re.compile(r"^\s*\d+(?:\t|→)")      # le numéro qu'un `Read` met devant chaque ligne
CODE_SORTIE = re.compile(r"\(exit code (\d+)\)")   # dans la notification d'une tâche de fond finie
ENTETE_COMPTEUR = ("COMPTEUR aux commits de fiche, en minutes — une fiche va du commit d'avant au sien ; actif : "
                   "les écarts entre lignes voisines, sessions et sous-agents (sans les essais), sans les pauses de "
                   "plus de %d min, chacun à la part de la ligne qui le ferme ; outils : minutes (appels) ; tours et "
                   "$ : ceux de cout ; suites : vertes sur celles dont la sortie dit le verdict")
TOTAUX_COUT = (("outils", "totalToolDuration"), ("modèle", "totalAPIDuration"), ("durée", "totalDuration"))


def seul_lance(commande, trouve):
    """Vrai si l'appel de la suite trouvé dans la commande porte `--seul` avant la fin de son segment."""
    segment = re.split(r"[\n;&|]", commande[trouve.end():], maxsplit=1)[0]
    return re.search(r"(?<!\S)--seul\b", segment) is not None


def sorte_outil(appel, relances=()):
    """Rendre la sorte d'un appel (nom, entrée) parmi `SORTES_OUTIL` : l'outil Artifact est la publication ; une
    commande Bash ou PowerShell, ce qu'elle lance (`COMMANDES`) — la suite avec `--seul`, « --seul » —, puis
    « relance » si elle porte une des commandes longues que le projet déclare (`relances_de`, RLA) ; le reste
    sinon."""
    nom, entree = appel
    if nom == "Artifact":
        return "publication"
    if nom not in ("Bash", "PowerShell"):
        return "reste"
    commande = coeur.sans_heredoc(str(entree.get("command", "")))
    for sorte, motif in COMMANDES:
        trouve = motif.search(commande)
        if trouve:
            return "--seul" if sorte == "suite" and seul_lance(commande, trouve) else sorte
    return "relance" if any(r in commande for r in relances) else "reste"


def relances_de(fichier):
    """Rendre les commandes longues que déclare le `CHANTIER.md` au-dessus d'un fichier de fiches : la ligne
    `- **commandes longues** :`, chaque motif entre accents graves (RLA) ; le projet les écrit, jamais le kit. Pas de
    carte, ni de ligne : aucune."""
    racine = trouver(os.path.dirname(os.path.abspath(fichier)))
    if racine is None:
        return ()
    valeur = coeur.champ(lignes_de(os.path.join(racine, "CHANTIER.md")), "commandes longues", "")
    return tuple(m for m in re.findall(r"`([^`\n]+)`", valeur) if m.strip())


def verdict_suite(texte, lien):
    """Rendre le verdict d'une sortie de suite : vrai si verte, faux si rouge, None s'il ne s'y lit pas — sortie
    écrite ailleurs, ou suite lancée en fond. L'attente d'une tâche de fond n'en dit pas : sa notification le dit, par
    son code de sortie ; au premier plan, un `ÉCART:` ou un `FIN:` la disent rouge, sinon une ligne `OK` verte."""
    if lien == "fond":
        code = CODE_SORTIE.search(texte)
        return None if code is None else code.group(1) == "0"
    if lien:
        return None
    lignes = texte.splitlines()
    if any(l.startswith(("ÉCART:", "FIN:")) for l in lignes):
        return False
    return True if any(l.strip() == "OK" for l in lignes) else None


def garde_fous(texte):
    """Compter les lignes d'une sortie qui s'ouvrent par chaque garde-fou de `GARDE_FOUS`, le numéro de ligne d'un
    `Read` ôté."""
    if not any(g in texte for g in GARDE_FOUS):
        return (0,) * len(GARDE_FOUS)
    debuts = [NUMERO_READ.sub("", l, count=1).lstrip() for l in texte.splitlines()]
    return tuple(sum(d.startswith(g) for d in debuts) for g in GARDE_FOUS)


def lire_sortie(appel, texte, lien, relances=()):
    """Rendre ce que `compteur` garde d'une sortie, lue au fil du transcript, sans son texte : (sorte d'outil — None
    pour le message d'une autre session —, 1 si elle compte un appel — 0 pour une notification ou l'attente d'une
    tâche de fond (`lien`) —, verdict de suite — None hors suite, ou s'il ne s'y lit pas —, garde-fous, chacun lu là
    où il dit vrai, puis vrai pour une notification : ce qu'elle ferme n'est pas un appel d'outil, mais l'attente de
    la tâche) ; `relances` : les commandes longues du projet (`sorte_outil`)."""
    sorte, nom = (None, None) if appel is None else (sorte_outil(appel, relances), appel[0])
    releve = nom in (None, "Agent")
    ou = (sorte in SUITES, sorte == "mutant", nom in ("Bash", "PowerShell"), releve, releve)
    vus = tuple(n if lu else 0 for n, lu in zip(garde_fous(texte), ou))
    verte = verdict_suite(texte, lien) if sorte in SUITES else None
    return sorte, int(appel is not None and not lien), verte, vus, lien.startswith("fond")


def mesure_vide():
    """Rendre la mesure d'une plage à zéro : secondes par part, pauses, durée, secondes et appels par sorte d'outil,
    secondes d'outil fermées par une notification, suites [jugées, vertes], garde-fous."""
    return {"parts": dict.fromkeys(coeur.mesure().PARTS, 0.0), "pauses": 0, "duree": 0.0,
            "outils": dict.fromkeys(SORTES_OUTIL, 0.0), "appels": dict.fromkeys(SORTES_OUTIL, 0), "fond": 0.0,
            "suites": [0, 0], "garde_fous": [0] * len(GARDE_FOUS)}


def ajouter_mesure(somme, mesure_):
    """Ajouter une mesure à une autre, en place ; la durée reste None dès qu'une manque."""
    for cle in ("parts", "outils", "appels"):
        for k, v in mesure_[cle].items():
            somme[cle][k] += v
    somme["pauses"] += mesure_["pauses"]
    somme["fond"] += mesure_["fond"]
    somme["duree"] = None if somme["duree"] is None or mesure_["duree"] is None else somme["duree"] + mesure_["duree"]
    somme["suites"] = [x + y for x, y in zip(somme["suites"], mesure_["suites"])]
    somme["garde_fous"] = [x + y for x, y in zip(somme["garde_fous"], mesure_["garde_fous"])]


def compter_sorties(rendu, evenements):
    """Ajouter à la mesure `rendu` ce que disent les sorties d'une plage : les appels par sorte d'outil, les suites
    jouées et vertes, les garde-fous."""
    m = coeur.mesure()
    for _, part, lu in evenements:
        if lu is None:
            continue
        sorte, appel, verte, vus, _ = lu
        if part == m.OUTILS:
            rendu["appels"][sorte] += appel
        if verte is not None:
            rendu["suites"] = [rendu["suites"][0] + 1, rendu["suites"][1] + verte]
        rendu["garde_fous"] = [x + y for x, y in zip(rendu["garde_fous"], vus)]


def compter_plage(journaux, plage):
    """Rendre la mesure d'une plage (début, fin] : les événements de chaque journal (`tranche`) sur une ligne de temps
    commune, découpés en parts (`parts`) — l'actif de `--actif` sur les mêmes transcripts ; la durée, de borne à borne,
    None si l'une est ouverte ; le temps d'outil par sorte, et sa part fermée par une notification ; puis ce que
    disent les sorties (`compter_sorties`)."""
    m = coeur.mesure()
    rendu = mesure_vide()
    evenements = [e for chemin, j in journaux for e in m.tranche(chemin, j.evenements, plage)]
    rendu["parts"], fermes, rendu["pauses"] = m.parts(evenements)
    rendu["duree"] = plage[1] - plage[0] if -coeur.INFINI < plage[0] and plage[1] < coeur.INFINI else None
    for secondes, part, lu in fermes:
        if part == m.OUTILS:
            rendu["outils"][lu[0] if lu else "reste"] += secondes
            rendu["fond"] += secondes if lu and lu[4] else 0.0
    compter_sorties(rendu, evenements)
    return rendu


def minutes_reparties(secondes, total=None):
    """Rendre les minutes de chaque nombre de secondes, arrondies pour sommer `total` — par défaut l'arrondi de leur
    somme (`minutes`) : chacun prend ses minutes entières, puis les plus gros restes une de plus."""
    total = coeur.mesure().minutes(sum(secondes)) if total is None else total
    entieres = [int(s // 60) for s in secondes]
    ordre = sorted(range(len(secondes)), key=lambda i: secondes[i] / 60 - entieres[i], reverse=True)
    for i in ordre[:max(0, total - sum(entieres))]:
        entieres[i] += 1
    return entieres


def texte_garde_fous(mesure_):
    """Écrire les garde-fous d'une mesure : suites vertes sur jugées (`verdict_suite`), puis le compte de chaque
    garde-fou — un tiret pour aucun —, le verdict du relecteur en ACCEPTÉE et REFUSÉE."""
    jouees, vertes = mesure_["suites"]
    ecart, attrape, garde, acceptee, refusee = mesure_["garde_fous"]
    return "suites %s, ÉCART %s, MUTANT ATTRAPÉ %s, GARDE %s, relecteur %s" % (
        "%d/%d" % (vertes, jouees) if jouees else "-", ecart or "-", attrape or "-", garde or "-",
        "%d ACCEPTÉE + %d REFUSÉE" % (acceptee, refusee) if acceptee or refusee else "-")


def ligne_compteur(nom, mesure_, cout):
    """Écrire la ligne de `compteur` d'une plage : durée, actif réparti en parts, outils par sorte, les tours et le
    prix de `cout`, puis les garde-fous ; les minutes de chaque part et de chaque sorte somment leur total à la minute
    (`minutes_reparties`)."""
    m = coeur.mesure()
    actif = minutes_reparties([mesure_["parts"][p] for p in m.PARTS])
    outils = minutes_reparties([mesure_["outils"][s] for s in SORTES_OUTIL], actif[m.PARTS.index(m.OUTILS)])
    duree = "-" if mesure_["duree"] is None else "%d" % m.minutes(mesure_["duree"])
    return "%s · durée %s · actif %d = %s · outils : %s · %d tours · %s · garde-fous : %s" % (
        nom, duree, sum(actif), " + ".join("%s %d" % (p, n) for p, n in zip(m.PARTS, actif)),
        ", ".join("%s %d (%d)" % (s, n, mesure_["appels"][s]) for s, n in zip(SORTES_OUTIL, outils)),
        cout[1], coeur.dollars(cout[2]), texte_garde_fous(mesure_))


def manques(journaux):
    """Rendre les lignes `AVERTISSEMENT:` de ce qui manque aux transcripts lus — leur format est interne à Claude Code
    et change d'une version à l'autre : un champ absent se dit, jamais en silence. Les lignes de message sans heure,
    hors du temps ; les sorties dont l'appel n'est pas au transcript, rangées au reste ; une session sans `origin`, où
    rien ne se lit tapé : son attente tombe au reste."""
    rendu = []
    for chemin, j in journaux:
        nom = os.path.basename(chemin)
        if j.sans_heure:
            rendu.append("AVERTISSEMENT: %s : %d ligne(s) de message sans heure, hors du temps" % (nom, j.sans_heure))
        if j.sans_appel:
            rendu.append("AVERTISSEMENT: %s : %d sortie(s) sans appel connu, rangée(s) au reste" % (nom, j.sans_appel))
        if j.users and not j.origines:
            rendu.append("AVERTISSEMENT: %s : %d ligne(s) user, aucune avec origin — l'attente tombe au reste"
                         % (nom, j.users))
    return rendu


def lire_journaux(chemins, sortie, relances=()):
    """Rendre [(chemin, journal)] des transcripts lisibles, chaque sortie lue au fil (`lire_sortie`, avec les
    commandes longues du projet) ; un illisible se dit, puis ce qui manque aux autres (`manques`)."""
    m = coeur.mesure()
    rendu = []

    def lire(appel, texte, lien):
        """`lire_sortie` avec les commandes longues du projet : `journal` n'en passe que trois."""
        return lire_sortie(appel, texte, lien, relances)

    for chemin in chemins:
        j, erreur = m.journal(chemin, lire)
        if erreur:
            sortie.write("AVERTISSEMENT: transcript non lu : %s — %s\n" % (chemin, erreur))
            continue
        rendu.append((chemin, j))
    for ligne in manques(rendu):
        sortie.write(ligne + "\n")
    return rendu


def dixiemes(secondes, signe=False):
    """Écrire des secondes en minutes à une décimale, à la virgule — signées si `signe` : un écart."""
    return (("%+.1f" if signe else "%.1f") % (secondes / 60)).replace(".", ",")


def ligne_recoupe(tete, avant, etat, siens):
    """Écrire la ligne de recoupe d'une `cost-state` : les outils, le modèle et la durée du compteur, du `startTime` à
    `avant` — la dernière ligne horodatée avant elle —, face à ses totaux, l'écart signé — pour les outils, aussi sans
    ce que ferme une notification : l'attente d'une tâche de fond n'est pas un appel d'outil ; un champ absent se
    dit."""
    m = coeur.mesure()
    debut = etat.get("startTime")
    if not isinstance(debut, (int, float)) or avant is None:
        return "%s · pas de plage — %s" % (tete, "aucune ligne horodatée avant" if avant is None else "startTime absent")
    mesure_ = compter_plage(siens, (debut / 1000, avant))
    nous = {"outils": mesure_["parts"][m.OUTILS], "modèle": mesure_["parts"][m.MODELE], "durée": avant - debut / 1000}
    morceaux = []
    for cle, champ in TOTAUX_COUT:
        eux = etat.get(champ)
        if not isinstance(eux, (int, float)):
            morceaux.append("%s %s contre %s absent" % (cle, dixiemes(nous[cle]), champ))
            continue
        ecart = "écart %s" % dixiemes(nous[cle] - eux / 1000, True)
        if cle == "outils":
            ecart += " ; sans les %s fermées par une notification de fond : %s" % (
                dixiemes(mesure_["fond"]), dixiemes(nous[cle] - mesure_["fond"] - eux / 1000, True))
        morceaux.append("%s %s contre %s %s (%s)" % (cle, dixiemes(nous[cle]), champ, dixiemes(eux / 1000), ecart))
    return "%s · %s" % (tete, " · ".join(morceaux))


def recoupe(journaux, chemin, sortie):
    """Écrire une ligne par `cost-state` d'une session (`etats_cout`), recoupée sur sa plage, session et sous-agents
    (`ligne_recoupe`)."""
    m = coeur.mesure()
    etats, erreur = m.etats_cout(chemin)
    if erreur:
        sortie.write("AVERTISSEMENT: recoupe : %s — %s\n" % (chemin, erreur))
        return
    agents = set(m.sous_agents(chemin))
    siens = [(c, j) for c, j in journaux if c == chemin or c in agents]
    for n, avant, etat in etats:
        tete = "RECOUPE %s ligne %d (minutes)" % (os.path.basename(chemin), n)
        sortie.write(ligne_recoupe(tete, avant, etat, siens) + "\n")
    if not etats:
        sortie.write("RECOUPE %s · aucune ligne cost-state\n" % os.path.basename(chemin))


def rangs_compteur(nommees, plages_, decoupe, sortie):
    """Rendre [(nom, plages, coût)] des lignes de `compteur` : une par fiche — les seules nommées, si on en nomme —,
    puis hors fiches quand on n'en nomme pas ; une fiche nommée sans plage se dit en `GARDE:`."""
    (par_fiche, trous), (parts_, hors) = plages_, decoupe
    connues = [ident for ident, _ in par_fiche]
    for ident in nommees:
        if ident not in connues:
            sortie.write("GARDE: fiche sans plage : %s — ni commit « %s : », ni session\n" % (ident, ident))
    rangs = [(ident, [plage], coeur.plus(*r)) for (ident, plage), (_, *r) in zip(par_fiche, parts_)
             if not nommees or ident in nommees]
    return rangs if nommees else rangs + [("hors fiches", trous, coeur.plus(*hors))]


def cmd_compteur(a, sortie):
    """Dire où passe le temps de chaque fiche, coupée aux commits comme `cout` (VIT17) : l'en-tête, une ligne par fiche
    (`ligne_compteur`), hors fiches et `TOTAL` — seulement les fiches nommées, si on en nomme ; `--recoupe` : puis une
    ligne par `cost-state` des sessions (`recoupe`). Sans découpe, une `GARDE:` et 1 ; une fiche nommée sans plage : 1."""
    lignes = lignes_de(chemin_garde(a.fichier))
    decoupe, pourquoi, gardes, (fiches_, heures, fin) = decoupe_et_heures(a.fichier, lignes)
    for g in gardes:
        sortie.write(g + "\n")
    if not decoupe:
        sortie.write("GARDE: pas de découpe — %s\n" % pourquoi[0])
        return 1
    fichiers = coeur.transcripts_du_fichier(fiches_, sessions_entete(lignes), [])
    journaux = lire_journaux([c for c, sorte in fichiers if sorte < 2], sortie, relances_de(a.fichier))
    sortie.write(ENTETE_COMPTEUR % (coeur.mesure().PAUSE // 60) + "\n")
    rangs = rangs_compteur(a.fiches, coeur.plages_du_cout(fiches_, heures, [], fin), decoupe, sortie)
    total = mesure_vide()
    for nom, bornes, cout in rangs:
        mesure_ = mesure_vide()
        for plage in bornes:
            ajouter_mesure(mesure_, compter_plage(journaux, plage))
        sortie.write(ligne_compteur(nom, mesure_, cout) + "\n")
        ajouter_mesure(total, mesure_)
    nom = "TOTAL (fiches nommées)" if a.fiches else "TOTAL (fiches + hors fiches)"
    sortie.write(ligne_compteur(nom, total, coeur.plus(*[r[2] for r in rangs])) + "\n")
    for chemin in [c for c, sorte in fichiers if sorte == 0] if a.recoupe else []:
        recoupe(journaux, chemin, sortie)
    return int(len(rangs) < len(set(a.fiches)))
