# Index du contexte <projet>

**`CLAUDE.md`, à la racine, est le fichier d'entrée** : il porte l'identité du
projet, l'état en cinq lignes, les règles, et une table « tâche → fichier » qui
suffit dans presque tous les cas. Cet index-ci ne sert que lorsque la tâche n'y
figure pas.

Un fichier = un sujet. **Ne charger que ce que la tâche demande.**
Chaque fichier s'ouvre sur une ligne « QUAND LIRE » : elle seule décide. Si
elle ne décrit pas la tâche en cours, le fichier n'est pas à ouvrir, même s'il
a l'air proche.

## Stable — ce qui ne bouge presque plus

| Fichier | Lire quand |
|---|---|
| `<NN>-etat.md` | on reprend après une interruption, ou on choisit quoi faire ensuite |
| *(hors dossier)* `methode-chantier.md`, à la racine du kit | on ouvre un chantier, ou on le découpe en fiches — la méthode n'est pas recopiée ici, elle voyage avec le plugin `vlp` et sert tous les projets |

## Chantiers — un fichier de fiches par chantier

| Fichier | Lire quand |
|---|---|
| `<NN>-<chantier>.md` | on joue une fiche `<X>*` — chantier **ouvert** |
| `<NN>-<chantier>.md` | **clos** — ne se rejoue pas, garde son socle d'API |

## <Autres familles>

<Une famille par sujet. Ces fichiers ne se lisent pas en série : chacun répond
à une question précise, ouvrir le voisin ne donne pas de contexte, seulement du
volume.>
