"""REF12 : des règles écrites, garanties par un test (choix `Q7` de la note `122` : une consigne est une demande, un
script une garantie). Chaque test porte la règle qu'il remplace ; la phrase d'origine renvoie ici. L'inventaire
complet, scriptable ou non : note `122`, section « Les règles écrites, scriptables ou non (`REF12`) »."""
import glob
import os
import re

from aides import RACINE, lire

COMMANDES = sorted(glob.glob(os.path.join(RACINE, "skills", "*", "SKILL.md")))
POSITIONNEL = re.compile(r"\$(?:[0-9]|ARGUMENTS\[)")   # `$1`, `$ARGUMENTS[0]` : substitués avant que le modèle lise


def test_arguments_seuls():
    """`CHANTIER.md`, « Contraintes d'écriture » : `$ARGUMENTS` sur une ligne à lui ; jamais `$1` ni `$2`."""
    assert len(COMMANDES) >= 8, "regles : les commandes du kit se trouvent\n" + str(COMMANDES)
    fautes = ["%s:%d" % (os.path.relpath(c, RACINE), n) for c in COMMANDES
              for n, l in enumerate(lire(c).splitlines(), 1)
              if POSITIONNEL.search(l) or ("$ARGUMENTS" in l and l.strip() != "$ARGUMENTS")]
    assert fautes == [], "regles : $ARGUMENTS seul sur sa ligne, jamais $1 ni $2\n" + "\n".join(fautes)


def test_pas_de_sed_sur_une_commande():
    """`CHANTIER.md`, « Contraintes d'écriture » : une commande ne découpe jamais une autre commande au `sed` — ce qui
    est partagé vit dans un fichier ou un script commun."""
    fautes = ["%s:%d" % (os.path.relpath(c, RACINE), n) for c in COMMANDES
              for n, l in enumerate(lire(c).splitlines(), 1) if re.search(r"\bsed\b[^\n]*(?:SKILL\.md|skills/)", l)]
    assert fautes == [], "regles : aucune commande ne découpe une autre au sed\n" + "\n".join(fautes)


def test_plugin_root_hors_des_donnees():
    """`CLAUDE.md`, règle 4 : `${CLAUDE_PLUGIN_ROOT}` ne vit que dans le texte des commandes et `hooks/hooks.json` —
    un gabarit est un fichier de données, que rien ne substitue."""
    gabarits = [f for f in glob.glob(os.path.join(RACINE, "templates", "**", "*"), recursive=True) if os.path.isfile(f)]
    assert gabarits, "regles : les gabarits se trouvent"
    fautes = [os.path.relpath(f, RACINE) for f in gabarits
              if "CLAUDE_PLUGIN_ROOT" in lire(f)]
    assert fautes == [], "regles : aucun gabarit ne porte ${CLAUDE_PLUGIN_ROOT}\n" + "\n".join(fautes)
