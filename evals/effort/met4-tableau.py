#!/usr/bin/env python3
"""Le tableau de MET4 : une ligne par essai, depuis met4-resultats.jsonl et la ligne `result` de chaque trace ;
puis les sommes par niveau (4 fiches, et les 3 fiches de code seules, à comparer à VIT25 série 2). Imprime du
markdown. Repris de `tableau-vit25.py` (VIT25, reconstitué du transcript de sa session) ; `compteur` retiré."""
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
FICHES = ["VIT23", "VIT20", "VIT19", "VIT12"]
NIVEAUX = ["medium", "high", "xhigh"]


def resultat(trace):
    if not os.path.isfile(trace):
        return {}
    with open(trace, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            if '"type":"result"' in ligne:
                return json.loads(ligne)
    return {}


def mutants(trace):
    """Les verdicts des appels d'outil qui lancent `vlp.py … mutant` : la dernière ligne `MUTANT …` du résultat de
    chacun ; « a/v/p » = attrapés, vivants, plantés (même lecture que VIT25)."""
    if not os.path.isfile(trace):
        return "?"
    appels, n = set(), {"ATTRAP": 0, "VIVANT": 0, "PLANT": 0}
    with open(trace, encoding="utf-8", errors="replace") as f:
        messages = [json.loads(ligne) for ligne in f if ligne.startswith("{")]
    for d in messages:
        for b in ((d.get("message") or {}).get("content") or []) if d.get("type") == "assistant" else []:
            commande = str((b.get("input") or {}).get("command", "")) if isinstance(b, dict) else ""
            if b.get("type") == "tool_use" and re.search(r"vlp\.py\"?\s+mutant\b", commande):
                appels.add(b["id"])
    for d in messages:
        for b in ((d.get("message") or {}).get("content") or []) if d.get("type") == "user" else []:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in appels:
                c = b.get("content")
                texte = c if isinstance(c, str) else " \n".join(x.get("text", "") for x in c or [] if isinstance(x, dict))
                verdicts = [x for x in texte.splitlines() if x.startswith("MUTANT ")]
                for k in n:
                    n[k] += 1 if verdicts and verdicts[-1].startswith("MUTANT " + k) else 0
    return "%d/%d/%d" % (n["ATTRAP"], n["VIVANT"], n["PLANT"])


def fr(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def milliers(x):
    return "{:,}".format(x).replace(",", " ") if isinstance(x, int) else "?"


def cliquet(c):
    if c.get("code") is None:
        return "non mesuré"
    bilan = next((s for s in c.get("sortie", []) if s.startswith("CLIQUET ") and "fonctions" in s), "")
    m = re.search(r"touchées (\d+).*neuves (\d+)", bilan)
    etat = "tenu" if c["code"] == 0 else "ROMPU"
    return "%s (%s touchées, %s neuves)" % (etat, m.group(1), m.group(2)) if m else etat


def lignes():
    out = []
    with open(os.path.join(ICI, "met4-resultats.jsonl"), encoding="utf-8") as f:
        for ligne in f:
            d = json.loads(ligne)
            nom = "%s-%s" % (d["fiche"], d["niveau"])
            trace = os.path.join(ICI, "traces", nom, d["fiche"] + ".jsonl")
            r = resultat(trace)
            m = re.search(r"FICHE \S+ · CASE \[(.)\] · tours (\d+) · ([\d.]+) \$ · (\d+) s", " ".join(d["boucle"]))
            if not m:
                out.append({"fiche": d["fiche"], "niveau": d["niveau"], "brut": d["boucle"]})
                continue
            usage = r.get("usage") or {}
            out.append({"fiche": d["fiche"], "niveau": d["niveau"], "case": m.group(1), "tours": int(m.group(2)),
                        "usd": float(m.group(3)), "s": int(m.group(4)),
                        "pense": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
                        "sortie": usage.get("output_tokens"),
                        "suite": "OK" if d["suite"]["ok"] else "ROUGE", "pyright": d["pyright"],
                        "cliquet": cliquet(d["cliquet"]), "verifier": "%d → %d" % tuple(d["verifier"]),
                        "mutant": mutants(trace), "relecteur": d["relecteur"]["verdict"],
                        "rel_usd": d["relecteur"]["usd"]})
    return sorted(out, key=lambda x: (FICHES.index(x["fiche"]), NIVEAUX.index(x["niveau"])))


rangs = lignes()
print("| Fiche · effort | Cochée | Tours | Essai | Durée | Réflexion (jetons) | Sortie (jetons) | Suite | pyright "
      "| Cliquet | `verifier(` | Mutants a/v/p | Relecteur |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in rangs:
    if "brut" in x:
        print("| %s · `%s` | ligne FICHE absente : %s |" % (x["fiche"], x["niveau"], " ; ".join(x["brut"])))
        continue
    print("| %s · `%s` | %s | %d | %s $ | %d s | %s | %s | %s | %s | %s | %s | %s | %s (%s $) |" % (
        x["fiche"], x["niveau"], "oui" if x["case"] == "x" else "non", x["tours"], fr(x["usd"]), x["s"],
        milliers(x["pense"]), milliers(x["sortie"]), x["suite"], x["pyright"], x["cliquet"], x["verifier"],
        x["mutant"], x["relecteur"], fr(x["rel_usd"])))
pleins = [x for x in rangs if "brut" not in x]
for titre, fiches in (("4 fiches", FICHES), ("3 fiches de code, comme VIT25 série 2", FICHES[:3])):
    print()
    print("Par niveau (%s) :" % titre)
    for niv in NIVEAUX:
        r = [x for x in pleins if x["niveau"] == niv and x["fiche"] in fiches]
        print("- `%s` : %d essais · %s $ d'essais · %d tours · %d s · réflexion %s jetons · relecteur %d/%d ACCEPTÉE"
              " · %s $ de relecteurs" % (niv, len(r), fr(sum(x["usd"] for x in r)), sum(x["tours"] for x in r),
                                         sum(x["s"] for x in r), milliers(sum(x["pense"] or 0 for x in r)),
                                         sum(1 for x in r if x["relecteur"] == "ACCEPTÉE"), len(r),
                                         fr(sum(x["rel_usd"] for x in r))))
print()
print("Total : %s $ d'essais + %s $ de relecteurs = %s $" % (
    fr(sum(x["usd"] for x in pleins)), fr(sum(x["rel_usd"] for x in pleins)),
    fr(sum(x["usd"] + x["rel_usd"] for x in pleins))))
