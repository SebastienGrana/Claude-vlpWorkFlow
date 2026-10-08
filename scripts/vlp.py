#!/usr/bin/env python3
"""La mécanique du kit vlp : ce que les commandes faisaient au `sed` et à l'`awk`.

Sous-commandes :

- `carte [dossier]` — la carte d'un projet, à injecter avant le 1er tour d'une
  commande. Remonte jusqu'au premier `CHANTIER.md`. Trouvé : `PROJET=<racine>`,
  le fichier en entier, une ligne `ATTENTE=<page> <url>` par page de la liste
  d'attente (`attente`, sauf avec `--relecteur`), `NUIT=1` si `VLP_NUIT` vaut `1` (la nuit : toute autre
  valeur, absente, ou `--relecteur` : rien — chantier NUI), `PLUGIN_RETARD=<n> … merge --ff-only <branche>` si
  le plugin chargé n'a pas le code de ce worktree du kit (`retard_plugin`, chantier ESR, sauf avec
  `--relecteur`), une ligne `AILLEURS=<code> <dossier>` par chantier courant d'un autre worktree (`chantiers_ailleurs`,
  NUI28, sauf avec `--relecteur`), puis — si un fichier de fiches est courant — ses titres
  de fiches numérotés, `PROCHAINE=<fiche>` (la première non cochée, dans l'ordre
  du fichier) ou `PROCHAINE=aucune`, et une `GARDE` si le fichier a des lignes
  mais aucun titre au format attendu. Aucun fichier courant : pour chaque
  chemin `.md` de la ligne **chantiers possibles** (backticks ôtés, prose
  ignorée ; sans backticks, le disque tranche où le chemin commence), l'en-tête
  `--- TODO : <chemin> (lignes A–B) ---` suivi du texte de la section TODO (du
  premier titre qui contient « TODO » jusqu'avant le titre suivant), ou
  `TODO=absente <chemin>`, ou `GARDE:` s'il est introuvable. Ligne absente :
  `TODO=absente (pas de ligne « chantiers possibles »)`. Puis le format des
  fiches : premier chemin de la ligne **méthode**, dans le projet sinon sous le
  kit, de `## Le fichier de fiches` jusqu'avant le titre qui suit `## Les deux
  formes de critère de fin` — `--- méthode : <chemin> (lignes A–B) ---` et le
  texte, ou `METHODE=absente <chemin>` si un titre manque, ou `GARDE:`.
  Pas trouvé : une ligne `VOISIN=` par sous-dossier équipé, avec son alias, ou
  `AUCUN_PROJET`. Sort toujours 0 : la commande lit la sortie, elle ne doit pas
  se faire refuser l'injection. `--python NOM` (les injections des skills : `"py -3"`, `python3` au relais ;
  VIT24) : une ligne vide, `PYTHON=NOM`,
  puis la carte, et un tampon dans le dossier temporaire ; `--relais` en plus :
  n'écrit rien si un tampon de moins de `RELAIS_SECONDES` existe (le premier
  Python a déjà répondu), sans le retirer. `--relecteur` : ni titres de fiches,
  ni `PROCHAINE=`, ni l'étendue `(X1..X3)` du fichier courant — le relecteur ne voit pas la suite (chantier REL).
  `--session-neuve` (l'injection de `/vlp:tache` seule) : après `PROCHAINE=`, `AVERTISSEMENT: session déjà notée
  dans ce fichier de fiches (<cadrage, fiches>) — /clear d'abord …` si l'id de `CLAUDE_CODE_SESSION_ID` est sur une
  ligne `**Session**` du fichier courant ; id vide ou absent, ou `VLP_NUIT=1` : rien (VIT20).
  `--enchaine` (l'injection de `/vlp:enchainer` seule) : pose la marque `vlp-enchaine-<id>` du même id dans le
  dossier temporaire, à chaque appel, relais compris (id hors chiffres, lettres et tirets : rien) ; cette marque
  fait taire l'`AVERTISSEMENT:` pour sa session (ARP3).
- `extraire <fichier> <fiche>` — la fiche entre ses marqueurs, marqueurs
  compris, puis `--- fiche, lignes : N`. Sans marqueurs, repli sur le titre
  jusqu'au premier `---`, annoncé par une `GARDE`. Absente : sort 1. Critère
  `(visuel)` : une ligne `ARRÊT:` avant le compte.
- `socle <fichier>` — de `## Le socle commun` (compris) à `## L'ordre des
  fiches` (exclu), puis `--- socle, lignes : N`. Vide : sort 1.
- `sessions <fichier>` — un id de ligne `**Session**` par ligne, dédoublonnés,
  dans l'ordre du fichier.
- `cout <fichier> [--session]` — `mesure-tokens.py` sur toutes les sessions du
  fichier, celles des fiches et celle du cadrage, que `ouvrir` note en tête (aucune :
  `SESSIONS 0 — pas de total`, sort 0), coupées aux commits comme la page : `DÉCOUPE
  aux commits de fiche`, une ligne par fiche, `hors fiches`, `TOTAL (fiches + hors
  fiches)` — aucun tour gardé : `GARDE: découpe à zéro` ; un fichier clos s'arrête à son
  dernier appel `vlp.py clore` — lancé, pas cité dans un texte (`lance_clore`) —, le chiffre que
  `clore` inscrit (`decouper`), et sa fiche sans commit au commit suivant qui nomme le préfixe
  (`plages`). Sans Git, sans commit qui
  nomme le préfixe, ou clos sans commit de fiche : `DÉCOUPE aucune — <raison>`, puis
  les tables des sessions entières. `--session` : `SESSION=<CLAUDE_CODE_SESSION_ID>`,
  puis (id non vide) la table de cette session seule, et celle de cette session plus
  celles du fichier. `--a-clore` : après `TOTAL`, `à clore` — le total si la dernière
  plage hors fiches s'arrêtait au dernier appel `vlp.py clore` qu'elle contient — et
  `après clore`, la différence ; sans cet appel, une `GARDE:` et pas de ligne. Les essais
  d'une session : ceux de ses bacs, et ceux qu'`essai` déclare (`essais_de`).
- `essai <motif> [--session <id>]` — déclare, une fois, un essai `claude -p` lancé hors d'un
  bac : une ligne `<session> <motif>` au registre `~/.claude/vlp-essais.txt` ; le motif est un
  nom de dossier de `~/.claude/projects/`, glob permis ; la session, `CLAUDE_CODE_SESSION_ID`
  par défaut. `ESSAI <session> <motif> · <n> dossier(s) · <m> transcript(s)` ; sans session,
  ou un motif avec `/`, `\\`, `..` ou un blanc : `GARDE:`, rien d'écrit, sort 1 (MET2).
- `compteur <fichier> [<fiche>…] [--recoupe]` — où passe le temps, aux plages de `cout` :
  `COMPTEUR aux commits de fiche`, une ligne par fiche — durée de commit à commit, actif
  = modèle + outils + attente + autre (chaque écart à la part de la ligne qui le ferme),
  outils par sorte en minutes (appels), tours et $ de `cout`, garde-fous —, `hors fiches`,
  `TOTAL`. Des fiches nommées : elles seules, `TOTAL (fiches nommées)` ; une sans plage :
  `GARDE:`, sort 1. Un champ qui manque aux transcripts : `AVERTISSEMENT:`. `--recoupe` :
  une ligne `RECOUPE` par `cost-state` des sessions, face à ses totaux. Sans découpe :
  `GARDE: pas de découpe — <raison>`, sort 1.
- `valider <fichier>… [--plan]` — les écarts d'un fichier de fiches, un par ligne
  `fichier:ligne: message`, puis `VALIDE|INVALIDE <n> fiches · socle <n> lignes
  · <n> écarts · <n> avertissements — <fichier>`. Avertit si une fiche ou le
  socle dépasse son seuil. Un écart : sort 1. `--plan` : ensuite, `<n>:<ligne>`
  pour chaque titre de fiche, `**Dépend de**`, `**Tentatives**`, `**Critère de fin**`.
- `lignes <chemin>…` — `<n> <fichier>`, `DOSSIER <d>` (` → <réel>` si lien) ou
  `ABSENT <chemin>` ; `~` et `*` développés ; puis `SEUILS page · fiche · socle`. Sort 0.
- `equiper <dossier> [--contexte C]` — ce que `/vlp:init` regarde : `DOSSIER=`,
  les 20 premiers sous-dossiers `nom/` (sans les cachés), `CLAUDE.md` s'il est
  là, les lignes `PROJET=`, `VOISIN=`, `AUCUN_PROJET` de la carte, et `ETAT=`
  pour `<dossier>/C` (défaut `context AI`). Sort 0.
- `lire <chemin>…` — imprime des fichiers du kit, chemins relatifs à sa racine
  (le parent de `scripts/`) : remplace un `cat` hors du projet, que PowerShell
  refuse. Hors du kit : `GARDE:` ; absent : `ABSENT <chemin>` ; l'un ou l'autre
  sort 1, les autres fichiers sont imprimés.
- `cocher <fichier> <fiche> [--resolu T] [--date D] [--verifier | --refuser M]` — `[ ]` → `[x]`
  sur le titre de la fiche et, si `CLAUDE_CODE_SESSION_ID` n'est pas vide, `**Session** : <id>`
  avant sa ligne `**Dépend de**` (déjà là : pas redoublée) ; `--resolu` réduit
  un bloc `**Tentatives**` à `**Tentatives** (<date>) — résolu par : T`.
  `COCHÉ <fiche> · Session <id|absente>`. Introuvable ou déjà cochée : `GARDE:`,
  rien écrit, sort 1. `--verifier` n'écrit rien, et rend `CASE <fiche> [x]` (sort 0) ou
  `CASE <fiche> [ ]` (sort 1) ; puis, si le sujet du dernier commit du dépôt du fichier commence
  par `<fiche>:` ou `<fiche> :` (le sous-agent a commité), `TÊTE <sha> <sujet>` et sort 1 ; hors d'un
  dépôt, `SANS GIT`, et la case seule décide. `--refuser M` (chantier REV) : `[x]` → `[ ]`, et
  sous le titre le bloc `**Tentatives** (<date>) — non résolu.`, `1. FAITE refusée à la
  relecture.`, `Erreur : M` ; déjà là, il gagne la ligne numérotée suivante et son `Erreur :`
  prend M, sans se doubler. `REFUSÉ <fiche> · refus <n>` : `<n>` compte, dans le bloc après
  l'ajout, les seules lignes numérotées `FAITE refusée à la relecture.`. `--session <uuid> --role <rôle>`
  (chantier NUI ; exclusif de `--verifier` et `--refuser`) : la session d'un rôle de la nuit, que la
  boucle connaît et non la session elle-même — `**Session** : <uuid> (<rôle>)`, fiche cochée ou non,
  jamais doublée (`NOTÉ` ou `DÉJÀ`) ; `--role clore` l'écrit dans l'en-tête, avant le premier `## `, comme
  `ouvrir`. `sessions`, `cout` et `page` ne lisent que l'id, sans le ` (<rôle>)`.
- `relecture <fiche> [--sha S]` — ce que lit le relecteur de `/vlp:enchainer` (chantier REV). Sans
  `--sha`, un instantané de l'arbre — suivis et non suivis, selon `.gitignore` — en commit de parent
  `HEAD`, par un index temporaire : ni `HEAD` ni l'index ne bougent ; avec, ce commit. Deux worktrees
  détachés `vlp-relecture-*` dans le dossier temporaire, ceux d'un appel précédent retirés d'abord :
  APRÈS sur le commit, AVANT sur son parent. Imprime `APRÈS=`, `AVANT=`, puis, lus dans le fichier de
  fiches courant du `CHANTIER.md` d'APRÈS — sans son chemin (FFE) —, le socle et la fiche comme `socle` et `extraire`,
  `git diff --name-status`, une ligne `HORS FICHE <chemin>` par fichier changé que la ligne
  **Fichiers** ne nomme pas — hors le fichier de fiches, le **fichier d'état** du `CHANTIER.md`
  d'APRÈS et `artefacts/` —, puis le diff. `--retirer` :
  retire ces worktrees, `RETIRÉ <n>`. `VLP_CANAL` posé (chantier NUI) : ils s'appellent
  `vlp-relecture-<canal>-…`, et `--retirer` comme les retraits d'avant relecture ne retirent que ceux du canal. Pas de dépôt, commit inconnu ou sans parent, fiche absente :
  `GARDE:`, aucun worktree ne reste, sort 1.
- `page <fichier> [<page.html>]` — régénère la page du chantier depuis le fichier
  de fiches : états, avancement, comptage, coûts (`**Session**`), date. Les coûts
  se coupent aux commits `<ID> :` (`git log`), sous-agents compris, plus une ligne
  « hors fiches » ; la session du cadrage, notée en tête par `ouvrir`, se coupe comme
  celles des fiches — ses tours d'avant l'ouverture vont hors fiches. Sans Git, sans
  commit qui nomme le préfixe, ou clos sans commit de fiche, ils se tirent de
  l'ancienne page. Sans page :
  `<dossier du fichier>/artefacts/<même nom>.html`. Garde de la page l'en-tête — sauf
  sa plage de fiches, refaite depuis le fichier —, les notes, le journal, le blocage
  et le bilan.
  `--note <fiche> <texte>`, `--journal <texte>` (répétables) ; `--creer
  --projet P --titre T --resultat R` part du gabarit ; `--verifier` n'écrit
  rien et sort 1 si états ou avancement diffèrent du fichier. `--forme` : la forme seule
  (style lié, fiches et journal repliés, bilan en haut), rien ne se recompte — coûts des
  fiches, total et hors fiches recopiés de l'ancienne page ; refuse `--creer`.
  Recopie les joints à côté de la page (`joints`), puis écrit `CSS <copie de vlp.css>` et
  `FILES {…}` ; une page d'avant BTN1 reçoit une fois `<meta charset>` et `<script src="vlp.js">`.
  `FILES` ne nomme que les joints changés depuis la dernière publication de la page (`publie`,
  noté par `attente hook`) ; page jamais notée : tous ; rien de changé : `FILES {}` (chantier JNT).
- `hook` — le hook `PostToolUse` (`Write|Edit`) du plugin : lit sur stdin le
  JSON du hook, prend `tool_input.file_path` (relatif : contre `cwd`). Sort 0
  muet si ce n'est pas un fichier de fiches — JSON illisible, chemin absent, pas
  `.md`, ou ni marqueur `<!-- FICHE:X1 -->` ni `## Le socle commun` hors bloc de
  code. Sinon `valider` : écart → écarts, bilan et consigne sur stderr, sort 2 ;
  valide → le JSON `hookSpecificOutput` dont `additionalContext` est le bilan,
  sort 0.
- `filet` — le hook `PostToolUse` du sous-agent : lit sur stdin le JSON du hook.
  Sort 0 muet si pas un sous-agent (`agent_id` absent, ou `agent_type` ne
  contient pas « fiche »), ou si le transcript du sous-agent est absent. Sinon
  compte les tours rendus et lit `maxTurns` d'`agents/fiche.md` ; si
  `tours_restants <= 3`, rend un JSON `hookSpecificOutput` avec l'avertissement,
  sort 0 ; sinon sort 0 muet.
- `etat <contexte>` — `ETAT=<NN>-etat.md` : le fichier d'état déjà présent,
  sinon le premier nombre à deux chiffres libre après le plus grand (`01` si le
  dossier est vide ou absent). Sort 0.
- `renvois <projet>` — les fichiers que l'index (1re cellule de ses tables) et
  le routage de `CLAUDE.md` (dernière cellule) nomment entre accents graves et
  qui n'existent ni contre le dossier de contexte ni contre la racine : une
  ligne `ABSENT: <source>:<ligne>: <nom>` chacun, puis `RENVOIS <n> nommés ·
  <n> absents`. Ignorés : un nom à `<…>` ou `*`, sans `.`, une ligne dont la 1re
  cellule commence par `*(`. Un absent : sort 1. Avant `RENVOIS`, une ligne
  `AVERTISSEMENT: <fichier> <n> lignes > <seuil>` par fichier de tête au-delà
  de son seuil, puis `POIDS CLAUDE.md <n>/<seuil> · CHANTIER.md <n>/<seuil> ·
  index <n>/<seuil>` (`absent` pour <n>) ; un poids ne change pas la sortie.
- `comparer <ancienne.html> <neuve.html>` — le texte visible de chaque page
  (balises, `<script>` et `<style>` retirés, entités décodées, blancs réduits),
  par ligne de tableau ou par bloc : une ligne `PERDU: <texte>` par texte de
  l'ancienne absent de la neuve, `AJOUTÉ: <texte>` pour l'inverse, puis
  `COMPARER <n> perdus · <n> ajoutés`. Un texte qui ne diffère que par sa plage
  `fiches X1–X7` sort en `PLAGE: <ancien> → <neuf>`, ni perdu ni ajouté, et la
  dernière ligne finit par ` · <n> plages refaites`. Sort 0 même avec des pertes — une
  mesure, pas une garde. Un fichier absent : `GARDE:`, sort 1.
- `niveau <projet>` — en quoi un projet équipé a dérivé du kit ; n'écrit rien.
  Agrège `renvois` (renvois absents en écarts, poids en avertissements, la ligne
  `POIDS` telle quelle), `feuille --verifier` et, si un fichier de fiches est
  courant, `page --verifier` ; ajoute ce que rien ne voyait : un `${…}` cité sur
  une ligne de champ ou de table de `CHANTIER.md`, de l'index ou du fichier
  d'état, et la table des chantiers clos restée dans `CHANTIER.md`. Compte le
  Markdown resté brut de la feuille régénérée, toujours sur une ligne `MARKDOWN
  <n> ** · <n> liens Markdown · <n> liens cassés — <page>` : un écart s'il n'est
  pas nul. Une copie locale de `methode-chantier.md` n'est pas un écart : la
  méthode la tolère pour un projet équipé avant la règle. Une ligne `ÉCART:
  <catégorie>: <phrase>`
  par écart (`renvois`, `feuille`, `page`, `variable`, `clos`, `marque`), puis `NIVEAU <n>
  écarts · <n> avertissements — <projet>`. Un écart : sort 1.
  `--ecrire` corrige les seuls écarts mécaniques — la table des chantiers clos
  retirée de `CHANTIER.md` (jamais si l'index ne nomme pas chacun de ses
  fichiers), la feuille de route posée depuis le gabarit puis régénérée, le
  bloc repliable des clos posé sur une feuille d'avant le 2026-09-17, et les
  lignes closes écrites avant `gras_et_liens` converties en place, et, dans un projet
  sans aucune marque d'ouverture, `**Ouvert.** le <date>` sous le titre du fichier que
  nomme l'ancienne ligne de `CHANTIER.md` — date du plus ancien commit « Chantier <code>
  ouvert », sinon celle de l'appel, et la ligne `CORRIGÉ: marque:` le dit (NUI30). Les
  renvois absents et les fichiers de tête hors seuil restent en `ÉCART:`. Tout
  se calcule avant la première écriture. Bilan `NIVEAU <n> corrigés · <n> à la
  main — <projet>` ; un écart restant : sort 1. `--date` fige la date.
- `feuille <projet> [--todo N] [--verifier]` — régénère dans
  `<contexte>/artefacts/feuille-de-route.html` la `ZONE:encours` (depuis le
  fichier de fiches courant et l'artefact du chantier), la `ZONE:todo` en
  cartes (depuis la TODO du fichier d'état ; une feuille en tableau se
  convertit ; `--todo N` y pose le badge « en cours », gardé
  d'un appel à l'autre tant qu'un chantier est ouvert), son décompte
  « <n> chantiers possibles » au-dessus des cartes (posé s'il manque, le chiffre
  en `<strong>`, la forme d'avant réécrite), le texte d'avant les cartes replié
  une fois dans `details.lecture` (`replier_lecture`), les
  lettres prises du pied (plus celle du chantier courant), et, une seule fois, le
  sommaire sous l'en-tête ; la date seulement si la page change.
  `FEUILLE todo <n> · encours <oui|non> · lettres <n> · <réécrite|inchangée>
  — <page>`. `--verifier` n'écrit rien, dit `identique|écart`, sort 1 sur écart.
  Avant `FEUILLE`, les joints recopiés et les lignes `CSS` et `FILES`, comme `page`. Avec au
  moins un coût clos, `couts.svg` (`svg_couts`) écrit à côté et nommé dans `FILES`, sa balise
  `<img>` posée une fois avant `details.clos` (`balise_couts`), ses barres dans `data-couts`
  pour `vlp.js` ; sans coût, ni l'un ni l'autre.
- `trier <projet>` — le tri du soir par script (chantier NUI) : lecture seule, aucun appel modèle, sur la TODO
  du fichier d'état. Par rang : `PRÊT <code>` ou `ÉCARTÉE <code> — <raison>` (la marque `MARQUE_VISUELLE` ou `push`
  en cellule 3-4, ou une dépendance non close ; une prête du même soir compte pour close), `FICHIERS <code> <chemins>`,
  `MARQUES <code> <total> : …` (`MARQUES_TRI`), `SOIR <code> — <raison>` pour une prête à découper le soir
  (au-delà de `GROS_FICHES`, sans nombre, « à cadrer »). Puis `CANAL <k> : <codes> — <raisons>` par groupe de prêtes
  liées (dépendance, sinon fichier commun comparé sur son nom), `inconnu → à la page` sans lien, et `TRI <n> rangs ·
  <n> prêts · <n> écartées`. TODO illisible : `GARDE:`, sort 1. Puis le fichier des nuits (`fichier_nuits`,
  `<contexte>/NN-nuits.md`) : sa section `## Leçons` (`indice` aux vivantes sous `LECON_INDICE` ; `GARDE:`, tri
  imprimé, sort 1, si le fichier ne se lit pas ou au-delà de `LECONS_MAX` vivantes), puis `TAUX jour` (le prix
  par fiche des clos, comme l'estimé d'`ouvrir`) et `TAUX nuit` (médiane des fiches acceptées des carnets,
  `indice` sous `CARNET_MIN`).
- `plan ecrire <projet> --json <fichier> [--date D]` — le plan du soir, dans le fichier des nuits
  (`fichier_nuits(creer=True)` : le premier soir il n'existe pas). Le JSON : `borne_usd`, `borne_chantiers`, puis
  par canal `A`, `B` la liste ordonnée de `{code, prefixe, reponses}`. Écrit `## Nuit <date>` avant `## Leçons` :
  la borne, une ligne par chantier, un `### <code>` par chantier, ses réponses en puces ; même date : remplacée,
  le reste repris tel quel. Refus, sans rien écrire, `GARDE:`, sort 1 : code absent de la TODO (`codes_todo`),
  préfixe qui n'est pas de une à trois majuscules, déjà pris (`lettres_prises`) ou donné deux fois, chantier dans
  deux canaux, canal autre que A ou B, borne absente ou nulle, réponse à saut de ligne, `VLP_NUIT=1`.
  `plan lire <projet> --date D [--canal A|B] [--chantier C]` — `BORNE <usd> $ · <n> chantiers`, puis
  `CHANTIER <code> · canal <c> · rang <n> · préfixe <P>` par chantier dans l'ordre ; `--chantier` : son seul
  `### <code>` (`imprimer_section`). Sans fichier des nuits ni plan à la date : `GARDE:`, sort 1 ; permis sous
  `VLP_NUIT=1`.
- `matin <projet> [<date>]` — la fusion du matin (NUI15) : les branches `refs/heads/nuit/<date>-*` dans `main`, une à
  une. Sans date, après les gardes, `nuit_a_ranger` prend la nuit qui a des branches à fusionner (ni `DÉJÀ` ni
  `DE CÔTÉ`) si elle est seule — `NUIT <date> — la seule à ranger : <n> branche(s)`, la date à reprendre pour
  `--rapport` — sinon `GARDE: plusieurs nuits à ranger : <date> (<n>), …` ou `GARDE: aucune nuit à ranger (<n>
  branche(s) nuit/* …)`, rien fusionné. `GARDE:` (sort 1, rien fusionné) : projet non équipé, date illisible, projet qui n'est pas la racine de son
  dépôt, `HEAD` hors `main`, arbre pas propre, `CHANTIER.md` de `main` sans ses deux libellés ou sa ligne de
  lettres, aucune branche. Ordre : le carnet de la nuit (rang de la 1re ligne de chaque `canal` + `chantier`),
  sinon l'heure de la pointe puis le nom (`ORDRE pointes — carnet absent`). Par branche : `DÉJÀ <b>` (ancêtre de
  `main`) ; `DE CÔTÉ <b> — <courant>` (son `CHANTIER.md` garde un chantier ouvert : jamais fusionnée) ; sinon
  `git merge --no-ff --no-commit`, puis `CHANTIER.md` refait par `git merge-file` sur ses trois versions dont les
  deux libellés et la liste des lettres sont remplacés par un jeton (`neutre`), puis rendus (`restaurer`) : ceux de
  `main` — tous deux à `aucun` si son chantier porte `**CLOS**` dans l'arbre fusionné (NUI26) —, et ses lettres
  suivies de celles de la branche qui lui manquent — Git perd sans conflit ce que `clore` remet à `aucun`. Un conflit sur la feuille (avec une archive des clos), `couts.svg` ou un joint : celui de `main`,
  ils se refont. `feuille` est refaite au rang « en cours » que `main` portait avant la fusion, avec joints, `couts.svg`
  et bloc d'archive (`rafraichir_couts`) ; `git add -A` ; commit `Matin <date> : <b>` ; `FUSIONNÉE <b>`. Autre
  conflit (code, `08-etat.md`, archive…), ou feuille en conflit sans archive : `ARRÊT <b> — conflit : <fichiers> —
  après résolution : <python> <vlp.py> feuille <projet> --todo <rang>` ; commit refusé : `ARRÊT <b> — commit
  refusé : <1re ligne>` ; sort 1, la fusion reste en cours, les suivantes ne sont pas touchées. En fin :
  `MATIN <n> fusionnée(s) · <m> de côté`. Avant la feuille, les fichiers que les deux côtés ont changés sont refaits
  par clé depuis la base, `main` et la branche (NUI16, `fusionner_fichiers`) : le fichier d'état (TODO par n°,
  journal en union, le reste par `git merge-file`), `CLAUDE.md` (lignes « Clos le » coupées à `CLOS_GARDES`), l'index
  et son archive (la ligne pour clé), `archive-clos.html` (la ligne close, `resommer`), `en-attente` (la page ; la plus
  récente gagne ; vide : retiré) et `publie` (la clé ; empreintes différentes : clé retirée, ligne `PUBLIE …`). Un
  désaccord ou un reste en conflit : `GARDE: <chemin> : <raison>`, puis l'`ARRÊT` ci-dessus. Pas de `merge=union` :
  il garde les deux lignes de `publie` quand les empreintes diffèrent. Ni push, ni carnet.
- `fusionner <projet> <branche>` — la fusion du jour (NUI26) : `branche` dans celle du dossier, par le chemin de
  `matin` (`fusionner_branche`), commit `Fusion : <branche>`, `FUSIONNÉE <branche>`. Déjà contenue : `DÉJÀ <branche>`,
  sort 0. `GARDE:` (sort 1, rien fusionné) : non équipé, hors racine, `HEAD` détachée, `MERGE_HEAD` présent, arbre
  sale, branche absente, branche qui garde un chantier ouvert (`de_cote` : le clore dans son worktree d'abord).
  Un code des lettres pris des deux côtés sous deux titres : `GARDE: le code <X> est pris deux fois : « <a> » et
  « <b> »`, avant le merge, rien d'écrit — `matin` aussi ; même entrée des deux côtés, comptée une fois (NUI27).
  `clore` dans un worktree hors de la principale imprime la ligne `FUSIONNER` à lancer depuis elle (sauf `VLP_NUIT=1`).
- `matin <projet> <date> --rapport <json>` — le rapport du matin (NUI19), sans fusion ni commit, rejouable. La date
  est obligatoire : sans elle, `GARDE:`. Trois premières gardes de `matin` (équipé, date, racine du dépôt) ; carnet
  de la nuit absent ou vide : `GARDE:`, sort 1.
  Complète le carnet : chaque ligne de session sans `usd_kit` reçoit `usd_kit` et `tours_kit` (`mesure_session_kit` : son
  transcript et ses sous-agents sommés, prix arrondi une fois au centime), mesurés hors verrou, écrits d'un coup sous celui
  du carnet ; session introuvable, illisible ou hors `GRILLE` : `KIT ? <session> — <raison>`, aucune clé `_kit`, jamais 0.
  Range au fichier des nuits (`fichier_nuits`, créé au besoin) une ligne de table par (nuit, canal, chantier) absente —
  `<jouées>/<acceptées>/<refusées>` et la somme des `usd_kit`, `≥` si des sessions n'en ont pas, `?` si aucune —, puis
  `NUITS <fichier> · <n> ligne(s) ajoutée(s)`. Croise les chantiers mis de côté selon Git (`de_cote`) et selon le carnet
  (`mis-de-cote:`) : un désaccord est une ligne `ÉCART <canal>-<code> — …`. Écrit le JSON de `chef page --questions` : `fait`
  (une ligne par chantier : issues, relances, modèles vus, `plugin_retard`, coût `_kit`, jamais `_cli`), `choix` (une carte
  par mis de côté aux trois réponses du socle, une par note selon sa `sorte` : `reste` trois réponses, `case3` et `case4`
  deux), `mal` (`NOTE SANS SORTE`, aussi imprimée). Fin : `RAPPORT <json> · <n> chantier(s) · <m> mis de côté · <k> carte(s)`.
- `joints <dossier>` — recopie `templates/vlp.css` et `templates/vlp.js` dans le dossier, et
  n'écrit que `FILES {"vlp.css": <chemin>, "vlp.js": <chemin>}` : le JSON du paramètre `files`
  d'`Artifact`, chemins en barres obliques (pour `/vlp:init`). Dossier absent : `GARDE:`, sort 1.
- `clore <projet> --livre T [--tokens N] [--abandon T] [--fait T] [--surpris T]
  [--date D]` — les écritures mécaniques de `cloture.md` : `**CLOS**` (et les
  abandonnées) dans le fichier de fiches courant, et `**Fait.** L1..Ln (date) :
  <fait, sinon livre>` à la place de `**Fait.**` ou `**Où on en est.**` ; la
  ligne ouverte de l'index passée à « clos » ; la ligne « jouer une fiche » du
  routage de `CLAUDE.md` retirée, et `| relire un chantier clos | <index> |`
  posée à sa place si elle manque ;
  dans la page du chantier, `ZONE:bilan` visible (Livré, Surpris) et coûts régénérés,
  `ZONE:blocage` cachée — absentes : `GARDE:`, le reste est écrit ; avec
  `--resume T`, dans « Où on en est » de `CLAUDE.md`, `- Clos le <date> : T
  (chantier L).` (déjà là : rien ; T déjà préfixé ou suffixé : pas doublé), et seules les `CLOS_GARDES` dernières lignes de
  cette forme restent ; dans `CHANTIER.md`, courant et artefact à `aucun`,
  la lettre aux lettres prises (plus de table des clos) ; dans la feuille
  de route, une ligne en tête de `ZONE:clos`, le total cumulé resommé des
  comptes bruts, puis `feuille`, et sa ligne `FILES` (joints et `couts.svg`, comme `feuille`).
  Tout est calculé avant la première écriture.
  La ligne du chantier sur la feuille prend le total mesuré (étape « 1 ter ») ;
  sans page ou sans mesure, elle retombe sur `--tokens`, puis sur « non mesuré ».
  Si `--tokens N` est donné et diffère du mesuré, écrit `ÉCART tokens <N> donné
  · <mesuré> mesuré — le mesuré fait foi` ; un total mesuré à 0 (découpe vide) ne
  l'emporte pas.
  L'estimé face au réel (chantier EST) : `estimé <N> fiches ≈<X> $ · cadré <C> · joué <J>
  fiches <Y> $` — N et X relus de la ligne `**Estimé.**`, C les titres de fiche, J les `[x]`,
  Y le prix mesuré, le pondéré de la page (`? $` sans lui, chantier TAU) ; sans `**Estimé.**` :
  `estimé non noté · …`, pas de `GARDE:`. Ce prix ouvre aussi la cellule Tokens de sa ligne
  sur la feuille (`47,08 $ · ≈95,0M (…)`), rien s'il est inconnu. Écrit en fin de `**Fait.**` (` — <estimé>.`), en `<p>Estimé : …</p>` après Surpris
  dans `ZONE:bilan`, et dans `CLOS` avant ` — <projet>`.
  Après l'index, `archiver` (ci-dessous) ; la ligne « relire un chantier clos »
  que `clore` pose dans `CLAUDE.md` pointe l'archive.
  `CLOS <lettre> <plage> · chantier <n> · cumul <brut> · routage <0|1> · index
  <0|1> · archivé <n> · bilan <0|1> · <estimé> — <projet>`. Aucun chantier ouvert, ou
  déjà `**CLOS**` : `GARDE:`, sort 1.
- `archiver <projet>` — chaque ligne de table `**clos**` de l'index quitte l'index pour
  `00-INDEX-archive.md`, dans son dossier (créée au besoin : titre, « QUAND LIRE », en-tête
  `| Fichier | Lire quand |`), déplacée telle quelle et triée par numéro de fichier ; l'index
  gagne une ligne qui renvoie à l'archive, si elle manque. Relancé : rien ne change.
  `ARCHIVÉ <n> · index <n> lignes · archive <n> lignes` ; pas de champ **index** : `GARDE:`,
  sort 1 (chantier IDX).
- `archive <projet> [--url URL]` — les lignes closes de la feuille de route, et leur pied, vont
  dans `archive-clos.html` (gabarit `templates/artefact-archive-clos.html`), à côté ; la feuille
  garde un bloc `ZONE:archive` — résumé et lien — et le graphique. `--url` écrit le champ
  **artefact archive** de `CHANTIER.md`. Relancé : rien ne change. `ARCHIVE <n> déplacées · <n>
  dans l'archive · feuille <avant> → <après> octets · url …` ; archive déjà là alors que la
  feuille a encore ses clos : `GARDE:`, sort 1 (chantier ARC).
- `abri <page.html>…` — crée à côté de chaque page son `.md` (résultat, notes, journal, bilan),
  tiré de la page, texte désechappé et balises retirées, sans toucher la page ; un `.md` déjà là
  n'est pas réécrit. `ABRI <md> · résultat <0|1> · notes <n> · journal <n> · bilan <0|1>`,
  ou `DÉJÀ <md>` ; page absente : `GARDE:`, sort 1 (chantier ABR).
- `ouvrir <projet> --fiches F --titre T [--artefact URL] [--estime-fiches N]` — les écritures
  mécaniques de l'ouverture : dans `CHANTIER.md`, courant = `F (L1..Ln)` et
  artefact = l'URL (sinon `aucun`, ou l'ancienne si F est déjà courant) ; une
  ligne « on joue une fiche » après la ligne de l'index au plus grand numéro ;
  une ligne « jouer une fiche du chantier » avant « relire un chantier clos »
  (sinon le premier « relire le chantier ») du routage de `CLAUDE.md`. Une ligne
  déjà là n'est pas redoublée ; relancé sur F, seule la plage de sa ligne
  d'index `**ouvert**` suit le fichier. `CLAUDE_CODE_SESSION_ID` non vide et sur
  aucune ligne `**Session**` du fichier : `**Session** : <id>` avant sa première
  ligne `## ` — la session du cadrage, que `cout` et `page` mesurent. `OUVERT
  <lettre> <plage> · index <+n|~1> · routage +<n> · session +<0|1> · artefact <url>
  — <projet>` (`~1` : plage refaite) ; index ou routage introuvable : `GARDE:`, le
  reste est écrit. `--estime-fiches N` (`0,5` ou `0.5`) : `**Estimé.** <N> fiches · ≈<X> $
  — ≈<Y> $/fiche sur <K> clos (le <date>).` juste avant `**Fait.**` de F — Y, la moyenne des
  prix mesurés des lignes de `ZONE:clos` qui en portent un, fiches comptées sur leur plage ;
  X = N × Y (chantier TAU) ;
  `OUVERT` gagne ` · estimé <N> fiches ≈<X> $`, ou ` · estimé gardé` si la ligne y est
  déjà (non réécrite). Pas de feuille, aucun clos mesuré, aucun clos au prix mesuré, pas de
  `**Fait.**` : `GARDE:`, le reste est écrit (chantier EST).
  Un autre chantier déjà ouvert, ou F porte `**CLOS**` : `GARDE:`, sort 1. Le code de F ouvert dans un autre
  worktree, sous un autre fichier : `GARDE: le code <X> est déjà ouvert ailleurs`, sort 1, rien d'écrit (NUI27).
- `contrat [<transcription>…] [--depuis D] [--ouverture F]` — le contrat d'`agents/fiche.md` lu dans des
  transcriptions de sous-agent (chantiers CON, ENQ). Sans argument : toutes celles dont le
  `.meta.json` voisin dit `vlp:fiche`, sous `~/.claude/projects/*/*/subagents/`. Une ligne
  chacune : `<id> <agentType> <départ de la session parente, UTC | ?> <premier mot du dernier
  message texte | (vide) | (interrompu)> git <n> bloqué <n>` — n : appels `Bash`/`PowerShell` qui
  lancent un verbe Git hors lecture (`LECTURE_GIT`, chantier VRB), hors corps d'un heredoc écrit par
  `cat` ou `tee` (chantier ECH) ; parmi eux, ceux dont le `tool_result` porte le refus du gardien
  (`REFUS_GIT`, ou `REFUS_GIT_AVANT`) comptent en bloqué, pas en écrit ; `(interrompu)` : un message utilisateur
  `[Request interrupted by user…` suit le dernier texte de l'assistant — il ne compte pas en
  sans-statut ; illisible : `ILLISIBLE <chemin>`. `--depuis` (heure
  ISO ou commit, comme `mesure-tokens.py --plage`) : celles dont la session parente a démarré
  à D ou après. `--ouverture` : ceux partis — leur heure à eux — depuis le plus ancien commit
  qui ajoute le fichier de fiches F, sous une ligne `DEPUIS <heure UTC> · ouverture de F` ; F
  dans aucun commit : `GARDE:`, sort 1 (chantier CHK). Puis `CONTRAT <n> sous-agents · <n>
  écrivent dans Git · <n> bloqués par le gardien · <n> sans statut en tête` (ni `FAITE`, ni
  `RETOUR`, ni `BLOQUÉE`, ni interrompu) ` · <n> interrompus`. Borne illisible : `GARDE:`, sort 1.
- `forme [<transcription>…] [--depuis D] [--regle R]` — la forme et le poids dans des
  transcriptions de sous-agent. Sans argument : toutes celles dont le `.meta.json` voisin dit
  `vlp:fiche` ou `vlp:relecture`, sous `~/.claude/projects/*/*/subagents/`. Une ligne
  chacune : `<id> <agentType> <départ de la transcription, UTC | ?> user <c> projet <c>
  memoire <c> resume <0|1> jauge <0|1> tete <0|1>` — `<c>` : caractères du `content` des
  fichiers d'instructions de ce type (User, Project, AutoMem, somme si plusieurs, 0 si aucun) ;
  `resume` 1 si une ligne du dernier message texte s'ouvre par « En résumé » ; `jauge` 1 si
  l'une s'ouvre par un des cinq libellés de `JAUGE` — marques de tête retirées (`REGLE`, celle
  du gardien), un émoji de jauge en tête ou le mot suivi de `—`, `…` ou de la fin de ligne
  (chantier OUV) ; `tete` 1 s'il commence par un mot de `STATUTS` ou de `VERDICTS` (le relecteur).
  `--regle` : la partie du message que jugent `resume` et `jauge` — `tout` (le texte entier,
  la mesure d'avant `JUG2`), `tiret`, `deux`, `tete` (chantier JUG). Illisible :
  `ILLISIBLE <chemin>`. `--depuis` (heure ISO ou commit) : celles dont la transcription a
  démarré à D ou après. Puis `FORME <n> sous-agents · user <moyenne> car. · resume <k> ·
  jauge <k> · tete <k>`. Borne illisible : `GARDE:`, sort 1.
- `gardien` — le hook du contrat (chantier CON et RLG), muet hors d'un sous-agent dont
  l'`agent_type` contient « fiche » ou « relecture » et sur une entrée illisible ; sort toujours 0.
  `PreToolUse` : un appel `Bash`/`PowerShell` qui écrit dans Git (le motif de `contrat`) est
  refusé, `permissionDecision` `deny` et sa raison — elle nomme l'agent (`vlp:fiche` ou `vlp:relecture`) et son fichier.
  `SubagentStop` : `vlp:fiche` — renvoyé au travail (`decision` `block`, une raison d'une ligne) si
  `last_assistant_message` ne commence pas par un statut — sauf `stop_hook_active`, déjà renvoyé —, ou s'il dit `FAITE` et
  que `cocher --verifier` sur la fiche de `Fiche à jouer :` (1er message de la transcription)
  rend une case vide ou une `TÊTE`, même sous `stop_hook_active` (chantier GAR), ou si une ligne du
  dernier message s'ouvre par « En résumé » ou une jauge (`forme_texte`, règle `REGLE` : une citation
  ne compte pas) et que `stop_hook_active` est faux (chantier FOR—JUG) ; `vlp:relecture` — renvoyé si
  la même règle le dit et que `stop_hook_active` est faux, sinon muet (chantier RLG—FOR—JUG).
- `ouverts <projet> [--rev R]` — les chantiers ouverts du dossier de contexte : `OUVERT <fichier>` chacun, ou
  `OUVERTS=0` ; ouvert = titre `# Chantier ` + marque `**Ouvert.**`, sans `**CLOS**` ni `**Pause.**` (chantier NUI21).
- `pause <fichier> "<raison>" [--date D]` — `**Pause.** le <date> — <raison>` sous le titre `# Chantier `, puis
  `PAUSE <fichier> le <date>` ; `ouvrir` sur ce fichier la lève (`· pause levée`). Introuvable, clos, déjà en pause,
  sans titre : `GARDE:`, sort 1, rien d'écrit (NUI30).
- `vigile [fichier]` — une page cassée ne part pas (chantier VID, `defauts_page`) : sans argument,
  le hook `PreToolUse` sur `Artifact`, `deny` pour un `.html` à défauts, muet sinon ; avec un chemin,
  une ligne `GARDE:` par défaut (sort 1) ou `PAGE SAINE <n> blocs`.
- `chef page --questions <json|@chemin> --sortie <page.html>` — la page à cartes (`templates/rapport-choix.html`)
  remplie par script, zéro appel modèle (chantier NUI) : le modèle choisit le contenu, le script écrit la page, celle du
  soir comme le rapport du matin. Le JSON : `projet`, `sujet`, `titre` ; `date` (`AAAA-MM-JJ`, défaut : le jour) ;
  `plage` et `pied` (textes) ; `jauge` (un mot de `JAUGE`, son émoji et sa classe `moyen` ou `ko` suivent) ; `puces`
  (l'en-tête, des textes) ; puis une clé par section du gabarit, dans son ordre, absente = section absente : `chiffres`
  `{cases: [{valeur, legende}], sources: [texte]}`, `fait` `[{ref, code, titre, livre, cout}]`, `decisions` `{intro,
  cartes: [{titre, portee, niveau faible|moyen, probleme, choix, ecarte, prix, defaire}]}`, `choix` `[{titre,
  puces: [texte], options: [{valeur, libelle, effet, recommande: true|false}]}]`, `mal` `[{genre erreur|alerte, titre,
  texte}]`, `fil` `[{heure, code, texte}]` ; `explique` (`true|false`, défaut `false`) : `data-explique` sur la page,
  l'Explique-moi sous chaque carte (quand le proposer : commentaire de tête du gabarit), et une ligne `CAPACITES sample`
  en sortie — la page se publie avec cette capacité. Les `name` (`D1`…, puis `Q1`…) et `data-cle` (`<projet>-<date>-<sujet>`) sont
  posés par le script. Les textes passent par `cellule_md` (échappés, gras et code rendus), `<title>`, `data-cle` et
  `value` par `esc` seul. La tête (`<link>`, `<style>`), « Tes réponses » et le `<script>` sont ceux du gabarit, cherchés
  hors commentaires (`COMMENTAIRE`) ; le commentaire de tête n'est pas recopié, le reste est bâti. `GARDE:` (sort 1, rien
  écrit) : JSON illisible, champ absent ou d'un autre genre, aucune carte, jauge hors `JAUGE`, question à moins de deux
  options, option sans effet, valeur doublée, deux recommandées, morceau du gabarit introuvable, ou `defauts_page` non vide
  sur la page bâtie (une ligne par défaut, au format de `vigile`). Sinon : `PAGE SAINE <n> blocs`, puis `CARTES D1 Q1…`,
  et `CAPACITES sample` avec `explique`.
- `attente ajouter <page> [--url U] [--projet D]`, `attente lister <dossier artefacts ou racine du projet>`,
  `attente retirer <page> [--projet D]` — la liste des pages que la limite du jour a refusées
  (chantier LOC) : `<contexte>/artefacts/en-attente`, une ligne par page, `page`, `url` (ou
  `aucune`) et `heure du refus` séparées par une tabulation, clé la page (la dernière entrée
  gagne), écrite dans un `.tmp` puis `os.replace`, le fichier disparaît quand elle se vide. La
  page est relative au dossier artefacts (un chemin absolu s'y ramène ; ailleurs : `GARDE:`).
  `ajouter` et `retirer` rendent `ATTENTE <n>` (les entrées restantes) ; `lister`, une ligne
  `ATTENTE=<page> <url>` par page puis `ATTENTE <n>`. `--projet` : le dossier du projet (défaut :
  le dossier courant). `attente hook` — le hook `PostToolUse` et `PostToolUseFailure` sur
  `Artifact` : un échec dont `error` dit `publish 429` ajoute la page (celle du `file_path`, si
  elle est sous les artefacts d'un projet équipé, `url` de l'appel ou `aucune`) et, la première
  fois du jour UTC pour ce projet (`tampon_neuf`), rend en `additionalContext` l'heure locale de
  la remise à zéro et celle d'une tâche planifiée `MARGE_TACHE` plus tard ; une publication
  réussie d'une page listée la retire ; tout le reste — page non lue, refus du vigile — se tait.
  Toute publication réussie note l'empreinte de ses `files` dans `publie`, à côté de la page.
- `repeindre <projet> [--a-blanc]` — chaque page de chantier clos (parcours de `recompter`)
  qui ne lie pas `vlp.css` passe par `page --forme` puis `vigile`, dans une copie :
  `REPEINTE <page> · lien <url>` ou `· sans lien` (section `## Lien` de son `.md`), une
  `GARDE:` si refusée — l'originale ne bouge pas. Puis `REPEINDRE <n> repeintes · <n> avec
  lien · <n> sans lien · <n> refusées · <n> déjà · <n> sans page`. `--a-blanc` n'écrit rien.
- `lien <page.html> <url>` — écrit l'URL en ligne dans la section `## Lien` du `.md` de la
  page (créé depuis la page s'il manque) : `LIEN écrit|déjà · <md> · <url>`.
- `liens <projet>` — pose le lien de chaque ligne de `ZONE:clos` dans le `.md` de sa page
  (parcours de `recompter`) ; deux liens pour une page : `DOUBLON`, rien d'écrit. Puis
  `LIENS <n> écrits · <n> déjà · <n> doublons · <n> sans lien · <n> sans page`.
- `recompter <projet>` — n'écrit rien (chantier REC). Pour chaque ligne de `ZONE:clos` de la
  feuille de route, le fichier de fiches que l'index nomme au même préfixe (`JUG1..JUG3` pour
  `JUG1–JUG3`), et une ligne `<préfixe> inscrit <n> · recompté <n|gardé> · écart <±n> ·
  <méthode>` : le recompté est le nombre de la ligne `TOTAL` de `cout` ; la méthode, `découpe`
  ou `gardé — <raison>` (sans session, transcription absente, `DÉCOUPE aucune`, découpe à zéro,
  fichier introuvable), écart 0 ; ` · partagée avec <préfixes>` si une de ses sessions est
  aussi dans le fichier d'un autre clos. Puis `RECOMPTE <n> clos · <n> recomptés · <n> gardés ·
  inscrit <n> · recompté <n> · écart <±n>`, recompté = inscrit + écarts. Pas de feuille, pas de
  `ZONE:clos`, pas d'index : `GARDE:`, sort 1. `--ecrire` : tout calculé d'abord, un recompté à
  écart non nul prend `recompté (REC), était <n> · <arrondi>`, un gardé `non recompté — <raison> ·
  <chiffre>` — la marque en tête, que `BRUT` ne lit qu'en fin —, puis pied et résumé resommés
  (`resommer`), `couts.svg` et sa balise refaits (comme `feuille`, sans ligne `FILES` : republier
  passe par `feuille`) ; relancé, rien ne change. Dernière ligne `ÉCRIT <n> cellules · total <avant> → <après>`.
  `--a-clore` : chaque ligne recomptée finit par ` · à clore <n> · après clore <n>` (le calcul de
  `cout --a-clore`, après clore = recompté − à clore), ou ` · sans appel clore`.
- `prix <projet> [--a-blanc]` — pose le `$` du `cout-total` de la page de chaque ligne de
  `ZONE:clos` (parcours de `recompter`) en tête de sa cellule Tokens s'il n'y est pas ; recale
  son ancien `joué … ≈X $` sur ce prix et marque son vieil estimé `(taux plat)`, dans le fichier
  de fiches, la page et son `.md` d'abri. Page sans `$` : rien, compté « sans prix ». `PRIX <n>
  posés · <n> déjà · <n> sans prix · <n> joués recalés · <n> estimés marqués`, puis une ligne
  `ÉCRIT <chemin>` par fichier écrit (aucune avec `--a-blanc`, qui n'écrit rien). Relancé, plus
  rien à écrire (chantier TAU).
- `bac <dossier>` — pose le bac d'essai de FIL3 dans un dossier absent ou vide (sinon `GARDE:`,
  rien d'écrit) : `CHANTIER.md`, `fiches.md` (`F1` douze `Read`, `F2` douze `exit 3`), `n01.txt`…
  `n12.txt`. Imprime `BAC <dossier>` et les deux commandes `claude -p`, sans les lancer (chantier BAC),
  puis `SESSION Set-Location "<dossier>"; & "<claude>"` : la ligne PowerShell qui ouvre une session
  dans le bac, avec le chemin de `claude` (`claude` seul, après la `GARDE:` de `claude`, s'il manque).
- `claude` — le `claude` que le kit lance : `VLP_CLAUDE`, sinon le PATH, sinon la plus haute version
  (comparée en nombres) sous `%LOCALAPPDATA%/Packages/Claude_*/LocalCache/Roaming/Claude/claude-code/`
  — l'app du Store, vue d'un terminal comme de l'app —, sinon sous `%APPDATA%/Claude/claude-code/`,
  vue de l'app seule : `claude.exe` à `<version>/` comme à `<version>/<empreinte>/` (VIT19).
  `CLAUDE <chemin>` (chantier CLI) ; sinon sort 1 : `GARDE: claude.exe absent de l'app…` si un dossier
  `claude-code` existe — le pre-commit refuse alors le commit —, `GARDE: claude.exe introuvable…` sinon.
- `transcription <jsonl>` — compte la transcription d'un sous-agent, une clé par ligne : `TOURS=`
  (`message.id` distincts porteurs d'`usage`, comme `comptoir_tours`), `APPELS=<n> — <outil> <n>, …`,
  `AVERTISSEMENTS=`, `AVERTIS_PAR_TOUR=<tour>:<n>,…` (tour de l'appel que désigne le `toolUseID`,
  `aucun` sans avertissement ; chantier TOU), `PREMIER_AVERTISSEMENT tour= outil= is_error=<oui|non> hook=` (l'appel que
  désigne son `toolUseID`) et `TEXTE=`, ou `PREMIER_AVERTISSEMENT aucun` ; `HOOK_ERREURS=<n> pour
  <n> appels`, `DERNIER mot= stop_reason=`, `DERNIERE_LIGNE=`. Illisible : `GARDE:`, sort 1 (chantier BAC).
- `kit-essai <dossier> --max-turns <n> [--kit <source>]` — copie le kit (par défaut celui de ce
  script ; sans `.git`, `.claude`, `context AI`, `evals/results`, `__pycache__`) dans un dossier absent
  ou vide, et y réécrit `maxTurns` d'`agents/fiche.md` : un plafond bas sans toucher au vrai kit.
  Dossier plein, ou pas de ligne `maxTurns` : `GARDE:`, rien d'écrit, sort 1. Imprime
  `KIT <dossier> · maxTurns <avant> → <n>` (chantier EVF).
- `servir <dossier> <port>` — un serveur local (`http.server`) sur `127.0.0.1` pour regarder
  les pages sans cache : `Cache-Control: no-store`, `.html .js .css .svg` en UTF-8, et
  `/_telephone?page=<page>` rend la page dans un cadre de 375 px de large (chantier LOC).
  Dossier absent ou port pris : `GARDE:`, sort 1. Imprime `SERVIR <url> · <dossier>`, puis sert
  jusqu'à l'arrêt.
- `apercu <projet> [--port N]` — écrit ou remplace, dans `<projet>/.claude/launch.json`, la seule
  entrée `apercu-<nom du dossier>`, qui lance `servir` sur `<contexte>/artefacts` ; le port est
  `--port`, sinon celui de l'entrée déjà là, sinon le premier libre depuis 8790. Les autres
  entrées restent à l'octet (l'entrée se greffe dans le texte, le fichier n'est pas réécrit).
  `APERCU écrit|remplacé|déjà <nom> · port <n> · <launch.json>`. `launch.json` illisible, sans
  `configurations` ou avec deux entrées du même nom : `GARDE:`, rien d'écrit, sort 1. Fichier
  pas couvert par `git check-ignore` (il porte des chemins de machine) : écrit quand même, et
  une `GARDE:` le dit, sort 0 ; pas de dépôt Git, pas de `GARDE:`.
- `mutant <fichier> <avant> <après> [--attendu "<début du libellé>" | --tous] [--test "<commande>"]` — le
  mutant d'une fiche de code (chantiers MUT, VIT2) : `@chemin` lit un argument dans un fichier, tel quel ;
  les `\n` d'`avant`/`après` suivent la fin de ligne du fichier. `avant` doit y être une fois exactement
  (sinon `GARDE:`, rien écrit). Le vrai fichier n'est jamais écrit : le kit — ou, hors du kit, le dossier du
  fichier — est copié dans un dossier temporaire (sans `MUTANT_EXCLUS`), la copie mutée, et les tests y
  tournent (défaut : le `test-vlp.py` de la copie, par ce Python ; dans `--test`, les chemins sous la racine
  copiée pointent dans la copie), avec `VLP_TOUS_ECARTS=1`, sortie lue ligne à ligne. `--attendu` : dès
  l'`ÉCART:` dont le libellé commence ainsi, l'arbre de processus est tué → `MUTANT ATTRAPÉ <n> écart(s) ·
  arrêté sur « … »` (sort 0) ; la suite finie sans lui → `MUTANT VIVANT pour <libellé>` (sort 1). `--attendu`
  sans `--test` (VIT21) : d'abord les seuls groupes qui portent le libellé (`test-vlp.py --seul`) — l'écart
  tombé là, `VISÉ --seul « … »` en tête ; sinon (aucun groupe, ou pas cet écart), la suite entière tranche,
  `SUITE ENTIÈRE · …` en tête. `--tous`, ou
  ni l'un ni l'autre : `MUTANT ATTRAPÉ <n> écart(s)` (sort 0) ou `MUTANT VIVANT` (sort 1). Une suite finie
  sort 0 ou dit `OK` ou `FIN:` en dernière ligne ; arrêtée avant — erreur, ou `DÉLAI:` de 1800 s —, c'est
  `MUTANT PLANTÉ …` (sort 1), même après un écart. Chaque `ÉCART:` vu est imprimé avant ; `COPIE restée : …`
  si la copie ne s'efface pas en 2 s ; puis `RENDU <sha1 12>` — `GARDE:` si l'empreinte a bougé, ou si les
  tests ne se lancent pas.
- `symboles <fichier> [<nom>…]` — une ligne `nom début-fin` par fonction ou classe de premier niveau d'un
  fichier Python, dans l'ordre du fichier, lue par `ast` sans l'importer (VIT9) : une fiche cite un nom,
  ceci rend sa ligne du jour. Avec des noms, leurs seules lignes, dans l'ordre demandé, et `ABSENT <nom>`
  pour un nom introuvable (sort 1). Fichier absent : `GARDE:`, sort 1.
- `rapide <motif> [--racine R]` — le contrôle rapide d'une fiche du kit, avant la suite entière (VIT23), joué en
  parallèle sous la racine (défaut : le dossier courant) : les groupes de `test-vlp.py` qui portent le motif
  (`--seul`), pyright sur les `.py` ajoutés, modifiés ou neufs depuis `HEAD`, et `sante --cliquet`. Une ligne
  `RAPIDE <contrôle> : vert|rouge|sauté · <s> s · …` par contrôle — rouge, ses lignes (30 au plus) ; sauté, sa
  raison (aucun groupe, aucun `.py` touché, pyright introuvable) —, puis `RAPIDE VERT` (sort 0) ou `RAPIDE ROUGE`
  (sort 1) et la durée. Il ne remplace pas la suite entière, que `cocher` exige toujours. Pas de
  `scripts/test-vlp.py` sous la racine : `GARDE:`, sort 1.
- `nuits noter "<texte>" [--canal C] [--stop]` — une ligne `note` au carnet de nuit (`carnet.py`, chantier
  NUI) ; avec `--stop`, la ligne `stop` (le texte en est la raison) que la boucle lit avant chaque
  session. Carnet : `VLP_CARNET`, sinon celui du jour du dépôt Git courant ; canal : `--canal`, sinon
  `VLP_CANAL`. Imprime `NOTÉ <chemin>` ; sans dépôt Git ni `VLP_CARNET` : `GARDE:`, sort 1. `--sorte reste|case3|case4`
  (NUI19) : ce que le matin fait de la note ; avec `--stop`, `GARDE:`.
- `nuits lecon "<ligne>" [--projet P]` — une leçon sous `## Leçons` du fichier des nuits (`fichier_nuits`, créé au
  besoin), dans la forme de `LECON_FORME` (NUI11). Hors forme, ou fichier illisible : `GARDE:`, sort 1, rien d'écrit.
  Imprime `LEÇON <fichier> · ajoutée` ou `· déjà là`.
- `sante [<fichiers>] [--base [--forcer "<raison>"] [--si-base] | --cliquet] [--racine R] [--sans-ruff]` — la
  santé du code, fonction par fonction (`sante.py`, qui en tient les règles ; chantier VIT) : les cinq comptes du
  socle de VIT et la docstring, par ruff s'il répond (`ruff`, sinon `-m ruff`), sinon par `ast`, « comptes estimés ». Sans fichier :
  les `.py` de `<racine>/scripts/`, racine par défaut le kit. Imprime une ligne par fonction (`!` sur un compte
  au-dessus de son seuil), `FICHIER` par fichier, `TOTAL`, puis, avec ruff, `AST=RUFF <n>/<m>` et chaque `AST≠RUFF`.
  `--base` écrit `scripts/sante-base.json` sous la racine — `BASE …`, ou `GARDE:` si elle se relâcherait, rien
  d'écrit, sauf `--forcer`, dont la raison y reste. `--si-base` : sans base sous la racine, `SANS BASE …`, sort 0,
  rien d'écrit (`/vlp:tache`, étape 6 bis, VIT16). `--cliquet` lui compare les fonctions : `EMPIRE`, `SEUIL` ou
  `DOCSTRING` par écart, le bilan `CLIQUET <n> fonctions · …`, puis `CLIQUET TENU` (sort 0) ou `CLIQUET ROMPU`
  (sort 1) ; sans base, `GARDE:`. ruff en échec : `RUFF ÉCHEC …`, et `ast` seul.

Les lignes des chantiers clos — lues ou écrites par `clore`, `recompter`, `prix`, `liens`,
`repeindre` et le prix moyen d'`ouvrir` — vivent dans `<contexte>/artefacts/archive-clos.html`
s'il existe, sinon dans la feuille ; le graphique reste sur la feuille (`page_clos`, chantier ARC).
`clore` y refait alors le bloc `ZONE:archive` de la feuille et met l'archive en liste d'attente
(`ATTENTE archive-clos.html — <URL>`), ou dit `GARDE:` sans champ **artefact archive**.

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
    import vlp_hook
    triee = vlp_hook.trier(sys.argv[1:])
    if triee == "":                     # un hook déjà pris par l'autre lanceur : sortir sans charger le cœur (VIT8)
        sys.exit(0)
    import vlp_coeur
    sys.exit(vlp_coeur.main(sys.argv[1:], entree=triee))
