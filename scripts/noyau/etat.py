"""L'état que les tests changent (REF44 ; plan de `REF18`, note `122`, « Les règles de la découpe »).

Le cœur le lit `etat.NOM` ; un test le change `mod.etat.NOM = …`. Jamais `from etat import NOM` : la copie
importée resterait figée, et le test changerait un nom que le code ne lit plus.
"""
import os

import vlp_hook

KIT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # scripts/noyau/ → le kit
GIT = "git"     # un test le remplace pour simuler un poste sans Git
TAMPON_HOOKS = vlp_hook.TAMPON
GABARIT_ORDRE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "templates", "ordre.html")
LIMITE_DOC_DB = 256 * 1024   # octets d'un document `db` : contrat d'artefact 0.2.75, db.d.ts, « at most 256 KiB serialized »
SOURCE_ORDRE = os.path.join(KIT, "context AI", "ordre.md")   # `None` : clore ne la refait pas (la suite de tests)
_mesure = None   # `mesure-tokens.py`, chargé une fois par `mesure()` du cœur
