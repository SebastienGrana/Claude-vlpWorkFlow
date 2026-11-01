"""`mesure-tokens.py` : une ligne de transcript qui est du JSON mais pas un objet (REF21).

`null`, une liste ou une chaîne se lisent sans erreur par `json.loads`, puis faisaient tomber `mesurer` sur
`d.get` (`AttributeError`) ; pyright l'a vu dès que la ligne lue a été typée `object`. Elles comptent
désormais comme lignes invalides, comme un JSON illisible.
"""
import importlib.util
import json
import os

from aides import SCRIPTS

spec = importlib.util.spec_from_file_location("mesure_tokens", os.path.join(SCRIPTS, "mesure-tokens.py"))
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_ligne_json_non_objet_comptee_invalide(tmp_path):
    tour = {"type": "assistant", "message": {"id": "msg_A", "model": "test", "content": [],
                                             "usage": {"input_tokens": 1, "output_tokens": 2}}}
    chemin = tmp_path / "s.jsonl"
    chemin.write_text("\n".join(["null", "[1, 2]", '"texte"', "3", json.dumps(tour)]) + "\n", encoding="utf-8")
    r, erreur = mod.mesurer(str(chemin))
    assert erreur is None
    assert (r["tours"], r["input"], r["output"], r["invalides"]) == (1, 1, 2, 4)
