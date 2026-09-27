> **QUAND LIRE** : on joue une fiche `VID*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache VID<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier VID — Une page vide ne part plus en ligne

**À quoi il sert.** Le 2026-09-27, une page Cairn est partie en ligne vide (commentaire jamais
fermé, CSS et texte avalés) ; rien ne l'a vue avant l'utilisateur. Un vigile par script la refuse avant `Artifact`.

**Estimé.** 0,5 fiches · ≈2,02 $ — ≈4,04 $/fiche sur 66 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** VID1..VID2 (2026-09-27) : vlp.py vigile et son hook PreToolUse sur Artifact : une page .html cassée (commentaire ouvert, aucun style, aucun bloc) est refusée avec sa raison, essayé pour de vrai — estimé 0,5 fiches ≈2,02 $ · cadré 2 · joué 2 fiches ≈9,92 $.

**Session** : fe900b64-3cf4-4545-abb2-d0f62b776645

## Le socle commun

Tranché avec l'utilisateur au cadrage (page à cartes, 2026-09-27) :

- **Toute page** `.html` publiée, du kit ou non ; appelé par un **hook** `PreToolUse` sur `Artifact`.
- **Bloquer** : une page cassée ne part pas (`permissionDecision` `deny`, sa raison).
- Trois défauts, rien d'autre : **commentaire ouvert** (`<!--` sans `-->` après lui) ;
  **aucun style** (ni balise `style`, ni `link` `rel="stylesheet"` — `vlp.css` passe par là) ;
  **moins d'un bloc** de texte visible.
- **Dehors** : vérifier que `vlp.css` est joint dans `files` (faux refus à la republication :
  un fichier omis reste en ligne) ; une page `.md` ; un envoi `asset: true`.
- Hook échoue à bloquer `Artifact` → **repli** : les commandes appellent le vigile avant de
  publier (voir `VID2`).

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `textes_visibles(html_)` | `scripts/vlp.py:3124` | les blocs de texte visible — à réutiliser, pas à recopier |
| `cmd_gardien` | `scripts/vlp.py:1730` | le moule : JSON d'entrée lu sur stdin, muet s'il ne le lit pas, `deny` en `hookSpecificOutput` |
| sous-commandes | `scripts/vlp.py:4069`, `:4140` | l'enregistrement et l'aiguillage de `gardien` : faire pareil |
| tests du gardien | `scripts/test-vlp.py:2529` | `mod.main([...], sortie, stdin)` et `verifier(nom, cond, sortie)` |

Nom retenu : **`vlp.py vigile`**. Sans argument, il lit l'entrée du hook sur stdin ; avec
un chemin, il juge ce fichier à la main (le repli) et rend une ligne `GARDE:` par défaut, ou
`PAGE SAINE <n> blocs`. Un test bâtit ses pages dans un dossier temporaire, jamais le vrai
dépôt ; un nouveau `with tempfile…` prend son propre nom de variable (piège déjà vu : un `t`
réemployé efface le dossier d'un voisin). `pyright scripts/` reste à **0 erreur**.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `VID1` | Écrire `vlp.py vigile`, testé | rien |
| `VID2` | Brancher le hook avant `Artifact`, et l'essayer pour de vrai | `VID1` |

Rien de parallèle : le hook appelle le script. Si `VID2` prouve que le hook ne bloque pas
`Artifact`, elle rend `RETOUR` et une fiche de repli (les commandes appellent le vigile) se découpe alors.

---

<!-- FICHE:VID1 -->
## VID1 [x] — Écrire `vlp.py vigile`, testé

**Session** : aeb2fbf2-07df-4411-aa44-ce09d4a28413
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute à `scripts/vlp.py` une fonction `defauts_page(html_)` qui rend la liste des défauts du
socle (vide si la page est saine), et la sous-commande `vigile` qui l'appelle, enregistrée et
aiguillée comme `gardien`, décrite dans la docstring du module en une ligne.
Mode hook (stdin) : `hook_event_name` `PreToolUse`, `tool_name` `Artifact`, `tool_input.file_path`
en `.html`, pas d'`asset` vrai ; fichier lisible et défauts → `deny` dont la raison nomme
chaque défaut et le fichier. Tout autre cas, entrée illisible comprise : muet, rien écrit.
Mode fichier : une ligne `GARDE:` par défaut, ou `PAGE SAINE <n> blocs`.
Les blocs visibles viennent de `textes_visibles`, rien de recompté à part.
Tests dans `scripts/test-vlp.py`, pages écrites dans un dossier temporaire : une page saine
(style, texte) ; une page Cairn reconstituée — un commentaire de tête qui s'ouvre et ne se
ferme jamais, un style et du texte derrière lui ; une page sans style ; une page sans bloc ;
une page stylée par un seul `link` ; en hook, un `Bash`, un `.md` et un JSON illisible, muets.

**Critère de fin**
`py scripts/test-vlp.py` : tous passent, compte brut avant/après affiché (nouveaux tests
nommés `vigile : …`). Trois mutants, chacun rejoué puis défait, font tomber au moins un
test `vigile` : ne plus chercher de commentaire ouvert ; accepter une page sans style ;
accepter zéro bloc. `pyright scripts/` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:VID2 -->
## VID2 [x] — Brancher le hook avant `Artifact`, et l'essayer pour de vrai

**Session** : aeb2fbf2-07df-4411-aa44-ce09d4a28413
**Dépend de** : `VID1`.
**Fichiers** : `hooks/hooks.json`, `ARTEFACTS.md` — et rien d'autre.

**Prompt**
Dans `hooks/hooks.json`, ajoute sous `PreToolUse` une entrée `matcher` `Artifact` qui lance
`vlp.py vigile`, avec les deux commandes `python3` et `py` comme l'entrée `Bash|PowerShell`.
Dans `ARTEFACTS.md`, une ligne dit que le vigile refuse une page cassée avant sa publication,
et renvoie au socle de `context AI/79-vigile.md` pour les trois défauts — sans les recopier.
Puis l'essai réel, que seul le chef peut faire (`/reload-plugins`, puis `Artifact`) : publier
une page cassée dans le dossier temporaire de la session — elle doit être refusée, raison
lue — puis une page saine, qui doit partir. Si la page cassée part : `RETOUR`, en disant ce
que le hook a reçu, s'il a tiré ; c'est le repli du socle.

**Critère de fin** (visuel)
La page cassée est refusée avec une raison qui nomme ses défauts ; la page saine est publiée
(son URL). `py scripts/vlp.py valider` et `py scripts/test-vlp.py` passent, comptes bruts affichés.
<!-- /FICHE -->
