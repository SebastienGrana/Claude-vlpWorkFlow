/*
  vlp.js — les boutons des pages du kit : page du chantier et feuille de route.
  Joint à chaque page comme vlp.css : la source est ici, `vlp.py page` et
  `vlp.py feuille` la recopient à côté de la page, et leur ligne FILES dit quoi
  joindre à la publication (chantier BTN).
  Aucun code de bouton dans le HTML : ce fichier fabrique ses boutons au
  chargement, à partir des crochets que la page porte déjà ; il pose des
  classes, jamais d'attribut style — les styles vivent dans vlp.css.
  BTN3 : tout déplier, copier la commande d'une fiche. BTN4 (filtrer la
  feuille par état) viendra ici aussi.
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

  // Tout déplier : en tête de .page, si la page a au moins un details.
  if (page.querySelector("details")) {
    const deplier = bouton("Tout déplier", "deplier");
    deplier.addEventListener("click", () => {
      const ouvrir = deplier.textContent === "Tout déplier";
      page.querySelectorAll("details").forEach((d) => { d.open = ouvrir; });
      deplier.textContent = ouvrir ? "Tout replier" : "Tout déplier";
    });
    page.prepend(deplier);
  }

  // Copier : dans le summary de chaque fiche non faite, copie `/vlp:tache <ID>`.
  page.querySelectorAll("li.fiche").forEach((li) => {
    const id = li.querySelector("span.id");
    const sommaire = li.querySelector("summary");
    if (li.dataset.etat === "faite" || !id || !sommaire) return;
    const commande = "/vlp:tache " + id.textContent.trim();
    const copier = bouton("Copier", "copier");
    copier.addEventListener("click", (e) => {
      e.preventDefault(); // le clic ne replie pas la fiche
      Promise.resolve()
        .then(() => navigator.clipboard.writeText(commande))
        .then(() => { copier.textContent = "Copié."; })
        .catch(() => {
          // Presse-papiers refusé : la commande dans un champ, sélectionnée.
          let zone = sommaire.querySelector("input.commande");
          if (!zone) {
            zone = document.createElement("input");
            zone.className = "commande";
            zone.readOnly = true;
            zone.value = commande;
            zone.setAttribute("aria-label", "Commande à copier");
            zone.addEventListener("click", (ev) => ev.preventDefault());
            sommaire.append(zone);
          }
          zone.focus();
          zone.select();
          copier.textContent = "Sélectionné : fais Ctrl+C";
        });
    });
    sommaire.append(copier);
  });
})();
