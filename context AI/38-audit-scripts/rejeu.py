"""Rejoue les chiffres de l'audit des pages publiées tirés des FICHIERS
(les hauteurs en écrans viennent du navigateur, les coûts de lecture des
transcriptions : scripts à part). Python 3, sans dépendance.

    python rejeu.py <racine ProgPerso>
"""
import glob, json, os, re, sys

racine = sys.argv[1]
art = os.path.join(racine, "Cairn-VlpLib", "context AI", "artefacts")
kit = os.path.join(racine, "Claude-vlpWorkflow")
gab = open(os.path.join(kit, "templates", "artefact-chantier.html"), encoding="utf-8").read()


def style(s):
    return sum(len(m) for m in re.findall(r"<style>(.*?)</style>", s, re.S))


def page(n):
    # une page de chantier, par son numéro : son titre reste dans le dépôt de Cairn
    (chemin,) = glob.glob(os.path.join(art, "%d-*.html" % n))
    return chemin


r = {}
pages = sorted(glob.glob(os.path.join(art, "*.html")))
chantiers = [p for p in pages if not p.endswith("feuille-de-route.html")]
r["pages"] = len(pages)
r["pages_chantier"] = len(chantiers)
for motif, cle in (("<details", "details"), ("<nav", "nav"), ('href="#', "ancres"), ("<button", "boutons"), ("<script", "scripts"), ("<svg", "svg")):
    r[cle + "_pages_avec"] = sum(1 for p in pages if motif in open(p, encoding="utf-8").read())
tailles = sorted(os.path.getsize(p) for p in chantiers)
r["taille_chantier_min_med_max"] = (tailles[0], tailles[len(tailles) // 2], tailles[-1])
parts = sorted(round(100.0 * style(open(p, encoding="utf-8").read()) / len(open(p, encoding="utf-8").read()))
               for p in chantiers if 'class="fiche"' in open(p, encoding="utf-8").read())
r["part_css_chantier_mediane_pct"] = parts[len(parts) // 2]
r["commentaires_html_page_recente"] = sum(len(m) for m in re.findall(r"<!--.*?-->", open(page(41), encoding="utf-8").read(), re.S))

f = open(os.path.join(art, "feuille-de-route.html"), encoding="utf-8").read()
r["feuille_octets"] = len(f.encode("utf-8"))
r["feuille_car"] = len(f)
todo = re.search(r"ZONE:todo.*?<tbody>(.*?)</tbody>", f, re.S).group(1)
clos = re.search(r"ZONE:clos.*?<tbody>(.*?)</tbody>", f, re.S).group(1)
r["todo_lignes"] = len(re.findall(r"<tr>", todo))
r["todo_car"] = len(todo)
r["todo_part_pct"] = round(100.0 * len(todo) / len(f))
lg = sorted(len(x) for x in re.findall(r"<tr>.*?</tr>", todo, re.S))
r["todo_ligne_min_med_max"] = (lg[0], lg[len(lg) // 2], lg[-1])
r["etoiles_markdown"] = f.count("**")
r["liens_markdown"] = len(re.findall(r"\]\(https?://", f))
r["href_chevrons"] = len(re.findall(r'href="&lt;', f))
r["clos_lignes"] = len(re.findall(r"<tr>", clos))
r["todo_rangs_coches"] = len(re.findall(r'<tr><td class="mono">[^<]*</td><td>✅', todo))
r["majuscules_css"] = len(re.findall(r"text-transform:\s*uppercase", gab))

p23 = open(page(23), encoding="utf-8").read()
r["p23_bilan_cache"] = bool(re.search(r"ZONE:bilan[^\n]*\n\s*<section hidden>", p23))
r["p24_sans_zone"] = "ZONE:" not in open(page(24), encoding="utf-8").read()
r["p27_enveloppe"] = open(page(27), encoding="utf-8").read().startswith("<!doctype html>")
r["gabarits_meta_charset"] = sum(open(os.path.join(kit, "templates", g), encoding="utf-8").read().count("charset")
                                 for g in ("artefact-chantier.html", "artefact-feuille-de-route.html"))

# les chantiers clos de la feuille, pour le graphique
donnees = []
for rang in re.findall(r"<tr>.*?</tr>", clos, re.S):
    cel = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", rang, re.S)]
    brut = re.search(r"\(([\d  ]+)\)", cel[3])
    nom = re.sub(r"\s*clos$", "", cel[0])
    donnees.append({"chantier": nom, "fiches": cel[1], "clos": cel[2],
                    "tokens": int(re.sub(r"\D", "", brut.group(1))) if brut else None})
r["clos_mesures"] = sum(1 for d in donnees if d["tokens"])
r["clos_total_tokens"] = sum(d["tokens"] for d in donnees if d["tokens"])

for k, v in r.items():
    print("%-34s %s" % (k, v))
json.dump(donnees, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "clos.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
