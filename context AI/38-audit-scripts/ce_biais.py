"""Contre-expertise : biais possibles de cout_lecture.py / poids_reel.py."""
import glob, json, os, sys, statistics
d = sys.argv[1]
top = glob.glob(os.path.join(d, "*.jsonl"))
sous = [p for p in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True) if p not in top]
print("jsonl racine", len(top), "· jsonl en sous-dossier (sous-agents)", len(sous))
side = 0
parall = []  # (delta, autres outils)
drops = 0
reads_avant_drop = 0
reads_sub = 0
tot_sub_ctx = 0
reads_seuls = []
for chemin in top:
    ctxs, evts = [], []
    par_msg = {}
    with open(chemin, encoding="utf-8") as f:
        for l in f:
            try: o = json.loads(l)
            except ValueError: continue
            if o.get("isSidechain"): side += 1
            m = o.get("message") or {}
            if o.get("type") == "assistant" and m.get("usage"):
                u = m["usage"]
                c = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                if not ctxs or ctxs[-1] != c:
                    ctxs.append(c)
                mid = m.get("id")
                for t in m.get("content", []):
                    if isinstance(t, dict) and t.get("type") == "tool_use":
                        par_msg.setdefault(mid, []).append(t.get("name"))
                        if t.get("name") == "Artifact" and t.get("input", {}).get("action") == "read":
                            evts.append((len(ctxs) - 1, mid))
    for i, mid in evts:
        if i + 1 >= len(ctxs): continue
        aj = ctxs[i + 1] - ctxs[i]
        if aj <= 0: continue
        autres = len(par_msg.get(mid, [])) - 1
        parall.append((aj, autres))
        if autres == 0: reads_seuls.append(aj)
        # chute de contexte (compactage) apres la lecture ?
        if any(ctxs[k + 1] < 0.6 * ctxs[k] for k in range(i + 1, len(ctxs) - 1)):
            reads_avant_drop += 1
    drops += sum(1 for k in range(len(ctxs) - 1) if ctxs[k + 1] < 0.6 * ctxs[k])
for p in sous:
    with open(p, encoding="utf-8") as f:
        for l in f:
            try: o = json.loads(l)
            except ValueError: continue
            m = o.get("message") or {}
            if o.get("type") == "assistant" and m.get("usage"):
                u = m["usage"]
                tot_sub_ctx += u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            for t in (m.get("content") or []) if isinstance(m.get("content"), list) else []:
                if isinstance(t, dict) and t.get("type") == "tool_use" and t.get("name") == "Artifact":
                    reads_sub += 1
print("lignes isSidechain dans les jsonl racine", side)
print("lectures retenues", len(parall), "· dont appelées en parallèle d'autres outils", sum(1 for a, n in parall if n > 0))
print("  somme delta lectures en parallèle", sum(a for a, n in parall if n > 0), "· seules", sum(a for a, n in parall if n == 0))
if reads_seuls:
    s = sorted(reads_seuls); print("  médiane des lectures SEULES", s[len(s) // 2], "n", len(s))
print("chutes de contexte >40 % (compactage)", drops, "· lectures suivies d'une chute", reads_avant_drop)
print("appels Artifact dans les sous-agents", reads_sub, "· contexte cumulé brut des sous-agents (non dédoublonné)", tot_sub_ctx)
