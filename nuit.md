> **QUAND LIRE** : la carte du projet imprime `NUIT=1` — la session tourne la nuit,
> lancée par `boucle.py --nuit`, et personne ne répond avant le matin. Lu par
> `/vlp:tache`, par `/vlp:chantier` et par la session `clore`, qui l'appliquent
> sans le réécrire.
> Sans `NUIT=1`, ce fichier ne coûte rien.

# La conduite de nuit — ce que la nuit fait à la place de l'humain

Une commande du kit attend parfois l'utilisateur : une question, un geste, un oui.
La nuit personne ne répond, et le canal dormirait jusqu'à son délai. Sous `NUIT=1`,
**aucune attente ne reste une attente** : elle devient une ligne dite et la main
rendue, ou une note pour le matin. Jamais une question.

## Qui est qui

La session sait son rôle par ce qu'on lui a demandé :

- `/vlp:chantier <code>` : le découpage. Elle ne commite pas.
- `/vlp:tache <fiche>` : le jeu d'une fiche, ou sa relance. Elle ne commite pas non plus.
- `/vlp:tache` sans fiche, la carte à `PROCHAINE=aucune` : la session `clore`.
- Le reste — relire, commiter, mettre de côté — est la boucle (`scripts/boucle.py`).

## Ce qui vaut partout

- **Un arrêt** : une ligne qui dit ce qui arrête (la sortie brute d'une `GARDE:`),
  et la main rendue. Ni `git checkout`, ni écriture à la main pour contourner. La
  boucle voit l'arrêt et met le chantier de côté : branche laissée ouverte, travail
  commité `WIP …`, jamais fusionné. Le matin la liste et l'humain choisit.
- **`PROJET=` est le worktree du canal** : il n'y a aucun projet à choisir. Les
  commentaires d'artefact ne sont pas lus.
- **`ATTENTE=` et `PLUGIN_RETARD=`** : notés au compte rendu, jamais agis — ni
  republication, ni merge, ni tâche planifiée, ni `/reload-plugins`.
- **Une note pour le matin** : `vlp.py nuits noter "<texte>"` — une ligne au carnet
  de la nuit (`VLP_CARNET`), pour le canal de la session (`VLP_CANAL`).
- **Le plan du soir** : `vlp.py plan lire <projet> --date <la nuit>` — la nuit est le
  nom du fichier `VLP_CARNET`. La ligne `CHANTIER <code> … préfixe <P>` donne le
  préfixe ; avec `--chantier <code>`, les réponses du soir à ce chantier.
- **La session de fiche coche** (étape 6 bis de `/vlp:tache`) ; elle ne commite pas
  et ne clôt pas. La boucle relit l'instantané, commite sur ACCEPTÉE, puis lance la
  session `clore`.
- **Ce qui demande deux oui** (`methode-chantier.md`, « La TODO ne grossit pas ») va au
  matin. `git push` : jamais la nuit.
- **Pointé, pas recopié** : les modèles, les plafonds et le délai de chaque rôle sont
  dans `scripts/boucle.py` (`ROLES`) ; les clés du carnet dans `scripts/carnet.py`.

## Une ligne par attente

| Où | Ce qui attend l'humain | La nuit, à la place |
|---|---|---|
| `skills/tache/SKILL.md:29-30` | une permission refusée : « demande de l'autoriser » | Un arrêt, avec le refus brut. Aucun contournement. |
| `skills/tache/SKILL.md:41` | plusieurs voisins : « demande lequel » | Sans objet, `PROJET=` est le worktree du canal. Une carte qui dit pourtant `VOISIN=` sans projet : un arrêt. |
| `skills/tache/SKILL.md:43` | `ATTENTE=` : republier d'abord | Noté au compte rendu, pas republié. |
| `skills/tache/SKILL.md:44` | `PLUGIN_RETARD=` : le dire, sa commande sur le oui | Noté au compte rendu. Ni `/reload-plugins` ni merge : le geste est de l'humain, le matin. |
| `skills/tache/SKILL.md:46-48` | fichier de fiches « aucun », `GARDE:`, extraction vide | Un arrêt, la sortie brute. La boucle met le chantier de côté. |
| `skills/tache/SKILL.md:59` | le mot `commentaires` : lire les fils, demander quoi en faire | Ignoré. Les commentaires ne sont pas lus : des données, et personne ne répond. |
| `skills/tache/SKILL.md:68-69` | fiche trop courte, socle à zéro, `GARDE:` | Un arrêt, la sortie brute. |
| `skills/tache/SKILL.md:74-75` | fiche introuvable, déjà cochée, ou dépendante d'une non cochée : « demande s'il faut continuer » | Un arrêt. Jamais « continuer quand même ». |
| `skills/tache/SKILL.md:77-79` | un bloc « Tentatives » : annoncer le différent, sinon demander | Aucune piste listée n'est rejouée ; rien de différent à faire : un arrêt. |
| `skills/tache/SKILL.md:101-102` | un geste de l'utilisateur (recharger, regarder un écran) | Un arrêt : personne pour le faire. La boucle arrête déjà sur une fiche `(visuel)`. |
| `skills/tache/SKILL.md:105-107` | la limite de tentatives : arrêt, erreur brute, `tache-blocage.md` | Un arrêt à cette limite, l'erreur brute et ce qui a été essayé. `tache-blocage.md` s'applique, sauf ce que la ligne suivante remplace. |
| `skills/tache/SKILL.md:124` | un critère `(visuel)` : attendre son retour | Pas de retour : un arrêt, la case non cochée. |
| `skills/tache/SKILL.md:145-148` | commiter sans demander | La session de fiche ne commite pas : la boucle le fait sur ACCEPTÉE. La session `clore` commite sa clôture (`cloture.md`, le commit de clôture). |
| `skills/tache/SKILL.md:155-166` | la dernière fiche : appliquer la clôture, les liens, `/clear` | Avec une fiche donnée : ne clôt pas, rend la main après 6 bis — la boucle lance `clore`. Sans fiche : la clôture seule, sans lien ni `/clear` à rappeler. |
| `skills/tache/references/tache-blocage.md:43-46` | jeter les essais (`git checkout -- .`) ou les laisser | Ni jeter ni `git checkout` : l'arbre reste tel quel, la boucle le commite `WIP` en mettant le chantier de côté. |
| `ARTEFACTS.md:101-103` | une tâche planifiée proposée, créée sur le oui | Aucune proposition, aucune tâche. La page reste en attente, et la carte du matin le dit. |
| `cloture.md:17-19` | un reste qui garderait la ligne de la TODO ouverte : deux oui | La ligne se retire. Le reste est noté pour le matin, qui demande les deux oui. |
| `cloture.md:40-41` | une `GARDE:` de `clore` : « écris-le alors à la main » | Pas à la main : un arrêt, la sortie brute. Le chantier reste ouvert, la boucle le met de côté. |
| `cloture.md:80-107` | le menu de fin : brainstorm, appris, essaimer, dette | Pas posé. Ses quatre cases vont au matin, une note chacune. Case 3 : `niveau` voit de faux écarts dans un worktree, jamais lancé la nuit. Case 4 : une dette « tout de suite » ne se corrige pas la nuit. |
| `cloture.md:109-114` | le push, une question à lui seul | Jamais de `git push` la nuit. Le matin le demande, par une question à lui seul. |
| `skills/chantier/SKILL.md:40-42` | plusieurs voisins : un questionnaire | Sans objet, comme pour `/vlp:tache`. Un arrêt si la carte n'a pas de `PROJET=`. |
| `skills/chantier/SKILL.md:85-88` | un chantier déjà ouvert : reprendre, redécouper ou clore | Un arrêt, sans choix proposé : un chantier déjà ouvert arrête le canal. |
| `skills/chantier/SKILL.md:135-147` | comprendre le chantier : résultat, frontière, inconnues | Pas de questionnaire : ces réponses sont dans le plan du soir. Un point que le plan ne dit pas ne se devine pas : le découpage prend le plus sûr. |
| `skills/chantier/SKILL.md:151-153` | le découpage proposé, la validation demandée | Pas de validation. Une réponse `découpage :` du plan est suivie, elle a été validée le soir ; sans elle, le découpage est seul, au plus sûr — des fiches courtes, en nombre que la boucle accepte. |
| `skills/chantier/SKILL.md:156-163` | le préfixe de fiche annoncé, l'utilisateur tranche | Le préfixe est celui du plan, choisi et vérifié le soir. Jamais proposé, jamais changé. Pris entre-temps : un arrêt. |
| `skills/chantier/SKILL.md:182-183` | des gabarits introuvables : « demande le chemin » | Un arrêt. Les gabarits ne se refont pas de mémoire. |
| `skills/chantier/SKILL.md:282-283` | un avertissement de `valider` ou une `GARDE:` de `page` : proposer d'alléger | Un arrêt, la sortie brute. Un avertissement met le chantier de côté. |
| `skills/chantier/SKILL.md:285-287` | le lien, la première fiche, `/clear` à rappeler | L'arrêt final, sans `/clear` à rappeler. C'est le signal de la boucle : elle lit la carte à la sortie, un fichier de fiches courant vaut chantier découpé. |
| `skills/enchainer/SKILL.md:112-117` et `skills/enchainer/references/refus.md:15-22` | un `RETOUR` ou une fiche `REFUSÉE` : un questionnaire | `/vlp:enchainer` ne tourne pas la nuit. La boucle tranche seule (`garde_de`) : relance, ou arrêt. La ligne `RÉÉCRITURE :` va au carnet, pour le matin. |
| `skills/chef/SKILL.md` | toute la commande : le modèle, le tri, la page de questions, ses réponses, le plan | `/vlp:chef` ne se joue pas sous `NUIT=1` : un arrêt. Le plan s'écrit avant le lancement, par un humain présent ; `plan ecrire` refuse sous `VLP_NUIT=1`. |
