#!/usr/bin/env python3
"""Le faux `claude` des tests de boucle.py : aucun appel modèle, un rôle par prompt.

Lancé tel quel par `--claude` : `faux-claude.py -p "<prompt>" [--model M] [--agent A] ...`, il rend
les lignes `stream-json` relevées par NUI1 (`system/init`, `assistant`, `result`), réduites.
Rôles (le prompt dit lequel) : `/vlp:chantier <code>` découpe, `/vlp:tache <fiche>` joue et coche,
`/vlp:tache` clôt, `--agent vlp:relecture` relit (`<fiche> [--sha <sha>]`). Autre prompt : une
ligne sur stderr, rien sur stdout, code 2.
Pilotes, tous par l'environnement : VLP_FAUX_RATE (fiches non cochées, séparées par des virgules),
VLP_FAUX_REFUSE (`<fiche>:<cause>[,<cause>…]`, cause `fiche`, `copie` ou `aucun` — sans verdict : la
première, à chaque relecture ; avec VLP_FAUX_ETAT, un fichier d'essai, une cause par relecture de la
fiche dans l'ordre, ACCEPTÉE ensuite, et le motif rend son rang : `motif factice 2`), VLP_FAUX_LIMITE (préfixe de `--model`), VLP_FAUX_GENRE (le
genre de cette limite : `session` par défaut, `semaine`, `opus`), VLP_FAUX_REPLI (`1`), VLP_FAUX_DORT
(secondes), VLP_FAUX_ERREUR (`coupure`, `api`, `tours`, `budget`), VLP_FAUX_DENIALS (nombre d'entrées de
`permission_denials` dans le `result` ; réduites à `tool_name`, leur forme réelle n'est pas relevée),
VLP_FAUX_ARGV (chemin : y ajoute, une ligne JSON par lancement, les arguments reçus), VLP_FAUX_ENV (chemin :
y ajoute `{role, VLP_CANAL, VLP_CARNET}` de chaque lancement), VLP_FAUX_COMMIT (fiches, séparées par des
virgules : après les avoir cochées, le rôle `jouer` fait `git add -A` et `git commit -m "<fiche> : fiche
<fiche>"` dans le dossier courant — la session qui commite malgré tout), VLP_FAUX_VLP (chemin de vlp.py, par
défaut celui d'à côté). Une fiche à bloc **Tentatives** se coche `--resolu`, comme `jouer` et `relance` le font
dans `skills/tache/SKILL.md` (le faux ne les distingue pas : même prompt). Le rôle `jouer` pose `CLAUDE_CODE_SESSION_ID` = son `--session-id` aux commandes qu'il
lance, comme le vrai claude ; hors VLP_FAUX_COMMIT, le faux n'appelle jamais Git.
"""
import io
import json
import os
import re
import subprocess
import sys
import time
import uuid
from typing import Optional

for _flux in (sys.stdout, sys.stderr):
    try:
        if isinstance(_flux, io.TextIOWrapper):
            _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
MODELE_DEFAUT = "claude-opus-5-5"
COUT, TOURS = 0.01, 3

FICHE = """<!-- FICHE:%s -->
## %s [ ] — fiche %s

**Prompt**
Rien.

**Critère de fin**%s
Rien.
<!-- /FICHE -->

---

"""

# forme déduite, https://code.claude.com/docs/en/errors (lu le 2026-10-01) : le texte est celui de la
# page ; elle ne donne ni le code de sortie ni `subtype`, ni `is_error` — vrai, code 1, `success` : déduits.
LIMITES = {"session": "You've hit your session limit · resets 3:45pm",
           "semaine": "You've hit your weekly limit · resets Mon 12:00am",
           "opus": "You've hit your Opus limit · resets 3:45pm"}

COURANT = r"^(\s*-\s*\*\*fichier de fiches courant\*\*\s*:\s*)[^\r\n]*"
ARTEFACT = r"^(\s*-\s*\*\*artefact du chantier\*\*\s*:\s*)[^\r\n]*"


def inconnu(raison: str) -> int:
    sys.stderr.write("faux-claude : %s\n" % raison)
    return 2  # prompt inconnu


def valeur(argv: list, option: str) -> Optional[str]:
    return argv[argv.index(option) + 1] if option in argv and argv.index(option) + 1 < len(argv) else None


def emettre(d: dict) -> None:
    print(json.dumps(d, ensure_ascii=False), flush=True)


def lire(chemin: str) -> str:
    with open(chemin, encoding="utf-8", newline="") as f:
        return f.read()


def ecrire(chemin: str, texte: str) -> None:
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(texte)


def courant() -> Optional[str]:
    """Le fichier de fiches courant de CHANTIER.md du cwd — la lecture de `lire_carte` (boucle.py)."""
    for ligne in lire("CHANTIER.md").splitlines():
        if "**fichier de fiches courant**" in ligne:
            v = ligne.split(":", 1)[1].strip().split(" (")[0].strip().strip("`")
            return None if v.lower().startswith("aucun") else v
    return None


def resultat(sid: str, modele: Optional[str], cout: float, **champs) -> dict:
    r = {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 0, "num_turns": TOURS,
         "session_id": sid, "total_cost_usd": cout, "permission_denials": [],
         "modelUsage": {modele: {"costUSD": cout}} if modele else {}}
    r.update(champs)
    return r


def decouper(code: str) -> int:
    ids = ("%s1" % code, "%s2" % code)
    corps = "# Fiches\n\n## Le socle commun\n\nRien.\n\n## L'ordre des fiches\n\n%s, %s.\n\n---\n\n" % ids
    for f in ids:
        corps += FICHE % (f, f, f, "")
    texte = lire("CHANTIER.md")
    nouveau, n = re.subn(COURANT, lambda m: "%s%s.md (%s..%s)" % (m.group(1), code, ids[0], ids[1]), texte, flags=re.M)
    if n != 1:
        return inconnu("pas de ligne « fichier de fiches courant » dans CHANTIER.md")
    ecrire("%s.md" % code, corps)
    ecrire("CHANTIER.md", nouveau)
    return 0


def jouer(fiche: str, session: Optional[str] = None) -> int:
    fichier = courant()
    if not fichier:
        return inconnu("aucun fichier de fiches courant")
    if fiche in os.environ.get("VLP_FAUX_RATE", "").split(","):
        return 0
    vlp = os.environ.get("VLP_FAUX_VLP") or os.path.join(ICI, "vlp.py")
    # Le vrai claude pose l'id de sa session aux commandes qu'il lance, et `cocher` le lit.
    env = dict(os.environ, CLAUDE_CODE_SESSION_ID=session) if session else None
    # Une fiche à bloc Tentatives se coche `--resolu`, comme `skills/tache/SKILL.md` : le bloc est remplacé.
    corps = re.search(r"<!-- FICHE:%s -->(.*?)<!-- /FICHE -->" % re.escape(fiche), lire(fichier), re.S)
    resolu = ["--resolu", "faux claude"] if corps and "**Tentatives**" in corps.group(1) else []
    r = subprocess.run([sys.executable, vlp, "cocher", fichier, fiche] + resolu, capture_output=True, text=True,
                       encoding="utf-8", env=env)
    if r.returncode:
        sys.stderr.write((r.stdout + r.stderr).strip() + "\n")
        return 2
    if fiche in os.environ.get("VLP_FAUX_COMMIT", "").split(","):
        # La session de jeu qui commite malgré tout : le cas `TÊTE` de la boucle.
        for git in (["add", "-A"], ["commit", "-q", "-m", "%s : fiche %s" % (fiche, fiche)]):
            r = subprocess.run(["git"] + git, capture_output=True, text=True, encoding="utf-8")
            if r.returncode:
                sys.stderr.write((r.stdout + r.stderr).strip() + "\n")
                return 2
    return 0


def clore() -> int:
    texte = lire("CHANTIER.md")
    for motif in (COURANT, ARTEFACT):
        texte = re.sub(motif, lambda m: m.group(1) + "aucun", texte, flags=re.M)
    ecrire("CHANTIER.md", texte)
    return 0


def verdict(mots: list) -> Optional[str]:
    """Le texte de relire, ou None : le prompt n'est pas `<fiche> [--sha <sha>]`."""
    if not (len(mots) == 1 or (len(mots) == 3 and mots[1] == "--sha")):
        return None
    refus, _, causes = os.environ.get("VLP_FAUX_REFUSE", "").partition(":")
    if refus != mots[0]:
        return "ACCEPTÉE — rejoué %s, 0 écart" % mots[0]
    liste, etat, k = causes.split(","), os.environ.get("VLP_FAUX_ETAT"), 0
    if etat:   # une cause par relecture de cette fiche, ACCEPTÉE ensuite ; le motif porte son rang
        vus = json.loads(lire(etat)) if os.path.exists(etat) else {}
        k = vus.get(refus, 0)
        ecrire(etat, json.dumps(dict(vus, **{refus: k + 1})))
        if k >= len(liste):
            return "ACCEPTÉE — rejoué %s, 0 écart" % mots[0]
    cause = liste[k]
    if cause == "aucun":
        return "Je n'ai pas conclu."
    if cause not in ("fiche", "copie"):
        return None
    texte = "REFUSÉE — %s : motif factice%s" % (cause, " %d" % (k + 1) if etat else "")
    if cause == "fiche":
        texte += "\nRÉÉCRITURE : phrase de la fiche → phrase corrigée"
    return texte


def main(argv: list) -> int:
    journal = os.environ.get("VLP_FAUX_ARGV")
    if journal:
        with open(journal, "a", encoding="utf-8", newline="") as f:
            f.write(json.dumps(argv, ensure_ascii=False) + "\n")
    prompt = valeur(argv, "-p")
    if prompt is None:
        return inconnu("pas de -p")
    mots = prompt.split()
    modele = valeur(argv, "--model") or MODELE_DEFAUT
    sid = valeur(argv, "--session-id") or str(uuid.uuid4())
    texte = "joué %s · %s" % (mots[-1] if mots else "", ",".join(argv))
    if valeur(argv, "--agent") == "vlp:relecture":
        role, texte = "relire", verdict(mots)
        if texte is None:
            return inconnu("prompt de relecture inconnu : %s" % prompt)
    elif len(mots) == 2 and mots[0] == "/vlp:chantier":
        role, texte = "découper", "découpé %s" % mots[1]
    elif len(mots) == 2 and mots[0] == "/vlp:tache":
        role = "jouer"
    elif mots == ["/vlp:tache"]:
        role, texte = "clore", "chantier clos"
    else:
        return inconnu("prompt inconnu : %s" % prompt)

    emettre({"type": "system", "subtype": "init", "cwd": os.getcwd(), "session_id": sid, "model": modele,
             "tools": ["Read", "Edit", "Bash", "PowerShell"] if role == "relire" else ["Bash", "Read", "Edit", "Write", "Skill"],
             "permissionMode": valeur(argv, "--permission-mode") or "default"})
    dort = os.environ.get("VLP_FAUX_DORT")
    if dort:
        time.sleep(float(dort))
    erreur = os.environ.get("VLP_FAUX_ERREUR")
    if erreur == "coupure":
        return 1
    if erreur == "api":
        message = "There's an issue with the selected model (%s)." % modele
        emettre({"type": "assistant", "message": {"model": "<synthetic>", "role": "assistant", "type": "message",
                 "content": [{"type": "text", "text": message}]}, "session_id": sid,
                 "error": "model_not_found", "is_api_error_message": True})
        emettre(resultat(sid, None, 0.0, is_error=True, terminal_reason="api_error", result=message))
        return 1
    if erreur in ("tours", "budget"):
        sous = "error_max_turns" if erreur == "tours" else "error_max_budget_usd"
        raison = "max_turns" if erreur == "tours" else "budget_exhausted"
        emettre(resultat(sid, modele, COUT, subtype=sous, is_error=True, terminal_reason=raison, errors=[]))
        return 1
    if erreur:
        return inconnu("VLP_FAUX_ERREUR inconnue : %s" % erreur)
    limite = os.environ.get("VLP_FAUX_LIMITE")
    if limite and modele.startswith(limite):
        genre = os.environ.get("VLP_FAUX_GENRE") or "session"
        if genre not in LIMITES:
            return inconnu("VLP_FAUX_GENRE inconnu : %s" % genre)
        emettre(resultat(sid, None, 0.0, is_error=True, result=LIMITES[genre]))
        return 1

    chemin_env = os.environ.get("VLP_FAUX_ENV")
    if chemin_env:
        with open(chemin_env, "a", encoding="utf-8", newline="") as f:
            f.write(json.dumps({"role": role, "VLP_CANAL": os.environ.get("VLP_CANAL"),
                                "VLP_CARNET": os.environ.get("VLP_CARNET")}, ensure_ascii=False) + "\n")
    code = {"découper": lambda: decouper(mots[1]), "jouer": lambda: jouer(mots[1], valeur(argv, "--session-id")),
            "clore": clore, "relire": lambda: 0}[role]()
    if code:
        return code
    vu = modele
    repli = (valeur(argv, "--fallback-model") or "").split(",")[0]
    if os.environ.get("VLP_FAUX_REPLI") == "1" and repli:
        vu = repli
        emettre({"type": "system", "subtype": "model_fallback", "trigger": "model_not_found",
                 "original_model": modele, "fallback_model": repli, "session_id": sid})
    emettre({"type": "assistant", "message": {"model": vu, "role": "assistant", "type": "message",
             "content": [{"type": "text", "text": texte}]}, "session_id": sid})
    refus = [{"tool_name": "Bash"}] * int(os.environ.get("VLP_FAUX_DENIALS") or 0)
    emettre(resultat(sid, vu, COUT, result=texte, terminal_reason="completed", permission_denials=refus))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
