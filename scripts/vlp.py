#!/usr/bin/env python3
"""La mécanique du kit vlp : ce que les commandes faisaient au `sed` et à l'`awk`.

Une ligne par sous-commande, celle de `vlp.py --help` ; son détail : `vlp.py <sous-commande> --help`, tiré de
`noyau/manuel.py` (REF36 — `tests/test_manuel.py` compare ces lignes aux siennes).

Sous-commandes — chacune a sa photo dans `tests/test_photos_vlp.py` (REF7) ; une sous-commande neuve sans photo,
ni raison de la sauter, fait échouer la suite :

- `carte` — la carte d'un projet, injectée avant le 1er tour d'une commande
- `extraire` — une fiche entre ses marqueurs, puis son compte de lignes
- `socle` — le socle commun d'un fichier de fiches, puis son compte de lignes
- `sessions` — les ids des lignes `**Session**` d'un fichier de fiches, dédoublonnés
- `cout` — le coût des sessions d'un fichier de fiches, coupé aux commits de fiche
- `essai` — déclare un essai `claude -p` lancé hors d'un bac
- `compteur` — où passe le temps, fiche par fiche, aux plages de `cout`
- `valider` — les écarts d'un fichier de fiches, puis son bilan
- `lancables` — les fiches non cochées qui peuvent partir ensemble, chacune dans son worktree
- `commiter` — coche une fiche et commite ses seuls chemins changés
- `lignes` — le nombre de lignes de fichiers, puis les seuils
- `equiper` — ce que `/vlp:init` regarde dans un dossier
- `lire` — imprime des fichiers du kit, chemins relatifs à sa racine
- `cocher` — coche une fiche ; ou lit sa case, la refuse, note la session d'un rôle de la nuit
- `relecture` — ce que lit le relecteur : l'avant, l'après, le socle, la fiche et le diff
- `page` — régénère la page du chantier depuis le fichier de fiches
- `figer` — le hook qui fige les tests existants pendant une fiche
- `hook` — le hook qui valide un fichier de fiches après son écriture
- `filet` — le hook qui avertit un sous-agent proche de son plafond de tours
- `etat` — le nom du fichier d'état, ou un texte ajouté à sa fin
- `renvois` — les fichiers que l'index et le routage nomment sans qu'ils existent
- `comparer` — le texte visible perdu ou ajouté entre deux pages
- `niveau` — en quoi un projet équipé a dérivé du kit ; `--ecrire` corrige le mécanique
- `feuille` — régénère la feuille de route d'un projet
- `trier` — le tri du soir de la TODO, par script
- `plan` — écrit ou lit le plan du soir, dans le fichier des nuits
- `matin` — fusionne les branches de la nuit ; avec `--rapport`, le rapport du matin
- `fusionner` — fusionne une branche dans celle du dossier, ou celle d'une fiche jouée en worktree
- `joints` — recopie `vlp.css` et `vlp.js` dans un dossier, et rend la ligne `FILES`
- `clore` — les écritures mécaniques de la clôture d'un chantier
- `oter` — retire un chantier de la TODO du fichier d'état
- `archiver` — les lignes closes de l'index vont à son archive
- `archive` — les lignes closes de la feuille de route vont à `archive-clos.html`
- `abri` — le `.md` à côté d'une page : résultat, notes, journal, bilan
- `ouvrir` — les écritures mécaniques de l'ouverture d'un chantier
- `contrat` — le contrat d'`agents/fiche.md`, lu dans des transcriptions de sous-agent
- `forme` — la forme et le poids de transcriptions de sous-agent
- `gardien` — le hook du contrat des sous-agents
- `ouverts` — les chantiers ouverts d'un dossier de contexte
- `postit` — le post-it d'un worktree, posé pour un sous-agent
- `pause` — met un chantier en pause
- `vigile` — une page cassée ne part pas : le hook, ou la vérification d'une page
- `chef` — la page à cartes, remplie par script
- `attente` — la liste des pages que la limite du jour a refusées, et son hook
- `repeindre` — repeint au style du kit la page de chaque chantier clos
- `lien` — écrit l'URL d'une page dans la section `## Lien` de son `.md`
- `liens` — pose le lien de chaque chantier clos dans le `.md` de sa page
- `recompter` — recompte le coût des chantiers clos ; n'écrit qu'avec `--ecrire`
- `prix` — pose le prix en $ de chaque chantier clos
- `bac` — pose le bac d'essai, et dit comment le lancer
- `claude` — le `claude` que le kit lance
- `transcription` — les comptes de la transcription d'un sous-agent
- `kit-essai` — copie le kit avec un plafond de tours bas
- `servir` — un serveur local qui sert les pages sans cache
- `apercu` — l'entrée de `launch.json` qui sert les pages du projet
- `mutant` — le mutant d'une fiche de code, joué dans une copie
- `symboles` — les lignes de chaque fonction ou classe d'un fichier Python
- `ordre` — l'enchaînement entre projets : ses données, sa page, ou sa base
- `cahier` — le cahier d'essais, bâti d'un `.md`
- `rapide` — le contrôle rapide d'une fiche du kit, avant la suite entière
- `nuits` — une note au carnet de nuit, ou une leçon au fichier des nuits
- `sante` — la santé du code, fonction par fonction : la base et le cliquet

Aiguillées avant le cœur, sans le charger — leur détail est la docstring de leur module :

- `couverture` — juge la couverture des lignes changées du commit indexé
- `concernes` — les tests qui exécutent ces fonctions
- `conserve` — aucune ligne de texte ne se perd quand une doc se découpe ou se range
- `retraits` — un test retiré ou affaibli, vu au commit

Les lignes des chantiers clos — lues ou écrites par `clore`, `recompter`, `prix`, `liens`,
`repeindre` et le prix moyen d'`ouvrir` — vivent dans `<contexte>/artefacts/archive-clos.html`
s'il existe, sinon dans la feuille ; le graphique reste sur la feuille (`page_clos`, chantier ARC).
`clore` y refait alors le bloc `ZONE:archive` de la feuille et met l'archive en liste d'attente
(`ATTENTE archive-clos.html — <URL>`), ou dit `GARDE:` sans champ **artefact archive**. Sous `VLP_NUIT=1`,
`clore` y met aussi la page du chantier et la feuille, qu'une session `claude -p` ne peut pas publier ; `matin`
imprime les `ATTENTE=` du projet avant sa ligne `MATIN` (NPB1).

Python 3 sans dépendance, zéro appel modèle.

Un hook (`hook`, `filet`, `gardien`, `vigile`, `attente hook`) n'agit qu'une fois quand `python3` et `py` le lancent
tous deux : le premier qui crée `<TAMPON_HOOKS>/vlp-hook-<sha1 du nom et de l'entrée>` agit, l'autre se tait
(chantier PYT) — sans charger le cœur : le tri vit dans `vlp_hook.py`, lu avant `vlp_coeur` (VIT8). Rejoué à la main, `VLP_SANS_TAMPON=1` dans l'environnement saute le tampon :
chaque lancement agit (chantier SON).
"""
import io
import sys

if __name__ == "__main__":
    # Sous Windows, la console n'est pas en UTF-8 : sans ceci, les accents
    # sortent illisibles.
    for flux in (sys.stdin, sys.stdout, sys.stderr):
        try:
            if isinstance(flux, io.TextIOWrapper):
                flux.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.dont_write_bytecode = False     # le .pyc du cœur sert même sous PYTHONDONTWRITEBYTECODE (VIT5)
    if sys.argv[1:2] == ["couverture"]:     # REF8 : son module à lui, hors du cœur au plafond de taille (REF9)
        import couverture
        sys.exit(couverture.principal(sys.argv[2:]))
    if sys.argv[1:2] == ["concernes"]:      # REF13 : son module à lui, hors du cœur
        import concernes
        sys.exit(concernes.principal(sys.argv[2:]))
    if sys.argv[1:2] == ["retraits"]:       # REF11 : lancé à chaque commit, sans charger le cœur
        import retraits
        sys.exit(retraits.principal(sys.argv[2:]))
    if sys.argv[1:2] == ["conserve"]:       # REF16 : son module à lui, hors du cœur
        import conserve
        sys.exit(conserve.principal(sys.argv[2:]))
    import vlp_hook
    triee = vlp_hook.trier(sys.argv[1:])
    if triee == "":                     # un hook déjà pris par l'autre lanceur : sortir sans charger le cœur (VIT8)
        sys.exit(0)
    import vlp_coeur
    sys.exit(vlp_coeur.main(sys.argv[1:], entree=triee))
