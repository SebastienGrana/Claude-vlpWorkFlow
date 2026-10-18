#!/usr/bin/env python3
"""Le code de `vlp.py` (VIT5) : `vlp.py` le lance, et son `.pyc` évite de recompiler ce module à chaque
lancement. La doc des sous-commandes vit dans la docstring de `vlp.py`, et nulle part ailleurs.
"""
import argparse
import collections
import datetime
import fnmatch
import glob
import hashlib
import html.parser
import io
import json
import os
import re
import shlex
import statistics
import sys
import tempfile
import time
import unicodedata

import carnet
import vlp_hook

from noyau import etat   # l'état que les tests changent, lu `etat.NOM` (REF44)
from noyau import facade   # les noms pas encore sortis, lus à l'appel par les modules (REF45)

facade.coeur.noms = globals()

from noyau.commun import *     # noqa: E402,F403 — la façade ré-exporte (REF45)
from noyau.fiches import *     # noqa: E402,F403
from noyau.carte import *      # noqa: E402,F403
from noyau.sessions import *   # noqa: E402,F403
from noyau.page import *        # noqa: E402,F403
from noyau.notes import *       # noqa: E402,F403
from noyau.feuille import *     # noqa: E402,F403
from noyau.clos import *        # noqa: E402,F403
import noyau.page   # noqa: E402 — `noyau.page.regenerer` : un test la remplace là (REF46)
from noyau.relecture import *   # noqa: E402,F403
from noyau.hooks import *       # noqa: E402,F403
from noyau.niveau import *      # noqa: E402,F403
from noyau.bac import *         # noqa: E402,F403
import noyau.relecture   # noqa: E402 — `noyau.relecture.git_texte` : un test la remplace là (REF47)
from noyau.nuit import *        # noqa: E402,F403
from noyau.clore import *       # noqa: E402,F403
from noyau.ouvrir import *      # noqa: E402,F403
from noyau.matin import *       # noqa: E402,F403
from noyau.rapport import *     # noqa: E402,F403
from noyau.ordre import *       # noqa: E402,F403
from noyau.cli import *         # noqa: E402,F403
