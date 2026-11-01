"""`cocher` sur un bloc **Tentatives** : les deux cas de la ligne `SOL` de la TODO (REF32), par `vlp.py cocher` comme
le chef l'appelle.

(1) Un refus, puis un blocage qui écrase sa ligne `Erreur :` : le bloc soldé ne garde aucun motif, plutôt que celui
d'un refus plus ancien. (2) Une tête dont la parenthèse porte un mot qui contient « résolu » (« irrésolu ») reste
ouverte : `cocher --refuser` ne la récrit pas.
"""
from aides import appel, ecrire, lire


def fiche(bloc):
    """Un fichier de fiches d'une seule fiche `W1` non cochée, `bloc` sous son titre."""
    return "# Fiches\n\n## W1 [ ] — Une fiche\n\n%s\n**Dépend de** : rien.\n" % "".join(l + "\n" for l in bloc)


def test_bloc_solde_apres_refus_puis_blocage_sans_vieux_motif(tmp_path, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    f = str(tmp_path / "ctx" / "01-w.md")
    ecrire(f, fiche(["**Tentatives** (2026-01-01) — non résolu.", "Refus soldés : 1 · dernier : m1",
                     "2. FAITE refusée à la relecture.", "3. piste X", "Erreur : blocage Y"]))
    code, _ = appel(["cocher", f, "W1", "--resolu", "repris", "--date", "2026-01-02"])
    assert code == 0
    assert lire(f) == ("# Fiches\n\n## W1 [x] — Une fiche\n\n**Tentatives** (2026-01-02) — résolu par : repris\n"
                       "Refus soldés : 2\n\n**Dépend de** : rien.\n")


def test_tete_irresolu_reste_ouverte_au_refus(tmp_path, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    f = str(tmp_path / "ctx" / "01-w.md")
    tete = "**Tentatives** (2026-01-01, irrésolu hier) — non résolu."
    ecrire(f, fiche([tete, "1. piste X", "Erreur : blocage Y"]))
    code, _ = appel(["cocher", f, "W1", "--refuser", "motif", "--date", "2026-01-05"])
    assert code == 0
    assert lire(f) == fiche([tete, "1. piste X", "2. FAITE refusée à la relecture.", "Erreur : motif"])
