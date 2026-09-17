> **QUAND LIRE** : on joue une fiche `C*` de ce chantier, ou on se demande où il
> en est. `/vlp:tache C<n>` n'en lit que le socle commun et sa fiche — jamais ce
> fichier en entier.

# Chantier C — Afficher la conso sur toutes les pages

**CLOS** le 2026-09-17. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**À quoi il sert.** Le chantier M (clos) mesure les tokens consommés mais ne
les affiche que dans `context AI/08-etat.md` et sur sa propre page. Ici, on
propage cet affichage à **toutes** les pages : chaque fiche de l'artefact de
chantier montre son coût, un total apparaît en bas de chaque liste (fiches
d'un chantier, chantiers clos de la feuille de route). Pas de cumul
inter-projet — chaque page ne parle que d'elle-même.

**Fait.** Rien. Ouvert le 2026-09-11, cadré en 2 fiches, `C1` à jouer.

## Le socle commun

**La convention d'affichage — fixée par C1, réutilisée partout ensuite.**
Un nombre < 1000 s'affiche tel quel. Au-delà : `≈<arrondi 1 décimale><k|M>
(<compte brut>)` — virgule française, `k` pour mille, `M` pour million. Le
compte brut reste toujours visible à côté (règle n°2 du kit : jamais de verdict
sans le compte qui le justifie), en plus petit / discret (classe `.mono`,
couleur `--doux`, déjà dans le CSS des deux gabarits).

Exemples : `847` reste `847` ; `118934` devient `≈119 k (118 934)` ;
`13030459` devient `≈13,0 M (13 030 459)`.

| Symbole | Fichier:ligne | Ce qu'il rend |
|---|---|---|
| Sortie de mesure | `scripts/mesure-tokens.py:64-79` | table TSV : `fichier input output cache_creation cache_read total lignes_invalides`, plus une ligne `TOTAL` si plusieurs fichiers passés |
| Coût de la fiche | `commands/tache.md:260-271` | calcule déjà le coût de la fiche **et** le cumul du chantier (deux tables), les affiche dans la session — ne les écrit pas encore sur une page |
| Régénérer l'artefact | `commands/tache.md:273-320` | les 4 gestes existants ; garde de taille 250 lignes (`commands/tache.md:322-331`) |
| Liste des fiches | `templates/artefact-chantier.html:72-89` | `ZONE:fiches`, chaque `<li class="fiche">` porte une `.note` |
| Chantiers clos | `templates/artefact-feuille-de-route.html:98-115` | `ZONE:clos`, table sans colonne coût aujourd'hui |
| Total à la clôture | `cloture.md:36-42` | calcule déjà le total du chantier qui se clôt, le verse dans le bilan du fichier d'état — pas encore sur une page |
| Republication des pages | `cloture.md:55-77` | séquence lire/réécrire/republier, artefact du chantier puis feuille de route |

**Ce qu'on ne fait pas** : pas de cumul entre projets équipés (tranché à
l'étape 3) ; pas de nouvel artefact ; pas de compteur qui vivrait à chaque
fiche sur la feuille de route — elle ne bouge qu'à l'ouverture et à la
clôture (`ARTEFACTS.md:24-30`), donc son total par chantier n'est écrit
**qu'une fois**, à la clôture.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `C1` | Afficher le coût des fiches et le total, sur les deux gabarits | rien |
| `C2` | Régénérer rétroactivement la feuille de route et l'artefact M | `C1` |

Pas de parallélisation : C2 réutilise la convention et les zones que C1 crée.

---

<!-- FICHE:C1 -->
## C1 [x] — Afficher le coût des fiches et le total, sur les deux gabarits

**Session** : ca51f6e9-70dc-4fde-bb13-1eafb1e538db
**Dépend de** : rien.
**Fichiers** : `templates/artefact-chantier.html`, `templates/artefact-feuille-de-route.html`, `commands/tache.md`, `cloture.md` — et rien d'autre.

**Prompt**
1. Fixe la fonction de format du socle commun (arrondi + compte brut entre
   parenthèses) — elle n'existe nulle part encore, c'est cette fiche qui la
   pose.
2. `artefact-chantier.html` : dans chaque `<li class="fiche">` de
   `ZONE:fiches`, sous `.note`, ajoute une ligne de coût discrète (affichée
   seulement si la fiche porte une ligne `**Session**`). Sous la liste
   `.fiches`, ajoute une ligne de total du chantier. Reste sous 250 lignes.
3. `tache.md`, étape 6 bis (ligne 300, geste 3) : ajoute le report du coût de
   la fiche et du total du chantier — déjà calculés à l'étape « Coût de la
   fiche » (ligne 260) — sur la page. N'appelle pas `mesure-tokens.py` une
   troisième fois.
4. `artefact-feuille-de-route.html`, `ZONE:clos` (ligne 98) : ajoute une
   colonne « Tokens » à la table, et une ligne de total cumulé en pied de
   table (somme des chantiers clos qui portent un total).
5. `cloture.md`, étape 5 (ligne 69) : reporte dans `ZONE:clos` le total déjà
   calculé à l'étape 3 (ligne 36) — pas un second calcul — et met à jour la
   ligne de total cumulé.

**Critère de fin**
`grep -n "ZONE:" templates/artefact-chantier.html templates/artefact-feuille-de-route.html`
montre les mêmes marqueurs qu'avant (aucun renommé) ; `wc -l` des deux gabarits
reste sous 250 chacun ; `grep -n "mesure-tokens.py" commands/tache.md` montre
un seul bloc d'appel (pas de troisième appel ajouté). La preuve sur données
réelles vient en C2. **Critère de fin** (visuel) pour la convention elle-même
: relis les deux gabarits modifiés et confirme que le compte brut reste lisible
à côté de l'arrondi, pas caché dans un attribut.
<!-- /FICHE -->

---

<!-- FICHE:C2 -->
## C2 [x] — Régénérer rétroactivement la feuille de route et l'artefact M

**Session** : 9fed64c1-1851-4f12-8b99-7d65fcb6d956
**Dépend de** : `C1`.
**Fichiers** : aucun fichier local à modifier — deux artefacts distants (leurs
URL sont dans `CHANTIER.md`, table des chantiers clos et ligne « artefact
feuille de route ») — et `context AI/08-etat.md` en lecture seule, pour le
total déjà connu de M (13 030 459).

**Prompt**
1. Lis l'artefact feuille de route (`action: "read"`, son url dans
   `CHANTIER.md`). Dans `ZONE:clos` : la ligne du chantier M reçoit son total
   (13 030 459) selon la convention de C1 ; la ligne du chantier E reçoit la
   mention « non mesurable » (le script `mesure-tokens.py` n'existait pas
   encore à sa clôture, le 2026-09-10) — jamais un zéro inventé. Ajoute la
   ligne de total cumulé posée par C1 (= le total de M seul, E exclu).
   Republie même `url`, sans `favicon`, `label` : `conso rétroactive`.
2. Lis l'artefact du chantier M (son url est dans la table des chantiers clos
   de `CHANTIER.md`). Dans sa `ZONE:bilan` (déjà remplie à sa clôture), ajoute
   la ligne de coût du chantier selon la même convention. Republie même `url`,
   sans `favicon`, `label` : `conso rétroactive`.
3. Ne touche pas à l'artefact du chantier E : pas de total à y afficher.

**Critère de fin**
Relecture des deux artefacts republiés : la feuille de route montre la colonne
Tokens sur la ligne M (avec le compte brut entre parenthèses) et « non
mesurable » sur la ligne E ; l'artefact M montre son total dans `ZONE:bilan`.
<!-- /FICHE -->
