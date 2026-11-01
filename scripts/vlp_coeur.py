#!/usr/bin/env python3
"""Le code de `vlp.py` (VIT5) : `vlp.py` le lance, et son `.pyc` évite de recompiler ce module à chaque
lancement. La doc des sous-commandes vit dans `noyau/manuel.py` (`vlp.py <sous-commande> --help`), et nulle part ailleurs.
"""
# Lus par les tests à travers la façade (`mod.argparse`, `mod.hashlib`, `mod.html`, `mod.carnet`, `mod.vlp_hook`) :
# ré-exportés, pas inutiles (REF54).
import argparse  # noqa: F401
import hashlib  # noqa: F401
import html.parser  # noqa: F401

import carnet  # noqa: F401
import vlp_hook  # noqa: F401

from noyau import etat  # noqa: F401 — l'état que les tests changent, lu `etat.NOM` (REF44)
from noyau import facade   # les noms pas encore sortis, lus à l'appel par les modules (REF45)

facade.coeur.noms = globals()

# La façade ré-exporte (REF45), dans cet ordre : un module lit par import les noms des modules chargés avant lui.
from noyau.commun import *
from noyau.fiches import *
from noyau.carte import *
from noyau.sessions import *
from noyau.page import *
from noyau.notes import *
from noyau.feuille import *
from noyau.clos import *
import noyau.page  # `noyau.page.regenerer` : un test la remplace là (REF46)
from noyau.relecture import *
from noyau.hooks import *
from noyau.niveau import *
from noyau.bac import *
import noyau.relecture  # noqa: F401 — `noyau.relecture.git_texte` : un test la remplace là (REF47)
from noyau.nuit import *
from noyau.clore import *
from noyau.ouvrir import *
from noyau.matin import *
from noyau.rapport import *
from noyau.ordre import *
from noyau.cli import *
