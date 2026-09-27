/*
  vlp.js — les boutons des pages du kit : page du chantier et feuille de route.
  Joint à chaque page comme vlp.css : la source est ici, `vlp.py page` et
  `vlp.py feuille` la recopient à côté de la page, et leur ligne FILES dit quoi
  joindre à la publication (chantier BTN).
  Aucun code de bouton dans le HTML : ce fichier fabrique ses boutons au
  chargement, à partir des crochets que la page porte déjà ; il pose des
  classes, jamais d'attribut style — les styles vivent dans vlp.css.
  BTN3 : tout déplier et tout replier, sous le titre de chaque liste de
  cartes ; copier la commande d'une fiche prête, dans la colonne de gauche. BTN4 (filtrer la feuille par état)
  viendra ici aussi.
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
  // que vlp.py pose sur une fiche dont une dépendance n'est pas faite —, sous son état et avant
  // ses dépendances et son « ∥ avec … » ; copie `/vlp:tache <ID>`.
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
    gauche.insertBefore(copier, gauche.querySelector(".dep, .avec"));
  });
})();
