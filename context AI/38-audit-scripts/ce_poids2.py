"""Poids réel recalculé : (a) arrêt au premier compactage, (b) lectures seules
ou toutes, (c) dénominateur avec ou sans sous-agents (dédoublonnés par id)."""
import glob, json, os, sys
d = sys.argv[1]
top = glob.glob(os.path.join(d, "*.jsonl"))
sous = [p for p in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True) if p not in top]

def contexts(chemin, avec_evts=True):
    ctxs, evts, par = [], [], {}
    vus = set()
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
                    if isinstance(t, dict) and t.get("type") == "tool_use":
                        par.setdefault(m.get("id"), 0)
                        par[m.get("id")] += 1
                        if t.get("name") == "Artifact" and t.get("input", {}).get("action") == "read":
                            evts.append((len(ctxs) - 1, m.get("id")))
    return ctxs, evts, par

res = {"brut": 0, "compact": 0, "seules_compact": 0, "ajout_seules": 0}
den_main = 0
for ch in top:
    ctxs, evts, par = contexts(ch)
    den_main += sum(ctxs)
    for i, mid in evts:
        if i + 1 >= len(ctxs): continue
        aj = ctxs[i + 1] - ctxs[i]
        if aj <= 0: continue
        rest = len(ctxs) - (i + 1)
        # jusqu'au premier compactage
        k = i + 1
        while k + 1 < len(ctxs) and ctxs[k + 1] >= 0.6 * ctxs[k]:
            k += 1
        rest_c = k - i
        res["brut"] += aj * rest
        res["compact"] += aj * rest_c
        if par.get(mid, 1) == 1:
            res["seules_compact"] += aj * rest_c
            res["ajout_seules"] += aj
den_sous = 0
for ch in sous:
    ctxs, _, _ = contexts(ch)
    den_sous += sum(ctxs)
print("dénominateur sessions principales", den_main)
print("dénominateur sous-agents (dédoublonné)", den_sous)
for k, v in res.items():
    print("%-16s %12d  part/principal %.2f %%  part/(principal+sous) %.2f %%" % (k, v, 100.0 * v / den_main, 100.0 * v / (den_main + den_sous)))
