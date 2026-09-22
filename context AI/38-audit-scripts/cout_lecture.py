"""Coût réel, en tokens, d'une lecture de page publiée (Artifact read) et de
la publication qui suit, mesuré dans les transcriptions de sessions.

Méthode : pour chaque tool_use Artifact, on prend le contexte total
(input + cache_creation + cache_read) du message assistant qui l'émet, et
celui du message assistant suivant. L'écart = ce que le résultat de l'outil
(et le petit texte autour) a ajouté au contexte.
"""
import glob, json, os, sys

dossier = sys.argv[1]
lignes_sortie = []
for chemin in sorted(glob.glob(os.path.join(dossier, "*.jsonl"))):
    msgs = []
    with open(chemin, encoding="utf-8") as f:
        for l in f:
            try:
                o = json.loads(l)
            except ValueError:
                continue
            m = o.get("message") or {}
            if o.get("type") == "assistant" and m.get("usage"):
                u = m["usage"]
                ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                outils = [c for c in m.get("content", []) if isinstance(c, dict) and c.get("type") == "tool_use"]
                msgs.append((ctx, outils, o.get("timestamp", "")))
    # dédoublonner : un message assistant peut apparaître en plusieurs lignes
    for i, (ctx, outils, ts) in enumerate(msgs):
        for t in outils:
            if t.get("name") != "Artifact":
                continue
            inp = t.get("input", {})
            action = inp.get("action", "publish")
            if action not in ("read", "publish"):
                continue
            suivant = next((c for c, o2, _ in msgs[i + 1:] if c != ctx), None)
            if suivant is None:
                continue
            cible = os.path.basename(inp.get("file_path", "") or inp.get("url", ""))
            lignes_sortie.append((ts[:10], os.path.basename(chemin)[:8], action, cible, suivant - ctx))

for l in lignes_sortie:
    print("%s  %s  %-7s  %-45s  %+7d" % l)
lectures = [l[4] for l in lignes_sortie if l[2] == "read" and l[4] > 0]
pubs = [l[4] for l in lignes_sortie if l[2] == "publish" and l[4] > 0]
for nom, v in (("read", lectures), ("publish", pubs)):
    if v:
        v = sorted(v)
        print("%s : n=%d  min=%d  médiane=%d  max=%d" % (nom, len(v), v[0], v[len(v) // 2], v[-1]))
