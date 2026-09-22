"""Lectures de la feuille de route de Cairn, une par une : date, tokens
ajoutés, et si le tour contenait d'autres appels d'outils (écart surestimé).
Puis le coût par fiche des chantiers clos du kit, pour chiffrer les chantiers.

    python feuille_detail.py <transcriptions de Cairn> <racine ProgPerso>
"""
import glob, json, os, re, sys

d, racine = sys.argv[1], sys.argv[2]
points = []
for chemin in glob.glob(os.path.join(d, "*.jsonl")):
    ctxs, evts, par = [], [], {}
    with open(chemin, encoding="utf-8") as f:
        for l in f:
            try:
                o = json.loads(l)
            except ValueError:
                continue
            m = o.get("message") or {}
            if o.get("type") == "assistant" and m.get("usage"):
                u = m["usage"]
                c = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                if not ctxs or ctxs[-1] != c:
                    ctxs.append(c)
                for t in m.get("content", []):
                    if isinstance(t, dict) and t.get("type") == "tool_use":
                        par[m.get("id")] = par.get(m.get("id"), 0) + 1
                        if t.get("name") == "Artifact" and t.get("input", {}).get("action") == "read":
                            evts.append((len(ctxs) - 1, m.get("id"), t["input"].get("url", ""), o.get("timestamp", "")[:10]))
    for i, mid, url, date in evts:
        if i + 1 >= len(ctxs) or not ("71823ec4" in url or "F1xfVYG1" in url):
            continue
        aj = ctxs[i + 1] - ctxs[i]
        if aj > 0:
            points.append((date, aj, par.get(mid, 1) > 1))
points.sort()
print("feuille :", len(points), "lectures ·", sum(1 for p in points if not p[2]), "seules")
print(";".join("%s %d %d" % (a, b, int(c)) for a, b, c in points))

# coût par fiche des chantiers clos du kit
f = open(os.path.join(racine, "Claude-vlpWorkflow", "context AI", "artefacts", "feuille-de-route.html"), encoding="utf-8").read()
clos = re.search(r"ZONE:clos.*?<tbody>(.*?)</tbody>", f, re.S).group(1)
par_fiche = []
for rang in re.findall(r"<tr>.*?</tr>", clos, re.S):
    cel = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", rang, re.S)]
    brut = re.search(r"\(([\d  ]+)\)", " ".join(cel))
    nb = re.search(r"([A-Z]+)(\d+)\s*(?:–|-|\.\.)\s*[A-Z]*(\d+)", cel[1] if len(cel) > 1 else "")
    if brut and nb:
        n = int(nb.group(3)) - int(nb.group(2)) + 1
        par_fiche.append(int(re.sub(r"\D", "", brut.group(1))) / n)
par_fiche.sort()
q = lambda p: par_fiche[int(p * (len(par_fiche) - 1))]
print("kit : %d chantiers clos mesurés · coût par fiche : q1 %.2f M · médiane %.2f M · q3 %.2f M"
      % (len(par_fiche), q(.25) / 1e6, q(.5) / 1e6, q(.75) / 1e6))
