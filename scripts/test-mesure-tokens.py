#!/usr/bin/env python3
"""Teste mesure-tokens.py sans fixture sur disque.

Écrit des jsonl synthétiques dans un dossier temporaire, appelle `mesurer`,
`resoudre`, `sous_agents` et `main`, compare. Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import contextlib
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from decimal import ROUND_HALF_UP, Decimal

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mesure_tokens", os.path.join(ICI, "mesure-tokens.py"))
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mesurer = mod.mesurer


def outil(nom):
    return {"type": "tool_use", "id": "toolu_" + nom, "name": nom, "input": {}}


def assistant(mid, entree, sortie, creation, lecture, sous_objet=None, blocs=None, modele="test", vitesse=None,
              heure=None):
    """Une ligne `assistant`. `sous_objet` : (1h, 5m), ou None pour un usage
    sans `cache_creation` (vieux transcript). `blocs` : le contenu, un bloc
    texte par défaut. `heure` : son `timestamp`, aucun par défaut."""
    usage = {
        "input_tokens": entree,
        "output_tokens": sortie,
        "cache_creation_input_tokens": creation,
        "cache_read_input_tokens": lecture,
    }
    if sous_objet is not None:
        h1, m5 = sous_objet
        usage["cache_creation"] = {"ephemeral_1h_input_tokens": h1, "ephemeral_5m_input_tokens": m5}
    if vitesse is not None:
        usage["speed"] = vitesse
    ligne = {
        "type": "assistant",
        "requestId": "req_" + mid,
        "message": {"id": mid, "model": modele, "usage": usage,
                    "content": blocs if blocs is not None else [{"type": "text", "text": "texte"}]},
    }
    if heure is not None:
        ligne["timestamp"] = heure
    return json.dumps(ligne)


# Trois tours : A sur trois lignes (mêmes comptes, deux outils de noms
# différents), B sur une ligne sans sous-objet cache_creation, C sur une ligne
# avec un outil. Plus une ligne sans usage, une ligne invalide, une ligne vide.
LIGNES = [
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40)),
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40), blocs=[outil("Bash")]),
    json.dumps({"type": "user", "message": {"role": "user", "content": "sans usage"}}),
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40), blocs=[outil("Edit")]),
    "{ceci n'est pas du json",
    "",
    assistant("msg_B", 20, 7, 200, 2000),
    assistant("msg_C", 30, 9, 300, 3000, sous_objet=(300, 0), blocs=[outil("Bash")]),
]

ATTENDU = {
    "tours": 3,
    "appels": 3,
    "outils": {"Bash": 2, "Edit": 1},
    "ctx_1er": 10 + 100 + 1000,       # tour A
    "ctx_dernier": 30 + 300 + 3000,   # tour C
    "input": 10 + 20 + 30,
    "output": 5 + 7 + 9,
    "cache_creation": 100 + 200 + 300,
    "cache_1h": 60 + 0 + 300,
    "cache_read": 1000 + 2000 + 3000,
    "total": 60 + 21 + 600 + 6000,
    "invalides": 1,
    "divergents": 0,
}

# Un tour dont les comptes changent entre ses deux lignes : la dernière gagne,
# et l'id est compté divergent.
LIGNES_DIVERGENT = [
    assistant("msg_D", 1, 5, 10, 100),
    assistant("msg_D", 1, 6, 10, 100),
]
ATTENDU_DIVERGENT = {"tours": 1, "output": 6, "divergents": 1, "appels": 0}

# Pondération : un tour dont les quatre comptes valent 1 000, modèle connu,
# cache écrit réparti 400 en 1 h et 600 en 5 min. Attendus calculés ici depuis
# la même grille que le script — le test vérifie la formule, pas les prix.
MODELE = "claude-opus-5"
p_entree, p_sortie, p_lu, p_5m, p_1h = mod.GRILLE[MODELE]
EQUIV = 1000 + 1000 * p_sortie / p_entree + 1000 * p_lu / p_entree + 600 * p_5m / p_entree + 400 * p_1h / p_entree
USD = (1000 * p_entree + 1000 * p_sortie + 1000 * p_lu + 600 * p_5m + 400 * p_1h) / Decimal(1_000_000)
LIGNES_POIDS = [
    assistant("msg_E", 1000, 1000, 1000, 1000, sous_objet=(400, 600), modele=MODELE),
    # Un tour <synthetic> à comptes nuls ne coûte rien et ne rend rien inconnu.
    assistant("msg_S", 0, 0, 0, 0, modele="<synthetic>"),
]
ATTENDU_POIDS = {
    "tours": 2,
    "equiv": int(EQUIV.quantize(Decimal(1), rounding=ROUND_HALF_UP)),
    "usd": str(USD.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
    "inconnus": [],
}

# Un modèle absent de la grille, et un tour fast : usd vaut « ? », equiv aussi
# (les ratios de la grille ne sont pas communs à tous les modèles).
LIGNES_INCONNU = [
    assistant("msg_F", 1000, 1000, 1000, 1000, modele=MODELE),
    assistant("msg_G", 10, 10, 10, 10, modele="modele-inconnu"),
    assistant("msg_H", 10, 10, 10, 10, modele=MODELE, vitesse="fast"),
]
ATTENDU_INCONNU = {
    "tours": 3,
    "equiv": "?" if mod.RATIOS_COMMUNS is None else None,
    "usd": "?",
    "inconnus": ["claude-opus-5 (fast)", "modele-inconnu"],
}

# claude-opus-5-5 est dans la grille depuis le 2026-09-23 : son usd se chiffre. Un million de
# chaque compte, cache écrit 400 000 en 1 h et 600 000 en 5 min, aux prix de la page officielle :
# 4 + 20 + 0,20 + 0,6 × 5 + 0,4 × 8 = 30,40 $.
LIGNES_OPUS55 = [assistant("msg_O", 10**6, 10**6, 10**6, 10**6, sous_objet=(400_000, 600_000),
                           modele="claude-opus-5-5")]
ATTENDU_OPUS55 = {"tours": 1, "usd": "30.40", "inconnus": []}

# Les heures des plages : des minutes autour du 2026-09-23 à 10:00 UTC, écrites comme dans un
# transcript (`iso`) ou comme une borne de plage (`sec`).
ORIGINE = datetime.datetime(2026, 9, 23, 10, 0, tzinfo=datetime.timezone.utc)


def iso(minutes):
    return (ORIGINE + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def sec(minutes):
    return (ORIGINE + datetime.timedelta(minutes=minutes)).timestamp()


# Une session coupée à 10:15. A est à 10:00 ; B a deux lignes, 10:10 et 10:16, et se juge à
# la première ; C est à 10:20 ; D n'a pas d'heure : il compte des deux côtés, et se signale.
LIGNES_PLAGE = [
    json.dumps({"type": "user", "timestamp": iso(-1), "message": {"role": "user", "content": "go"}}),
    assistant("msg_PA", 1, 1, 0, 0, heure=iso(0), blocs=[outil("Bash")]),
    assistant("msg_PB", 10, 10, 0, 0, heure=iso(10)),
    assistant("msg_PB", 10, 10, 0, 0, heure=iso(16), blocs=[outil("Edit")]),
    assistant("msg_PC", 100, 100, 0, 0, heure=iso(20)),
    assistant("msg_PD", 1000, 1000, 0, 0),
]
# Un sous-agent parti à 09:55 (sa première ligne horodatée, un `user`) et fini à 10:20 :
# entier dans la plage de son départ, absent de la suivante.
LIGNES_SOUS_AGENT = [
    json.dumps({"type": "user", "timestamp": iso(-5), "message": {"role": "user", "content": "fiche"}}),
    assistant("msg_SA1", 1, 1, 0, 0, heure=iso(5)),
    assistant("msg_SA2", 10, 10, 0, 0, heure=iso(20), blocs=[outil("Read")]),
]
# (nom, lignes, attendu, plage, sous-agent ?). Avant 10:15 : A, B, D (2 + 20 + 2 000) ; après :
# C, D (200 + 2 000). Bornes (10:00, 10:20] : A n'y est pas, C y est.
CAS_PLAGE = [
    ("sans-plage", LIGNES_PLAGE, {"tours": 4, "total": 2222, "appels": 2, "sans_heure": 0}),
    ("plage-avant", LIGNES_PLAGE, {"tours": 3, "total": 2022, "appels": 2, "sans_heure": 1}, (sec(-60), sec(15))),
    ("plage-apres", LIGNES_PLAGE, {"tours": 2, "total": 2200, "appels": 0, "sans_heure": 1}, (sec(15), sec(60))),
    ("plage-bornes", LIGNES_PLAGE, {"tours": 3, "total": 2220, "sans_heure": 1}, (sec(0), sec(20))),
    ("sous-agent-parti-avant", LIGNES_SOUS_AGENT, {"tours": 0, "total": 0, "appels": 0}, (sec(0), sec(60)), True),
    ("sous-agent-entier", LIGNES_SOUS_AGENT, {"tours": 2, "total": 22, "appels": 1}, (sec(-10), sec(0)), True),
]


def ecrire(chemin, lignes):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")


def verifier(nom, lignes, attendu, plage=None, sous_agent=False):
    """Mesure les lignes écrites en transcript de session, ou de sous-agent, sur la plage.
    « sans heure » sur stderr si et seulement si un tour en manque."""
    with tempfile.TemporaryDirectory() as tmp:
        if sous_agent:
            chemin = os.path.join(tmp, "sess", "subagents", f"agent-{nom}.jsonl")
        else:
            chemin = os.path.join(tmp, nom + ".jsonl")
        ecrire(chemin, lignes)
        erreurs = io.StringIO()
        with contextlib.redirect_stderr(erreurs):
            r, erreur = mesurer(chemin, plage)
    if erreur:
        return f"{nom} : mesurer a rendu une erreur : {erreur}"
    for cle, val in attendu.items():
        if cle not in r:
            return f"{nom} : colonne absente : {cle}"
        if r[cle] != val:
            return f"{nom} : {cle} = {r[cle]}, attendu {val}"
    if ("sans heure" in erreurs.getvalue()) != (r["sans_heure"] > 0):
        return f"{nom} : sans_heure = {r['sans_heure']}, stderr = {erreurs.getvalue()!r}"
    return None


@contextlib.contextmanager
def home(dossier):
    """Redirige le home : HOME sous POSIX, USERPROFILE sous Windows."""
    anciens = {k: os.environ.get(k) for k in ("HOME", "USERPROFILE")}
    for k in anciens:
        os.environ[k] = dossier
    try:
        yield
    finally:
        for k, v in anciens.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def verifier_resolution():
    with tempfile.TemporaryDirectory() as tmp:
        attendu = os.path.join(tmp, ".claude", "projects", "projet-x", "abc-123.jsonl")
        ecrire(attendu, LIGNES)
        with home(tmp):
            chemin, erreur = mod.resoudre("abc-123")
            if erreur or os.path.normcase(chemin) != os.path.normcase(attendu):
                return f"resoudre(id) = {chemin!r} / {erreur!r}, attendu {attendu!r}"
            chemin, erreur = mod.resoudre("inconnu-999")
            if chemin is not None or not erreur:
                return f"resoudre(id inconnu) = {chemin!r} / {erreur!r}, attendu une erreur"
            chemin, erreur = mod.resoudre("~/a/b.jsonl")
            if erreur or not os.path.normcase(chemin).startswith(os.path.normcase(tmp)):
                return f"resoudre(~) = {chemin!r}, attendu sous {tmp!r}"
            for brut in ("C:\\a\\b.jsonl", "C:/a/b.jsonl"):
                chemin, erreur = mod.resoudre(brut)
                if erreur or chemin != brut:
                    return f"resoudre({brut!r}) = {chemin!r}, attendu tel quel"

            # Le même fichier passé par son id puis par son chemin : une seule
            # ligne de table, pas de TOTAL, une ligne d'appels.
            sortie, erreurs = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
                code = mod.main(["abc-123", attendu])
            lignes = sortie.getvalue().splitlines()
            if code != 0 or len(lignes) != 3 or "TOTAL" in sortie.getvalue():
                return f"main(id, chemin) : code {code}, sortie {lignes!r}, attendu 3 lignes sans TOTAL"
            if lignes[2] != "abc-123.jsonl\tappels\tBash=2 Edit=1":
                return f"main : ligne d'appels = {lignes[2]!r}"
            if "déjà compté" not in erreurs.getvalue():
                return f"main : doublon non signalé sur stderr : {erreurs.getvalue()!r}"
    return None


def verifier_sous_agents():
    """Une session et deux sous-agents, que `main` range sous sa ligne ; une session sans
    `subagents/` ; un sous-agent passé aussi à part, compté une fois."""
    with tempfile.TemporaryDirectory() as tmp:
        projet = os.path.join(tmp, ".claude", "projects", "projet-x")
        session, seule = os.path.join(projet, "sess-1.jsonl"), os.path.join(projet, "sess-2.jsonl")
        dossier = os.path.join(projet, "sess-1", "subagents")
        agent_a, agent_b = os.path.join(dossier, "agent-a.jsonl"), os.path.join(dossier, "agent-b.jsonl")
        ecrire(session, LIGNES)
        ecrire(seule, LIGNES)
        ecrire(agent_b, [assistant("msg_SB", 1, 2, 3, 4)])
        ecrire(agent_a, [assistant("msg_SA", 10, 20, 30, 40)])
        ecrire(os.path.join(dossier, "agent-a.meta.json"), ["{}"])     # pas un transcript
        trouves = [os.path.normcase(c) for c in mod.sous_agents(session)]
        if trouves != [os.path.normcase(agent_a), os.path.normcase(agent_b)]:
            return f"sous_agents(session) = {trouves!r}, attendu agent-a puis agent-b"
        if mod.sous_agents(seule) != []:
            return f"sous_agents(sans subagents/) = {mod.sous_agents(seule)!r}, attendu []"
        sortie, erreurs = io.StringIO(), io.StringIO()
        with home(tmp), contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
            code = mod.main(["sess-1", agent_a])
    lignes = sortie.getvalue().splitlines()
    noms = [ligne.split("\t")[0] for ligne in lignes[1:5]]
    if code != 0 or noms != ["sess-1.jsonl", "agent-a.jsonl", "agent-b.jsonl", "TOTAL"]:
        return f"main(session, un de ses sous-agents) : code {code}, lignes {noms!r}"
    total = lignes[4].split("\t")[1 + mod.COLONNES.index("total")]
    if total != str(ATTENDU["total"] + 100 + 10):
        return f"main : total du TOTAL = {total}, attendu {ATTENDU['total']} + 100 + 10"
    if erreurs.getvalue().count("déjà compté") != 1:
        return f"main : sous-agent passé deux fois, stderr = {erreurs.getvalue()!r}"
    return None


def verifier_chemin_long():
    """Sous Windows, un transcript de sous-agent de 260 caractères se trouve et se lit ;
    ailleurs, rien à vérifier."""
    if os.name != "nt":
        return None
    prefixe = "\\\\?\\"     # sans lui, ni l'écrire ni l'effacer
    with tempfile.TemporaryDirectory() as tmp:
        court = os.path.join(tmp, "s", "subagents", "agent-long.jsonl")
        racine = os.path.join(tmp, "s" * (1 + 260 - len(court)))
        chemin = os.path.join(racine, "subagents", "agent-long.jsonl")
        ecrire(prefixe + chemin, LIGNES)
        try:
            trouves = mod.sous_agents(racine + ".jsonl")
            if [len(c) for c in trouves] != [260]:
                return f"sous_agents(chemin long) = {trouves!r}, attendu un chemin de 260"
            r, erreur = mesurer(trouves[0])
            if erreur or r["tours"] != ATTENDU["tours"]:
                return f"mesurer(chemin de 260) : {erreur or r['tours']!r}, attendu {ATTENDU['tours']} tours"
        finally:
            os.remove(prefixe + chemin)
    return None


def verifier_plage_cli():
    """`--plage DEBUT FIN` : bornes en heures ISO, UTC ou locales, ou en commits Git ; une borne
    illisible — un fichier suivi par Git compris — ou une plage incomplète sort 1."""
    def lancer(*argv):
        sortie, erreurs = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
            code = mod.main(list(argv))
        lignes = [l.split("\t") for l in sortie.getvalue().splitlines()]
        ligne = next((dict(zip(mod.COLONNES, l[1:])) for l in lignes if l[0] == "sess-p.jsonl"), {})
        return code, (ligne.get("tours"), ligne.get("total")), erreurs.getvalue()

    locale = lambda m: (ORIGINE + datetime.timedelta(minutes=m)).astimezone().replace(tzinfo=None).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        ecrire(os.path.join(tmp, ".claude", "projects", "projet-x", "sess-p.jsonl"), LIGNES_PLAGE)
        ecrire(os.path.join(tmp, "suivi.txt"), ["x"])
        # Deux commits datés -60 et +15 minutes ; le premier suit `suivi.txt`.
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        subprocess.run(git + ["init", "-q"], cwd=tmp, capture_output=True)
        subprocess.run(git + ["add", "suivi.txt"], cwd=tmp, capture_output=True)
        for m in (-60, 15):
            date = "%d +0000" % sec(m)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", str(m)], cwd=tmp, capture_output=True,
                           env=dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        ancien = os.getcwd()
        os.chdir(tmp)
        try:
            with home(tmp):
                for nom, bornes in (("heures UTC", (iso(-60), iso(15))), ("heures locales", (locale(-60), locale(15))),
                                    ("commits", ("HEAD~1", "HEAD"))):
                    code, ligne, erreurs = lancer("--plage", *bornes, "sess-p")
                    if code != 0 or ligne != ("3", "2022"):
                        return f"--plage en {nom} : code {code}, (tours, total) = {ligne}, stderr {erreurs!r}"
                for nom, texte in (("borne illisible", "ni-heure-ni-commit"), ("fichier suivi par Git", "suivi.txt")):
                    code, _, erreurs = lancer("--plage", texte, "HEAD", "sess-p")
                    if code != 1 or texte not in erreurs:
                        return f"--plage, {nom} : code {code}, stderr {erreurs!r}"
                code, _, _ = lancer("sess-p", "--plage", iso(0))
                if code != 1:
                    return f"--plage incomplète : code {code}"
        finally:
            os.chdir(ancien)
    return None


def main():
    for nom, lignes, attendu, *options in [
        ("trois-tours", LIGNES, ATTENDU),
        ("divergent", LIGNES_DIVERGENT, ATTENDU_DIVERGENT),
        ("poids", LIGNES_POIDS, ATTENDU_POIDS),
        ("inconnu", LIGNES_INCONNU, {k: v for k, v in ATTENDU_INCONNU.items() if v is not None}),
        ("opus-5-5", LIGNES_OPUS55, ATTENDU_OPUS55),
    ] + CAS_PLAGE:
        ecart = verifier(nom, lignes, attendu, *options)
        if ecart:
            print(ecart)
            return 1
    for bloc in (verifier_resolution, verifier_sous_agents, verifier_chemin_long, verifier_plage_cli):
        ecart = bloc()
        if ecart:
            print(ecart)
            return 1
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        code = mod.main(["--grille"])
    if code != 0 or len(sortie.getvalue().splitlines()) != 1 + len(mod.GRILLE):
        print(f"main(--grille) : code {code}, {len(sortie.getvalue().splitlines())} lignes, attendu {1 + len(mod.GRILLE)}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
