"""Les noms du cœur pas encore sortis, lus au moment de l'appel (REF45, option 1 tranchée par l'utilisateur le 2026-10-18).

27 des 29 sections de l'ancien `vlp_coeur.py` s'appellent en cycle : un module lit des noms d'un module chargé après
lui. Il les lit `coeur.<nom>`, jamais par import — à son import, ces noms n'existent pas encore. `coeur.noms` est
l'espace de la façade (`globals()`), posé par elle avant d'importer les modules, et rempli à mesure. Un nom d'un
module chargé avant se lit, lui, par import (REF45 à REF49). Une fonction qu'un test remplace s'appelle par son module
— `noyau.page.regenerer`, `noyau.clos.recompte`, `noyau.relecture.git_texte` — et se remplace là.
"""
from typing import Any


class Espace:
    """Un espace de noms lu à chaque accès : `coeur.champ` rend `noms["champ"]` au moment de l'appel."""

    def __init__(self):
        """Un espace vide : la façade y pose ses `globals()` avant d'importer ses modules."""
        self.noms: dict[str, Any] = {}

    def __getattr__(self, nom: str) -> Any:
        """Le nom `nom` de la façade, lu à cet instant ; absent : `AttributeError`, jamais un `KeyError`."""
        try:
            return self.noms[nom]
        except KeyError:
            raise AttributeError("coeur.%s : nom absent de la façade" % nom) from None


coeur = Espace()
