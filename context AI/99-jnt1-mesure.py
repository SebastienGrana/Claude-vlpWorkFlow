"""JNT1 : publications `Artifact` et refus « joints non lus » dans les transcriptions.
Usage : py "context AI/99-jnt1-mesure.py" "<motif de dossier sous ~/.claude/projects>"
(défaut *vlpWorkflow*). Lit les blocs tool_use/tool_result, jamais le texte des messages :
un `grep` compte aussi les citations (13 fichiers, 76 occurrences le 2026-09-29)."""
import glob, json, os, re, sys
REFUS = "touches files whose published content is not what you last saw"
motif = sys.argv[1] if len(sys.argv) > 1 else "*vlpWorkflow*"
pub = {True: 0, False: 0}; refus = 0; s_refus = set(); s_pub = set(); repub = 0; passes = 0
for f in glob.glob(os.path.join(os.path.expanduser("~/.claude/projects"), motif, "*.jsonl")):
    vus, appels = set(), {}
    for l in open(f, encoding="utf-8", errors="replace"):
        try:
            c = (json.loads(l).get("message") or {}).get("content")
        except (ValueError, AttributeError):
            continue
        for b in c if isinstance(c, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") == "Artifact":
                i = b.get("input") or {}; a = i.get("action", "publish")
                if a in ("read", "list") and (i.get("path") or i.get("paths") or i.get("scope") == "files"):
                    vus.add(i.get("url"))
                elif a == "publish" and not i.get("asset") and i.get("file_path"):
                    appels[b["id"]] = (i.get("url"), bool(i.get("files")))
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in appels:
                url, files = appels.pop(b["tool_use_id"]); pub[files] += 1; s_pub.add(f)
                t = b.get("content"); t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
                if REFUS in t:
                    refus += 1; s_refus.add(f)
                if not b.get("is_error"):
                    if url and files:
                        repub += 1; passes += url not in vus
                    m = re.search(r"artifact/(\w+)", t)
                    vus.add(url or (m and "https://claude.ai/artifact/" + m.group(1)))
print("PUBLICATIONS avec files %d · sans files %d · sessions %d" % (pub[True], pub[False], len(s_pub)))
print("REFUS joints non lus %d · sessions %d" % (refus, len(s_refus)))
print("REPUBLICATIONS avec files reussies %d · dont sans joint vu ni publie avant dans la session %d" % (repub, passes))
