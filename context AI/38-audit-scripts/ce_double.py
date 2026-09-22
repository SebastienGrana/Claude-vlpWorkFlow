import glob, json, os, sys
d = sys.argv[1]
multi = 0; evts_multi = 0; ajout_double = 0; poids_double = 0
for ch in glob.glob(os.path.join(d, "*.jsonl")):
    ctxs, lus = [], {}
    with open(ch, encoding="utf-8") as f:
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
                        lus.setdefault((len(ctxs) - 1), []).append(t["input"].get("url", ""))
    for i, urls in lus.items():
        if len(urls) > 1 and i + 1 < len(ctxs):
            aj = ctxs[i + 1] - ctxs[i]
            if aj <= 0: continue
            multi += 1; evts_multi += len(urls)
            ajout_double += aj * (len(urls) - 1)
            poids_double += aj * (len(urls) - 1) * (len(ctxs) - (i + 1))
print("tours avec plusieurs Artifact read", multi, "· lectures concernées", evts_multi)
print("ajout compté en trop", ajout_double, "· poids réel compté en trop", poids_double)
