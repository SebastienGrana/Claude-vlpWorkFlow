#!/usr/bin/env python3
"""Le carnet de nuit : un fichier JSONL par nuit, écrit par plusieurs processus à la fois.

Sans dépendance ni appel modèle ; `vlp.py` et `boucle.py` le chargent par `import carnet`.
Chemin : `<--git-common-dir absolu>/vlp-nuit/<date>.jsonl` (`du_jour`) — dans `.git`, donc ni
suivi ni hook. Une ligne = un objet JSON qui porte les 21 clés de `CLES` (absente : `null`),
les 17 du socle de NUI1 plus `usd_kit`, `tours_kit`, `note`, `stop` ; une clé inconnue est
refusée (`ValueError`). `lire` saute la ligne illisible (processus tué en pleine écriture) ;
`ajouter` ouvre une ligne neuve si la dernière n'est pas finie.

Ajout sous verrou `<carnet>.verrou`, créé en `O_CREAT|O_EXCL` et qui porte le PID. Verrou tenu :
attendre `PAS`, réessayer. Plus vieux que `VERROU_AGE` secondes (date du fichier) : cassé, et une
ligne `garde` le dit (PID, âge) avant la ligne ajoutée.

`est_session(ligne)` : `role` posé, `note` et `stop` nuls — seul tri des lignes de session.
`cout_de(ligne, plafonds)` : ce qu'une ligne de session a coûté — son `usd_cli`, à défaut son `usd_kit`
(la session coupée, mesurée dans sa transcription, NUI8), à défaut le plafond de son rôle dans `plafonds`
(`{rôle: $}`, passé par boucle.py depuis sa table `ROLES`, jamais recopié ici ; sans lui, 0). Un `0.0` est un
coût, pas une absence. `pot(lignes, plafonds)` : la somme de `cout_de` sur les lignes de session, tous
canaux. `borne(...)` : le texte de la borne atteinte (pot ≥ borne en $, ou chantier absent du carnet qui veut
partir alors que le nombre de chantiers est déjà ≥ borne), sinon `None`. `stop(...)` écrit la ligne `stop` ;
`stop_de(lignes)` rend la dernière raison. `VLP_CARNET` et `VLP_CANAL` : ce que la fille reçoit.

Avant chaque session `--nuit`, boucle.py écrit une `note` `depart <rôle>` (canal, chantier, fiche, session) :
hors `est_session`, donc hors pot et hors mesure ; sans ligne de session au même id, la session a été coupée.
"""
import json
import os
import subprocess
import time
from typing import Optional

CLES = ("nuit", "canal", "chantier", "role", "fiche", "modele_demande", "modeles_vus", "tours_cli",
        "usd_cli", "duree_s", "issue", "refus_n", "cause", "reecriture", "garde", "plugin_retard",
        "session", "usd_kit", "tours_kit", "note", "stop")
VERROU_AGE = 30   # secondes : au-delà, le verrou est cassé — seul endroit du nombre
PAS = 0.02        # secondes d'attente entre deux essais de verrou
ENV_CARNET, ENV_CANAL = "VLP_CARNET", "VLP_CANAL"


def du_jour(dossier: str, jour: Optional[str] = None) -> Optional[str]:
    """Le chemin du carnet de `jour` (défaut : aujourd'hui) pour le dépôt de `dossier`, ou None."""
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=dossier,
                           capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    commun = r.stdout.strip()
    if r.returncode != 0 or not commun:
        return None
    return os.path.join(os.path.abspath(commun), "vlp-nuit", (jour or time.strftime("%Y-%m-%d")) + ".jsonl")


def nuit_de(carnet: str) -> str:
    """Le nom de la nuit : celui du fichier, sans `.jsonl`."""
    return os.path.splitext(os.path.basename(carnet))[0]


def ligne(champs: dict) -> dict:
    inconnues = sorted(set(champs) - set(CLES))
    if inconnues:
        raise ValueError("clé inconnue du carnet : %s" % ", ".join(inconnues))
    return {k: champs.get(k) for k in CLES}


def lire(carnet: str) -> list:
    try:
        with open(carnet, encoding="utf-8", errors="replace") as f:
            brutes = f.read().splitlines()
    except OSError:
        return []
    lignes = []
    for brute in brutes:
        try:
            d = json.loads(brute)
        except ValueError:
            continue
        if isinstance(d, dict):
            lignes.append(d)
    return lignes


def finit_mal(carnet: str) -> bool:
    """Vrai si le fichier existe et que sa dernière ligne n'est pas terminée."""
    try:
        with open(carnet, "rb") as f:
            f.seek(-1, os.SEEK_END)
            return f.read(1) != b"\n"
    except OSError:
        return False


def ecrire(carnet: str, d: dict) -> None:
    texte = ("\n" if finit_mal(carnet) else "") + json.dumps(d, ensure_ascii=False) + "\n"
    with open(carnet, "a", encoding="utf-8", newline="") as f:
        f.write(texte)


def casser(verrou: str) -> Optional[tuple]:
    """(PID, âge en s) si le verrou a plus de `VERROU_AGE` s et vient d'être retiré, sinon None."""
    try:
        vu = os.path.getmtime(verrou)
        age = time.time() - vu
        if age <= VERROU_AGE:
            return None
        with open(verrou, encoding="utf-8") as f:
            pid = f.read().strip()
        if os.path.getmtime(verrou) != vu:
            return None
        os.remove(verrou)
    except OSError:
        return None
    return pid, int(age)


def prendre(verrou: str) -> Optional[tuple]:
    """Crée le verrou, en attendant s'il est tenu. Rend (PID, âge) du verrou cassé, ou None."""
    casse = None
    while True:
        try:
            fd = os.open(verrou, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, PermissionError):   # Windows : PermissionError tant qu'un retrait finit
            casse = casse or casser(verrou)
            time.sleep(PAS)
            continue
        with os.fdopen(fd, "w") as f:
            f.write(str(os.getpid()))
        return casse


def ajouter(carnet: str, **champs) -> None:
    """Ajoute une ligne au carnet, sous verrou. Clé inconnue : `ValueError`, rien d'écrit."""
    contenu = ligne(champs)
    os.makedirs(os.path.dirname(carnet), exist_ok=True)
    verrou = carnet + ".verrou"
    casse = prendre(verrou)
    try:
        if casse:
            ecrire(carnet, ligne({"nuit": champs.get("nuit"), "canal": champs.get("canal"),
                                  "garde": "verrou cassé : PID %s, âge %d s" % casse}))
        ecrire(carnet, contenu)
    finally:
        try:
            os.remove(verrou)
        except OSError:
            pass


def stop(carnet: str, canal: Optional[str], raison: str) -> None:
    ajouter(carnet, nuit=nuit_de(carnet), canal=canal, stop=raison)


def noter(carnet: str, canal: Optional[str], texte: str) -> None:
    ajouter(carnet, nuit=nuit_de(carnet), canal=canal, note=texte)


def stop_de(lignes: list) -> Optional[str]:
    """La raison du dernier `stop` du carnet, d'un canal quelconque, ou None."""
    raisons = [str(d["stop"]) for d in lignes if d.get("stop") is not None]
    return raisons[-1] if raisons else None


def est_session(d: dict) -> bool:
    return d.get("role") is not None and d.get("note") is None and d.get("stop") is None


def cout_de(d: dict, plafonds: Optional[dict] = None) -> float:
    """Le coût d'une ligne de session : `usd_cli`, à défaut `usd_kit`, à défaut le plafond de son rôle, sinon 0."""
    for cle in ("usd_cli", "usd_kit"):
        if d.get(cle) is not None:
            return d[cle]
    return (plafonds or {}).get(d.get("role"), 0)


def pot(lignes: list, plafonds: Optional[dict] = None) -> float:
    return round(sum(cout_de(d, plafonds) for d in lignes if est_session(d)), 6)


def borne(lignes: list, chantier: str, borne_usd: Optional[float], borne_chantiers: Optional[int],
          plafonds: Optional[dict] = None) -> Optional[str]:
    """Le texte de la borne atteinte pour `chantier` qui veut partir, ou None."""
    p = pot(lignes, plafonds)
    if borne_usd is not None and p >= borne_usd:
        return "pot %.4f $ ≥ borne %.4f $" % (p, borne_usd)
    vus = {d.get("chantier") for d in lignes if est_session(d) and d.get("chantier")}
    if borne_chantiers is not None and chantier not in vus and len(vus) >= borne_chantiers:
        return "%d chantiers ≥ borne %d (%s absent)" % (len(vus), borne_chantiers, chantier)
    return None
