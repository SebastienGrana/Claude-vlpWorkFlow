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
  Le graphique des coûts : Chart.js (MIT), chargé à la demande sur la feuille —
  pas de roue réinventée pour les axes et les bulles (demande du 2026-09-28).
  Lecture (2026-10-05) : un nombre ne se coupe plus en fin de ligne.
  Écouter (2026-10-06) : la page lue à voix haute, en tête de page.
*/
(() => {
  const page = document.querySelector(".page");
  if (!page) return;

  // Nombres et dates jamais coupés : « 5 069 068 », « 2,57 $ », « 41 tours », « 3 fiches »
  // reçoivent une espace insécable ; une date (« 2026-09-30 ») ou une plage (« MOR1–MOR14 »)
  // passe dans un `span.insecable`. À l'affichage seulement : vlp.py écrit des espaces ordinaires,
  // que ses propres lectures de la page attendent. Le texte brut (pre) et les scripts n'y passent pas.
  const insecable = /(\d) (?=\d{3}(?!\d)|\$|(?:tours|fiches?|tokens)\b)/g;
  const bloc = /(\d{4}-\d\d-\d\d|[A-Z]{2,4}\d+–[A-Z]{2,4}\d+)/;
  const textes = [];
  const marche = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
  for (let n = marche.nextNode(); n; n = marche.nextNode()) {
    if (!n.parentElement.closest("pre, script")) textes.push(n);
  }
  textes.forEach((n) => {
    const morceaux = n.data.replace(insecable, "$1 ").split(bloc);
    if (morceaux.length === 1) {
      if (morceaux[0] !== n.data) n.data = morceaux[0];
      return;
    }
    n.replaceWith(...morceaux.map((m, i) => {
      if (i % 2 === 0) return m;
      const s = document.createElement("span");
      s.className = "insecable";
      s.textContent = m;
      return s;
    }));
  });

  const bouton = (texte, classe) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = classe ? "bouton " + classe : "bouton";
    b.textContent = texte;
    return b;
  };

  // Écouter : la voix du navigateur (Web Speech, sans paquet ; essayée dans le cadre d'un artefact
  // le 2026-10-06) lit la sélection s'il y en a une, sinon le texte visible de la page — une carte
  // repliée ne se lit pas. Un morceau par ligne ou par phrase : certains navigateurs coupent une
  // lecture trop longue. Ce qui se passe s'affiche à côté du bouton, et une erreur part en console.
  // « Plus lent » et « Plus vite » changent la vitesse, gardée dans le navigateur ; en pleine
  // lecture, la phrase en cours reprend à la nouvelle vitesse.
  const voix = window.speechSynthesis;
  const entete = page.querySelector("header");
  if (voix && entete) {
    const sansEmoji = (t) => t.replace(/\p{Extended_Pictographic}/gu, "").trim();
    const CLE_VITESSE = "vlp-vitesse";
    const [LENTE, RAPIDE, PAS] = [0.75, 2, 0.25];
    let vitesse = 1.25; // plus vite que la normale (1), à sa demande du 2026-10-06
    try {
      const gardee = Number(localStorage.getItem(CLE_VITESSE));
      if (gardee >= LENTE && gardee <= RAPIDE) vitesse = gardee;
    } catch (e) { console.warn("vlp.js — vitesse gardée illisible :", e); }
    const ecoute = document.createElement("div");
    ecoute.className = "ecoute";
    const lire = bouton("🔊 Écouter", "ecouter");
    const taire = bouton("Arrêter");
    taire.hidden = true;
    const lent = bouton("Plus lent");
    const vite = bouton("Plus vite");
    const cadence = document.createElement("span");
    cadence.className = "cadence mono";
    const suivi = document.createElement("span");
    suivi.className = "suivi";
    suivi.setAttribute("aria-live", "polite");
    const montrer = () => {
      cadence.textContent = "× " + vitesse.toLocaleString("fr-FR");
      lent.disabled = vitesse <= LENTE;
      vite.disabled = vitesse >= RAPIDE;
    };
    const fin = (texte) => { taire.hidden = true; suivi.textContent = texte; };
    let morceaux = [];
    let choisi = "";
    let encours = -1; // le morceau qui se lit, -1 hors lecture
    let numero = 0; // la dernière lecture lancée : une ancienne ne parle plus à sa place
    const lancer = (depart) => {
      voix.cancel();
      const tour = ++numero;
      const fr = voix.getVoices().find((v) => v.lang.toLowerCase().startsWith("fr"));
      let parti = false;
      morceaux.slice(depart).forEach((m, k) => {
        const i = depart + k;
        const phrase = new SpeechSynthesisUtterance(m);
        phrase.lang = "fr-FR";
        phrase.rate = vitesse;
        if (fr) phrase.voice = fr;
        phrase.onstart = () => {
          if (tour !== numero) return;
          encours = i;
          if (parti) return;
          parti = true;
          taire.hidden = false;
          suivi.textContent = choisi ? "Lecture de la sélection…" : "Lecture de la page…";
        };
        if (i === morceaux.length - 1) phrase.onend = () => {
          if (tour !== numero) return;
          encours = -1;
          fin("Lecture finie.");
        };
        phrase.onerror = (e) => {
          if (tour !== numero || e.error === "interrupted" || e.error === "canceled") return;
          console.warn("vlp.js — voix en erreur :", e.error);
          encours = -1;
          fin("Erreur de la voix : " + e.error);
        };
        voix.speak(phrase);
      });
      suivi.textContent = "Lancement…";
      setTimeout(() => {
        if (parti || tour !== numero) return;
        console.warn("vlp.js — la voix n'a pas démarré en 3 s");
        fin("La voix n'a pas démarré.");
      }, 3000);
    };
    lire.addEventListener("click", () => {
      choisi = String(window.getSelection() || "").trim();
      suivi.textContent = "";
      const etiquettes = new Set([...page.querySelectorAll("button")].map((b) => sansEmoji(b.textContent)));
      morceaux = sansEmoji(choisi || page.innerText)
        .split(/\n+|(?<=[.!?;:])\s+/)
        .map((m) => m.trim())
        .filter((m) => m && !etiquettes.has(m) && m !== cadence.textContent);
      if (!morceaux.length) { fin("Rien à lire."); return; }
      lancer(0);
    });
    const changer = (pas) => {
      vitesse = Math.min(RAPIDE, Math.max(LENTE, vitesse + pas));
      try { localStorage.setItem(CLE_VITESSE, String(vitesse)); }
      catch (e) { console.warn("vlp.js — vitesse non gardée :", e); }
      montrer();
      if (encours >= 0) lancer(encours);
    };
    lent.addEventListener("click", () => changer(-PAS));
    vite.addEventListener("click", () => changer(PAS));
    taire.addEventListener("click", () => { numero++; encours = -1; voix.cancel(); fin("Arrêté."); });
    montrer();
    ecoute.append(lire, taire, lent, cadence, vite, suivi);
    entete.append(ecoute);
  }

  // Tout déplier, tout replier : deux boutons sous le titre de chaque liste de cartes — fiches
  // du chantier, chantiers possibles —, qui n'ouvrent et ne ferment que les cartes de la liste.
  page.querySelectorAll("ul.fiches, ol.todo").forEach((liste) => {
    const titre = liste.closest("section")?.querySelector("h2");
    if (!titre || !liste.querySelector("details")) return;
    const replis = document.createElement("span");
    replis.className = "replis";
    [["Tout déplier", true], ["Tout replier", false]].forEach(([texte, ouvrir]) => {
      const b = bouton(texte);
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

  // Le graphique des coûts : l'image couts.svg porte ses barres dans `data-couts` (vlp.py,
  // `donnees_couts`). Chart.js, chargé à la demande, la remplace par un graphique à axe gradué
  // dont chaque barre, survolée ou touchée, dit son chantier et son coût. Sans Chart.js (hors
  // ligne, bloqué), l'image reste.
  const image = page.querySelector('img[src="couts.svg"][data-couts]');
  if (image) {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js";
    script.addEventListener("load", () => {
      let donnees;
      try { donnees = JSON.parse(image.dataset.couts); } catch { return; }
      const { couleur, barres } = donnees;
      const style = getComputedStyle(document.documentElement);
      const doux = style.getPropertyValue("--doux").trim();
      const ligne = style.getPropertyValue("--line").trim();
      const millions = (v) => v === 0 ? "0" : v >= 1e6
        ? (v / 1e6).toLocaleString("fr-FR", { maximumFractionDigits: 1 }) + "M"
        : (v / 1e3).toLocaleString("fr-FR", { maximumFractionDigits: 1 }) + "k";
      const cadre = document.createElement("div");
      cadre.className = "graphique";
      const toile = document.createElement("canvas");
      toile.setAttribute("role", "img");
      toile.setAttribute("aria-label", image.alt);
      cadre.append(toile);
      image.before(cadre);
      new window.Chart(toile, {
        type: "bar",
        data: {
          labels: barres.map((b) => b[0]),
          datasets: [{ data: barres.map((b) => b[1]), backgroundColor: couleur }],
        },
        options: {
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { display: false },
            tooltip: {
              titleFont: { size: 14 },
              bodyFont: { size: 14 },
              callbacks: { label: (c) => barres[c.dataIndex][2] + " tokens" },
            },
          },
          scales: {
            x: {
              ticks: { display: false },
              grid: { display: false },
              title: { display: true, text: "du plus ancien au plus récent →", color: doux },
            },
            y: {
              beginAtZero: true,
              ticks: { color: doux, callback: millions },
              grid: { color: ligne },
            },
          },
        },
      });
      image.hidden = true;
    });
    document.head.append(script);
  }

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
