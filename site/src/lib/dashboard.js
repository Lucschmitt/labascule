/**
 * dashboard.js — Helper de calcul pur pour le tableau de bord longitudinal
 * Projet La Bascule — https://github.com/Lucschmitt/labascule
 *
 * Aucune I/O. Toutes les fonctions prennent un tableau de fiches JSON
 * (déjà chargées, hors calibration) et retournent des données calculées.
 *
 * @module dashboard
 */

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

/** Critères de la sous-grille L (évaluables sur texte isolé) */
const CRITERES_L = ["C-01", "C-02", "C-13", "C-14", "C-15", "C-16", "C-17", "C-18", "C-19"];

/** Critères institutionnels (axe vertical du vecteur) */
const CRITERES_INST = ["C-06", "C-07", "C-08", "C-11"];

/** Critères rhétoriques (axe horizontal du vecteur) */
const CRITERES_RHET = ["C-03", "C-04", "C-05", "C-09", "C-10", "C-12"];

/** Tous les critères C (sous-grille contextuelle) */
const CRITERES_C = [...CRITERES_INST, ...CRITERES_RHET].sort();

/** Libellés des critères C pour les tooltips */
export const CRITERES_C_LABELS = {
  "C-03": "Normalisation discursive des positions extrêmes",
  "C-04": "Désignation d'un ennemi intérieur",
  "C-05": "Cadrage de crise permanente",
  "C-06": "Fragilisation des contre-pouvoirs",
  "C-07": "Pression ou capture des médias",
  "C-08": "Instrumentalisation des processus électoraux",
  "C-09": "Ralliement ou accommodation du centre-droit",
  "C-10": "Intimidation des opposants",
  "C-11": "Alignement avec régimes autoritaires étrangers",
  "C-12": "Accommodation des modérés par les extrêmes",
};

/** Palettes couleur partagée */
export const COLORS = {
  tealVeryLight: "#E1F5EE",
  tealLight: "#9FE1CB",
  tealMid: "#5DCAA5",
  tealDark: "#1D9E75",
  amber: "#EF9F27",
  coral: "#D85A30",
  coralDark: "#993C1D",
  red: "#712B13",
  grey: "#888780",
  noData: "#D0CFC9",
};

// ---------------------------------------------------------------------------
// Utilitaires internes
// ---------------------------------------------------------------------------

/**
 * Retourne la date de publication d'une fiche (fallback sur date_analyse).
 * @param {Object} fiche
 * @returns {Date|null}
 */
function ficheDate(fiche) {
  const raw = fiche?.source?.date_publication || fiche?.date_analyse;
  if (!raw) return null;
  const d = new Date(raw);
  return isNaN(d.getTime()) ? null : d;
}

/**
 * Formate une date en clé "YYYY-MM".
 * @param {Date} d
 * @returns {string}
 */
function toMonthKey(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

/**
 * Retourne la clé de mois N mois avant une date donnée.
 * @param {Date} ref
 * @param {number} n
 * @returns {string}
 */
function monthKeyOffset(ref, n) {
  const d = new Date(ref);
  d.setMonth(d.getMonth() - n);
  return toMonthKey(d);
}

/**
 * Soustrait N mois à une date et retourne la nouvelle Date.
 */
function subtractMonths(date, n) {
  const d = new Date(date);
  d.setMonth(d.getMonth() - n);
  return d;
}

/**
 * Filtre les fiches dont la date tombe dans [start, end[ (bornes en Date).
 * @param {Object[]} fiches
 * @param {Date} start
 * @param {Date} end
 * @returns {Object[]}
 */
function fichesInRange(fiches, start, end) {
  return fiches.filter((f) => {
    const d = ficheDate(f);
    if (!d) return false;
    return d >= start && d < end;
  });
}

/**
 * Retourne le score d'un critère dans une fiche, ou null si absent/non applicable.
 * @param {Object} fiche
 * @param {string} critereId
 * @param {boolean} requireApplicable — si true, retourne null si applicable=false
 * @returns {number|null}
 */
function getCritereScore(fiche, critereId, requireApplicable = true) {
  const criteres = fiche?.scoring?.criteres;
  if (!Array.isArray(criteres)) return null;
  const c = criteres.find((x) => x.id === critereId);
  if (!c) return null;
  if (requireApplicable && c.applicable === false) return null;
  if (typeof c.score !== "number") return null;
  return c.score;
}

/**
 * Calcule la moyenne d'un ensemble de critères sur un tableau de fiches.
 * Ignore les critères avec applicable=false ou score absent.
 * @param {Object[]} fiches
 * @param {string[]} critereIds
 * @returns {number|null} — null si aucune valeur disponible
 */
function avgCriteres(fiches, critereIds) {
  const values = [];
  for (const fiche of fiches) {
    for (const id of critereIds) {
      const s = getCritereScore(fiche, id, true);
      if (s !== null) values.push(s);
    }
  }
  if (values.length === 0) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * Interpolation linéaire entre deux stops couleur hex.
 * @param {string} hex1
 * @param {string} hex2
 * @param {number} t — 0..1
 * @returns {string} hex color
 */
function lerpColor(hex1, hex2, t) {
  const parse = (h) => [
    parseInt(h.slice(1, 3), 16),
    parseInt(h.slice(3, 5), 16),
    parseInt(h.slice(5, 7), 16),
  ];
  const [r1, g1, b1] = parse(hex1);
  const [r2, g2, b2] = parse(hex2);
  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------
// Indicateur 1 — Stripes mensuelles
// ---------------------------------------------------------------------------

/**
 * Stops de couleur pour les stripes (score → couleur).
 * Format : [seuil_bas, seuil_haut, couleur_bas, couleur_haut]
 */
const STRIPE_STOPS = [
  [0.00, 0.10, COLORS.tealVeryLight, COLORS.tealVeryLight],
  [0.10, 0.20, COLORS.tealVeryLight, COLORS.tealLight],
  [0.20, 0.30, COLORS.tealLight,     COLORS.tealMid],
  [0.30, 0.40, COLORS.tealMid,       COLORS.tealDark],
  [0.40, 0.55, COLORS.tealDark,      COLORS.amber],
  [0.55, 0.70, COLORS.amber,         COLORS.coral],
  [0.70, 0.85, COLORS.coral,         COLORS.coralDark],
  [0.85, 1.00, COLORS.coralDark,     COLORS.red],
];

/**
 * Convertit un score L (0..1) en couleur hex.
 * @param {number} score
 * @returns {string}
 */
export function scoreLToColor(score) {
  const s = Math.max(0, Math.min(1, score));
  for (const [lo, hi, cLo, cHi] of STRIPE_STOPS) {
    if (s >= lo && s <= hi) {
      const t = hi === lo ? 0 : (s - lo) / (hi - lo);
      return lerpColor(cLo, cHi, t);
    }
  }
  return COLORS.red;
}

/**
 * Calcule les données pour les stripes mensuelles.
 *
 * @param {Object[]} fiches — toutes les fiches hors calibration
 * @returns {{ month: string, score: number|null, hasData: boolean, color: string }[]}
 *   Tableau trié chronologiquement du premier au dernier mois avec données,
 *   plus les mois intermédiaires sans données.
 */
export function computeStripes(fiches) {
  // Grouper par mois
  const byMonth = {};
  for (const fiche of fiches) {
    const d = ficheDate(fiche);
    if (!d) continue;
    const scoreL = fiche?.scoring?.score_L?.score;
    if (typeof scoreL !== "number") continue;
    const key = toMonthKey(d);
    if (!byMonth[key]) byMonth[key] = [];
    byMonth[key].push(scoreL);
  }

  if (Object.keys(byMonth).length === 0) return [];

  // Déterminer la plage de mois
  const keys = Object.keys(byMonth).sort();
  const first = keys[0];
  const last = keys[keys.length - 1];

  // Générer tous les mois entre first et last inclus
  const result = [];
  let cur = new Date(`${first}-01`);
  const endDate = new Date(`${last}-01`);

  while (cur <= endDate) {
    const key = toMonthKey(cur);
    const scores = byMonth[key];
    let score = null;
    let hasData = false;

    if (scores && scores.length > 0) {
      score = Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 100) / 100;
      hasData = true;
    }

    result.push({
      month: key,
      score,
      hasData,
      color: hasData ? scoreLToColor(score) : COLORS.noData,
    });

    cur.setMonth(cur.getMonth() + 1);
  }

  return result;
}

// ---------------------------------------------------------------------------
// Indicateur 2 — Vecteur de progression
// ---------------------------------------------------------------------------

/**
 * Retourne la couleur de la flèche selon la force et les deltas.
 */
function vectorColor(force, deltaInst, deltaRhet) {
  if (deltaRhet < 0 && deltaInst < 0) return COLORS.tealDark;
  if (force < 0.15) return COLORS.amber;
  if (force < 0.35) return COLORS.coral;
  return COLORS.coralDark;
}

/**
 * Calcule les données pour le vecteur de progression.
 *
 * @param {Object[]} fiches — toutes les fiches hors calibration
 * @returns {{
 *   deltaInst: number,
 *   deltaRhet: number,
 *   force: number,
 *   nActive: number,
 *   color: string,
 *   hasCurrent: boolean,
 *   hasPrevious: boolean
 * }}
 */
export function computeVector(fiches) {
  const now = new Date();
  const t0 = subtractMonths(now, 3);
  const t1 = subtractMonths(now, 6);

  const current = fichesInRange(fiches, t0, now);
  const previous = fichesInRange(fiches, t1, t0);

  const scoreInstCurr = avgCriteres(current, CRITERES_INST);
  const scoreRhetCurr = avgCriteres(current, CRITERES_RHET);
  const scoreInstPrev = avgCriteres(previous, CRITERES_INST);
  const scoreRhetPrev = avgCriteres(previous, CRITERES_RHET);

  const hasCurrent = scoreInstCurr !== null || scoreRhetCurr !== null;
  const hasPrevious = scoreInstPrev !== null || scoreRhetPrev !== null;

  const deltaInst = (scoreInstCurr ?? 0) - (scoreInstPrev ?? 0);
  const deltaRhet = (scoreRhetCurr ?? 0) - (scoreRhetPrev ?? 0);
  const force = Math.sqrt(deltaInst ** 2 + deltaRhet ** 2);

  // Nombre de critères C activés dans la fenêtre courante
  let nActive = 0;
  const allC = [...CRITERES_INST, ...CRITERES_RHET];
  for (const fiche of current) {
    for (const id of allC) {
      const s = getCritereScore(fiche, id, true);
      if (s !== null && s > 0) {
        nActive++;
        break; // compter une fois par fiche par critère — on compte les critères uniques ci-dessous
      }
    }
  }
  // Recalcul correct : nb de critères distincts avec au moins une activation dans la fenêtre
  nActive = 0;
  for (const id of allC) {
    const hasActivation = current.some((f) => {
      const s = getCritereScore(f, id, true);
      return s !== null && s > 0;
    });
    if (hasActivation) nActive++;
  }

  return {
    deltaInst,
    deltaRhet,
    force,
    nActive,
    color: vectorColor(force, deltaInst, deltaRhet),
    hasCurrent,
    hasPrevious,
    angle: Math.atan2(deltaInst, deltaRhet), // radians
  };
}

// ---------------------------------------------------------------------------
// Indicateur 3 — Barres critères C
// ---------------------------------------------------------------------------

/**
 * Calcule les taux d'activation pour chaque critère C sur deux fenêtres de 6 mois.
 *
 * @param {Object[]} fiches
 * @returns {{
 *   id: string,
 *   curr: number|null,
 *   prev: number|null,
 *   delta: number|null,
 *   color: string,
 *   insuffisant: boolean
 * }[]}
 */
export function computeCriteres(fiches) {
  const now = new Date();
  const t0 = subtractMonths(now, 6);
  const t1 = subtractMonths(now, 12);

  const current = fichesInRange(fiches, t0, now);
  const previous = fichesInRange(fiches, t1, t0);

  const insufficientCurr = current.length < 3;
  const insufficientPrev = previous.length < 3;

  return CRITERES_C.map((id) => {
    const calc = (fichesList, insufficient) => {
      if (insufficient) return null;
      const applicable = fichesList.filter((f) => {
        const c = f?.scoring?.criteres?.find((x) => x.id === id);
        return c && c.applicable !== false;
      });
      if (applicable.length === 0) return null;
      const activated = applicable.filter((f) => {
        const c = f.scoring.criteres.find((x) => x.id === id);
        return c.score > 0;
      });
      return activated.length / applicable.length;
    };

    const curr = calc(current, insufficientCurr);
    const prev = calc(previous, insufficientPrev);
    const delta = curr !== null && prev !== null ? curr - prev : null;

    let color = COLORS.grey;
    if (delta !== null) {
      if (delta > 0.08) color = COLORS.coral;
      else if (delta < -0.08) color = COLORS.tealDark;
    }

    return {
      id,
      curr,
      prev,
      delta,
      color,
      insuffisant: insufficientCurr,
    };
  });
}

// ---------------------------------------------------------------------------
// Métriques synthétiques (cards)
// ---------------------------------------------------------------------------

/**
 * Calcule les métriques résumées sur les 3 derniers mois.
 *
 * @param {Object[]} fiches
 * @returns {{
 *   avgL: number|null,
 *   avgC: number|null,
 *   signal: string,
 *   signalSub: string,
 *   signalColor: string,
 *   nFiches: number
 * }}
 */
export function computeMetrics(fiches) {
  const now = new Date();
  const t0 = subtractMonths(now, 3);
  const recent = fichesInRange(fiches, t0, now);

  // Score L moyen
  const lScores = recent
    .map((f) => f?.scoring?.score_L?.score)
    .filter((s) => typeof s === "number");
  const avgL = lScores.length > 0 ? lScores.reduce((a, b) => a + b, 0) / lScores.length : null;

  // Score C moyen
  const cScores = recent
    .map((f) => f?.scoring?.score_C?.score)
    .filter((s) => typeof s === "number");
  const avgC = cScores.length > 0 ? cScores.reduce((a, b) => a + b, 0) / cScores.length : null;

  // Signal période
  let signal = "Vert";
  let signalSub = "Aucun signal détecté";
  let signalColor = COLORS.tealDark;

  if (avgL !== null) {
    if (avgL < 0.20) {
      signal = "Vert"; signalSub = "Aucun signal détecté"; signalColor = COLORS.tealDark;
    } else if (avgL < 0.35) {
      signal = "Ambre"; signalSub = "Signaux à surveiller"; signalColor = COLORS.amber;
    } else if (avgL < 0.55) {
      signal = "Orange"; signalSub = "Signaux préoccupants"; signalColor = COLORS.coral;
    } else {
      signal = "Rouge"; signalSub = "Signaux critiques"; signalColor = COLORS.coralDark;
    }
  }

  return {
    avgL,
    avgC,
    signal,
    signalSub,
    signalColor,
    nFiches: recent.length,
  };
}

// ---------------------------------------------------------------------------
// Export principal
// ---------------------------------------------------------------------------

/**
 * Point d'entrée unique du helper.
 *
 * @param {Object[]} fiches — tableau de fiches JSON (hors calibration)
 * @returns {{
 *   stripes: ReturnType<computeStripes>,
 *   vector: ReturnType<computeVector>,
 *   criteres: ReturnType<computeCriteres>,
 *   metrics: ReturnType<computeMetrics>
 * }}
 */
export function computeDashboard(fiches) {
  return {
    stripes: computeStripes(fiches),
    vector: computeVector(fiches),
    criteres: computeCriteres(fiches),
    metrics: computeMetrics(fiches),
  };
}
