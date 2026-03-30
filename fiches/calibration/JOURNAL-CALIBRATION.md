# Journal de calibration — La Bascule

**Version grille testée** : 0.1.0-draft  
**Date** : 2026-03-30  
**Méthode** : simulation manuelle (pipeline réel à venir)

---

## Principe

Ce journal enregistre les fiches de calibration utilisées pour valider
la grille de critères. Chaque fiche de calibration est un texte historique
ou contemporain dont le score attendu est connu a priori.

**Règle de non-régression** : si le pipeline produit un score s'écartant
de plus de 15 points du score attendu sur une fiche de calibration,
la grille ou les prompts sont considérés défectueux.

---

## Fiches de calibration haute (score attendu > 80%)

| ID | Texte | Date | Score attendu | Score obtenu | Critères applicables | Statut |
|----|-------|------|---------------|--------------|----------------------|--------|
| CAL-DE-1933-001 | Décret du Reichstag (28 fév. 1933) | 1933-02-28 | 100% | 100% | 6 | ✅ Validé |
| CAL-IT-1926-001 | Lois fascistissimes italiennes | 1925-12/1926-11 | 100% | 100% | 8 | ✅ Validé |

## Fiches de calibration basse (score attendu < 20%)

| ID | Texte | Date | Score attendu | Score obtenu | Critères applicables | Statut |
|----|-------|------|---------------|--------------|----------------------|--------|
| CAL-FR-2017-001 | Ordonnance travail CSE | 2017-09-22 | < 15% | 7% | 7 | ✅ Validé |

---

## Observations issues des tests

### Observation 1 — Couverture variable selon le type de texte
Les décrets d'urgence et les lois de dissolution activent principalement
C-01, C-02, C-13, C-15, C-16, C-17. Les critères C-03 à C-12 (milices,
financement, ralliements) ne sont pas activables sur des textes législatifs
isolés — ils évaluent des phénomènes contextuels. Conséquence : le score
global est toujours relatif au nombre de critères applicables, jamais
absolu sur 17.

### Observation 2 — C-13 est le critère le plus sensible
C-13 (mesures d'exception répétées) a produit un score "partiel" (0.5)
sur l'ordonnance travail 2017, alors que le score attendu était 0.
La condition (a) est satisfaite — c'est une ordonnance. Mais la condition (b)
(usage récurrent sur 12 mois) n'est pas satisfaite isolément.
Conclusion : C-13 ne doit jamais être évalué sur un texte isolé — il
requiert une analyse du contexte d'ensemble (nombre d'ordonnances sur 12 mois).
**Action : ajouter cette précision dans la définition de C-13 (version 0.1.2).**

### Observation 3 — C-14 résiste correctement à la tentation du faux positif
L'ordonnance travail 2017 a été critiquée par la CGT comme une attaque
contre les syndicats. La grille score C-14 à 0 car aucune des 3 conditions
opérationnelles n'est satisfaite : ni réduction de financement >20%,
ni syndicats-maison, ni restriction du droit de grève. Ce résultat valide
la robustesse des définitions opérationnelles : le critère distingue
"réforme contestée" de "destruction des syndicats".

### Observation 4 — C-03 jamais activé sur textes législatifs
Les milices (C-03) n'apparaissent jamais comme applicables à un texte
législatif isolé — même les lois fascistissimes ne créent pas les milices,
elles les préexistent. C-03 doit être évalué en tant que critère contextuel
(état de fait au moment de l'analyse), pas en tant que critère lié à un
texte spécifique.
**Action : clarifier dans le protocole que C-03 est un critère contextuel
permanent, mis à jour séparément des fiches législatives (version 0.1.2).**

---

## Prochaines fiches de calibration à produire

| Priorité | Type | Texte envisagé | Score attendu |
|----------|------|----------------|---------------|
| 1 | Haute complémentaire | Loi d'habilitation allemande du 23 mars 1933 | ~100% |
| 2 | Basse complémentaire | Loi française sur la transition énergétique (2015) | < 10% |
| 3 | Intermédiaire | Loi immigration française de janvier 2024 | 30-50% (à déterminer) |

La fiche de calibration intermédiaire (score 30-50%) est la plus utile
pour valider la gradation de la grille. Elle constitue aussi la première
fiche contemporaine réelle du baromètre.

---

*Journal de calibration v0.1.0 — à mettre à jour à chaque test du pipeline réel.*
