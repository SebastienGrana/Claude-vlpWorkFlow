#!/usr/bin/env python3
"""Teste mesure-tokens.py sans fixture sur disque.

Écrit des jsonl synthétiques dans un dossier temporaire, appelle `mesurer`,
`resoudre` et `main`, compare. Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mesure_tokens", os.path.join(ICI, "mesure-tokens.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mesurer = mod.mesurer


def outil(nom):
    return {"type": "tool_use", "id": "toolu_" + nom, "name": nom, "input": {}}


def assistant(mid, entree, sortie, creation, lecture, sous_objet=None, blocs=None):
    """Une ligne `assistant`. `sous_objet` : (1h, 5m), ou None pour un usage
    sans `cache_creation` (vieux transcript). `blocs` : le contenu, un bloc
    texte par défaut."""
    usage = {
        "input_tokens": entree,
        "output_tokens": sortie,
        "cache_creation_input_tokens": creation,
        "cache_read_input_tokens": lecture,
    }
    if sous_objet is not None:
        h1, m5 = sous_objet
        usage["cache_creation"] = {"ephemeral_1h_input_tokens": h1, "ephemeral_5m_input_tokens": m5}
    return json.dumps({
        "type": "assistant",
        "requestId": "req_" + mid,
        "message": {"id": mid, "model": "test", "usage": usage,
                    "content": blocs if blocs is not None else [{"type": "text", "text": "texte"}]},
    })


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


def ecrire(chemin, lignes):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")


def verifier(nom, lignes, attendu):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = os.path.join(tmp, nom + ".jsonl")
        ecrire(chemin, lignes)
        r, erreur = mesurer(chemin)
    if erreur:
        return f"{nom} : mesurer a rendu une erreur : {erreur}"
    for cle, val in attendu.items():
        if cle not in r:
            return f"{nom} : colonne absente : {cle}"
        if r[cle] != val:
            return f"{nom} : {cle} = {r[cle]}, attendu {val}"
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


def main():
    for nom, lignes, attendu in [
        ("trois-tours", LIGNES, ATTENDU),
        ("divergent", LIGNES_DIVERGENT, ATTENDU_DIVERGENT),
    ]:
        ecart = verifier(nom, lignes, attendu)
        if ecart:
            print(ecart)
            return 1
    ecart = verifier_resolution()
    if ecart:
        print(ecart)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
