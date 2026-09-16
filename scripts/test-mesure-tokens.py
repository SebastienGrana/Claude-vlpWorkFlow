#!/usr/bin/env python3
"""Teste `mesurer` de mesure-tokens.py sans fixture sur disque.

Écrit un jsonl synthétique dans un dossier temporaire, appelle `mesurer`,
compare colonne par colonne. Imprime `OK` et sort 0, ou le premier écart et sort 1.
"""
import importlib.util
import json
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mesure_tokens", os.path.join(ICI, "mesure-tokens.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mesurer = mod.mesurer


def assistant(mid, entree, sortie, creation, lecture, sous_objet=None, contenu="texte"):
    """Une ligne `assistant`. `sous_objet` : (1h, 5m), ou None pour un usage
    sans `cache_creation` (vieux transcript)."""
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
                    "content": [{"type": "text", "text": contenu}]},
    })


# Trois tours : A sur trois lignes (mêmes comptes), B sur une ligne sans
# sous-objet cache_creation, C sur une ligne. Plus une ligne sans usage, une
# ligne invalide, une ligne vide.
LIGNES = [
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40)),
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40), contenu="bloc 2"),
    json.dumps({"type": "user", "message": {"role": "user", "content": "sans usage"}}),
    assistant("msg_A", 10, 5, 100, 1000, sous_objet=(60, 40), contenu="bloc 3"),
    "{ceci n'est pas du json",
    "",
    assistant("msg_B", 20, 7, 200, 2000),
    assistant("msg_C", 30, 9, 300, 3000, sous_objet=(300, 0)),
]

ATTENDU = {
    "tours": 3,
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
    assistant("msg_D", 1, 6, 10, 100, contenu="bloc 2"),
]
ATTENDU_DIVERGENT = {"tours": 1, "output": 6, "divergents": 1}


def verifier(nom, lignes, attendu):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = os.path.join(tmp, nom + ".jsonl")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
        r, erreur = mesurer(chemin)
    if erreur:
        return f"{nom} : mesurer a rendu une erreur : {erreur}"
    for cle, val in attendu.items():
        if cle not in r:
            return f"{nom} : colonne absente : {cle}"
        if r[cle] != val:
            return f"{nom} : {cle} = {r[cle]}, attendu {val}"
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
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
