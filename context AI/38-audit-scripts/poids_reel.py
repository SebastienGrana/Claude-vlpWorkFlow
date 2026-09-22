"""Poids réel d'une lecture de page : tokens ajoutés x tours restants de la
session (le bloc est relu, depuis le cache, à chaque tour suivant)."""
import glob, json, os, sys
tot_ajout = tot_poids = n = 0
feuille = [0, 0, 0]
tot_session = 0
for chemin in sorted(glob.glob(os.path.join(sys.argv[1], "*.jsonl"))):
    ctxs, evts = [], []
    with open(chemin, encoding="utf-8") as f:
        for l in f:
            try: o = json.loads(l)
            except ValueError: continue
            m = o.get("message") or {}
            if o.get("type") == "assistant" and m.get("usage"):
                u = m["usage"]
                c = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                if not ctxs or ctxs[-1] != c:
                    ctxs.append(c)
                for t in m.get("content", []):
                    if isinstance(t, dict) and t.get("type") == "tool_use" and t.get("name") == "Artifact" and t.get("input", {}).get("action") == "read":
                        evts.append((len(ctxs) - 1, t["input"].get("url", "")))
    tot_session += sum(ctxs)
    for i, url in evts:
        if i + 1 >= len(ctxs): continue
        ajout = ctxs[i + 1] - ctxs[i]
        if ajout <= 0: continue
        restants = len(ctxs) - (i + 1)
        n += 1; tot_ajout += ajout; tot_poids += ajout * restants
        if "71823ec4" in url or "F1xfVYG1" in url:
            feuille[0] += 1; feuille[1] += ajout; feuille[2] += ajout * restants
print("lectures", n, "· ajout", tot_ajout, "· poids réel (x tours restants)", tot_poids)
print("dont feuille de route", feuille[0], "· ajout", feuille[1], "· poids réel", feuille[2])
print("contexte total de toutes les sessions (somme des tours)", tot_session)
print("part des lectures de pages dans le total : %.2f %%" % (100.0 * tot_poids / tot_session))
