/*
  vlp.js — les boutons des pages du kit : page du chantier et feuille de route.
  Joint à chaque page comme vlp.css : la source est ici, `vlp.py page` et
  `vlp.py feuille` la recopient à côté de la page, et leur ligne FILES dit quoi
  joindre à la publication (chantier BTN).
  Aucun code de bouton dans le HTML : ce fichier fabrique ses boutons au
  chargement, à partir des crochets que la page porte déjà ; il pose des
  classes, jamais d'attribut style — les styles vivent dans vlp.css.
  BTN3 : tout déplier et tout replier, sous le titre de chaque liste de
  cartes ; copier la commande d'une fiche prête, dans la colonne de gauche.
  BTN4 : filtrer la feuille par état, sous son sommaire.
*/
(() => {
  const page = document.querySelector(".page");
  if (!page) return;

  const bouton = (texte, classe) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "bouton " + classe;
    b.textContent = texte;
    return b;
  };

  // Tout déplier, tout replier : deux boutons sous le titre de chaque liste de cartes — fiches
  // du chantier, chantiers possibles —, qui n'ouvrent et ne ferment que les cartes de la liste.
  page.querySelectorAll("ul.fiches, ol.todo").forEach((liste) => {
    const titre = liste.closest("section")?.querySelector("h2");
    if (!titre || !liste.querySelector("details")) return;
    const replis = document.createElement("span");
    replis.className = "replis";
    [["Tout déplier", true], ["Tout replier", false]].forEach(([texte, ouvrir]) => {
      const b = bouton(texte, "deplier");
      b.addEventListener("click", () => {
        liste.querySelectorAll("details").forEach((d) => { d.open = ouvrir; });
      });
      replis.append(b);
    });
    titre.after(replis);
  });

  // Copier : dans la colonne de gauche de chaque fiche prête — non faite, et sans `data-attend`,
  // que vlp.py pose sur une fiche dont une dépendance n'est pas faite —, sous son identifiant ;
  // copie `/vlp:tache <ID>`.
  page.querySelectorAll("li.fiche").forEach((li) => {
    const id = li.querySelector("span.id");
    const gauche = li.querySelector(".gauche");
    if (li.dataset.etat === "faite" || li.hasAttribute("data-attend") || !id || !gauche) return;
    const commande = "/vlp:tache " + id.textContent.trim();
    const copier = bouton("Copier", "copier");
    copier.addEventListener("click", () => {
      Promise.resolve()
        .then(() => navigator.clipboard.writeText(commande))
        .then(() => { copier.textContent = "Copié."; })
        .catch(() => {
          // Presse-papiers refusé : une ligne sous la carte, la commande sélectionnée.
          let ligne = li.querySelector(".copie");
          if (!ligne) {
            ligne = document.createElement("span");
            ligne.className = "copie";
            const zone = document.createElement("input");
            zone.className = "commande";
            zone.readOnly = true;
            zone.value = commande;
            zone.setAttribute("aria-label", "Commande à copier");
            ligne.append(zone, "Sélectionné : fais Ctrl+C");
            li.append(ligne);
          }
          const zone = ligne.querySelector("input");
          zone.focus();
          zone.select();
        });
    });
    gauche.append(copier);
  });

  // Filtrer par état : sur la feuille seulement (elle a #todo et #clos), quatre boutons sous le
  // sommaire, un seul enfoncé. Quitter « Tout » retient l'état des replis ; y revenir le rend.
  const sommaire = page.querySelector("nav.sommaire");
  const encours = document.getElementById("encours");
  const todo = document.getElementById("todo");
  const clos = document.getElementById("clos");
  if (!sommaire || !todo || !clos) return;
  const cartes = [...todo.querySelectorAll("li.carte-todo")];
  const enCours = (li) => !!li.querySelector('.badge[data-etat="cours"]');
  const replisClos = [...clos.querySelectorAll("details")];
  let avant = null; // l'état des replis de #clos au moment de quitter « Tout »
  const filtres = {
    tout: () => true,
    afaire: (li) => !enCours(li),
    cours: enCours,
    clos: () => false,
  };
  const filtrer = (etat) => {
    if (etat === "tout") {
      if (avant) replisClos.forEach((d, i) => { d.open = avant[i]; });
      avant = null;
    } else if (!avant) {
      avant = replisClos.map((d) => d.open);
    }
    if (encours) encours.hidden = !(etat === "tout" || etat === "cours");
    todo.hidden = etat === "clos";
    clos.hidden = !(etat === "tout" || etat === "clos");
    cartes.forEach((li) => { li.hidden = !filtres[etat](li); });
    if (etat === "clos") replisClos.forEach((d) => { d.open = true; });
  };
  const barre = document.createElement("div");
  barre.className = "filtres";
  barre.setAttribute("role", "group");
  barre.setAttribute("aria-label", "Filtrer par état");
  [["Tout", "tout"], ["À faire", "afaire"], ["En cours", "cours"], ["Clos", "clos"]].forEach(([texte, etat]) => {
    const b = bouton(texte, "filtre");
    b.setAttribute("aria-pressed", String(etat === "tout"));
    b.addEventListener("click", () => {
      barre.querySelectorAll(".filtre").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      filtrer(etat);
    });
    barre.append(b);
  });
  sommaire.after(barre);
})();
