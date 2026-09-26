# Chantier courant — vlp (le kit Claude-vlpWorkflow)

> Fichier lu **en entier** par `/vlp:chantier` et `/vlp:tache`, depuis la racine du
> projet. C'est la seule table à tenir : rien à mettre à jour ailleurs quand un
> chantier s'ouvre ou se clôt. Garde-le sous le seuil de `scripts/vlp.py` : `renvois` avertit.
> Les libellés en gras se recopient **à l'identique** : ils sont lus tels quels.

- **alias** : vlp
- **kit** : ce dossier même — le projet est le kit. Chez znorr :
  C:/Users/znorr/Documents/ProgPerso/Claude-vlpWorkflow, lié dans ~/.claude/skills/vlp
- **contexte** : context AI/
- **méthode** : methode-chantier.md, à la racine du kit — il voyage avec le plugin
- **chantiers possibles** : context AI/08-etat.md
- **fichier d'état** : context AI/08-etat.md
- **index** : context AI/00-INDEX.md
- **fichier de fiches courant** : context AI/74-voisines.md (VOI1..VOI6)
- **artefact feuille de route** : https://claude.ai/code/artifact/ff1fc060-daca-486f-b4c6-e1f55114c0f7
- **artefact du chantier** : https://claude.ai/artifact/VRWQkwQen7EJRRdGZx8Xem
- **livraison** : aucune — le plugin est chargé en place ; `/reload-plugins` pour
  que la session en cours voie une modification
- **vérification** : geste de l'utilisateur — rejouer la commande modifiée sur un
  projet équipé, et regarder ce qu'elle fait

## Contraintes d'écriture

Les règles que toute fiche respecte, quel que soit son sujet.

- Une règle vit à un seul endroit — un nombre aussi : on la référence, on ne la
  recopie jamais (le kit a souffert de six copies divergentes).
- Une commande est autoportante : chaque étape nomme ce qu'elle ouvre, et rien
  d'autre. Elle ne découpe jamais une autre commande au `sed` : ce qui est
  partagé vit dans un fichier ou un script commun.
- Le déterministe s'écrit dans `scripts/`, testé, et la commande l'appelle en
  un tour ; la prose ne décrit pas un algorithme.
- Tout ajout dans une commande se paye à chaque exécution : court, ou pas du tout.
- `$ARGUMENTS` sur une ligne à lui ; jamais `$1` ni `$2` dans la prose — ils
  sont substitués avant que le modèle lise.
- Le texte des commandes est en français ; chemins en barres obliques, jamais
  un chemin de machine.

## Chantiers clos — dans l'index, pas ici

Chacun a sa ligne dans l'**index** ; sa page reste sur la feuille de route.

Lettres de fiche déjà prises : E (Enchaîner les fiches), M (Mesurer les tokens), C (Afficher la conso), T (Compter les tours), B (Corriger les bugs de l'audit), R (Réduire les tours de `/vlp:tache`), S (Un script `vlp.py` pour la mécanique), H (Hooks du kit), V (Evals du plugin), D (Fusionner la doctrine), I (Un projet neuf qui ne ment pas), K (Migrer `commands/` → `skills/`), N (`/vlp:enchainer` : réparer ou retirer), L (`/vlp:enchainer` : alléger le chef), P (Un lanceur Python sans accolade), A (Une fiche visuelle arrête `/vlp:enchainer`), G (Le kit sans Git Bash), W (Evals sous WSL2), X (Le kit sans `sh`), F (La feuille de route par script), O (Ouvrir et clore par script), J (Des fichiers de tête qui ne grossissent plus), Y (Le kit entier sans `sh`), U (`/vlp:tache` sans refus sous PowerShell), Q (`/vlp:enchainer` sans Git), Z (Une GARDE au lieu d'un traceback), NIV (Remettre les projets équipés à niveau), REP (Réparer les pages publiées), CPT (Un coût juste, fiche par fiche et sous-agents compris), SAG (Le sous-agent ne bute plus sur 30 tours), FIL (Le filet tire après tout outil), CAS (Le chef relit la case avant de commiter), VAL (Le contrôle avant commit ne se saute plus), FIN (Le coût juste, aux deux bords du chantier), TAR (Ce que vlp.py écrit, il le relit), PLA (La plage des fiches suit le fichier), MTK (mesure-tokens.py se lit et se borne en ligne de commande), CAD (Le cadrage compte dans le coût du chantier), ZER (Un vieux chantier ne se recompte plus à zéro), REV (Relire chaque fiche avant son commit), CON (Le contrat du sous-agent, vérifié à sa sortie), GLO (Le CLAUDE.md de l'utilisateur dans le sous-agent), GAR (Le gardien renvoie pour de vrai), UNI (Un seul chiffre par clôture), PYT (Un hook n'agit qu'une fois), RLG (Le gardien derrière le relecteur), FOR (La forme du sous-agent, pour de vrai), JUG (Le gardien ne juge que la fin du message, pas tout le texte), REC (Recompter les chantiers clos au coût juste), ESS (Les essais `claude -p` dans le coût), ESD (Les essais d'un chantier sans découpe, puis republier), APC (Ce que le chiffre de clôture ne voit pas), LEC (`/vlp:chantier` ne lit plus l'état en entier), ENC (`/vlp:enchainer` rejoue une fiche floue), REL (Le relecteur ne voit pas la suite), FFE (Le relecteur ne lit plus le fichier de fiches entier), EST (L'estimé face au réel, à chaque clôture), BAC (Un bac d'essai par script), EVF (Le filet en eval rejouable), RAT (Un `Read` raté réveille-t-il le filet ?), SON (Rejouer un hook à la main sans le tampon), TOU (Le filet n'avertit qu'une fois par tour). Un nouveau chantier en choisit un autre —
**trois majuscules** depuis le 2026-09-17 (l'alphabet à une lettre est épuisé), jamais
réemployées. `/vlp:chantier` le propose, l'utilisateur tranche ; c'est cette ligne qui rend le refus possible.
