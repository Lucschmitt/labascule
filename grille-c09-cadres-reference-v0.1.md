# Grille de référence — Cadres caractéristiques de l'extrême droite
## Artefact C-09 · Version 0.1 · DRAFT — non validé empiriquement

**Statut :** Ébauche structurelle. Les cadres listés ci-dessous sont construits
à partir des catégories du Manifesto Project [CMP20] et de la connaissance
des programmes RN/FN 2007-2024. Ils doivent être validés empiriquement par
une session de codage dédiée avant mise en production.

**Usage :** Cet artefact est la référence exclusive pour la sous-condition (c1)
de C-09. Un Agent 4 ne peut déclencher (c1) que sur un cadre figurant dans
cette liste. Il ne peut pas inférer de nouveaux cadres de lui-même.

**Versionnement :** mis à jour à chaque version mineure de `methode-labascule.md`.
Version de ce fichier synchronisée avec la version de la grille.

**Référentiel source :** Manifesto Project codebook v5 [CMP20],
catégories 601, 605, 607.1, 608, 608.1, 608.2.

---

## Structure d'un cadre caractéristique

Chaque cadre est défini par trois éléments obligatoires :

| Élément | Description |
|---------|-------------|
| **Thème** | Domaine politique concerné |
| **Désignation** | Groupe désigné comme responsable du problème |
| **Solution différenciatrice** | Mesure impliquant une différenciation de droits selon l'origine, la nationalité ou le statut |
| **Catégories CMP** | Codes Manifesto Project correspondants |
| **Contre-indicateur** | Traitement du même thème qui NE déclenche PAS (c1) |

---

## Cadres de référence v0.1

### CF-01 — Préférence nationale sur les droits sociaux

| Élément | Contenu |
|---------|---------|
| **Thème** | Protection sociale, aides au logement, allocations familiales, RSA |
| **Désignation** | Les étrangers (immigrés, non-nationaux) désignés comme bénéficiaires illégitimes des prestations sociales |
| **Solution différenciatrice** | Condition de nationalité française ou d'ancienneté de résidence (ex. 5 ans) pour accéder aux prestations |
| **Catégories CMP** | 504 (Welfare State expansion — négatif) + 608.1 (traitement des immigrés présents — négatif) |
| **Contre-indicateur** | Réforme des conditions de ressources sans critère de nationalité ; universalisation des droits |

---

### CF-02 — Ethnicisation de la criminalité / insécurité

| Élément | Contenu |
|---------|---------|
| **Thème** | Sécurité intérieure, délinquance, criminalité |
| **Désignation** | Un groupe ethnonational ou religieux désigné comme responsable prioritaire de l'insécurité |
| **Solution différenciatrice** | Mesures d'expulsion, de contrôle ou de restriction ciblant ce groupe ; double peine ; déchéance de nationalité |
| **Catégories CMP** | 109 (Law & Order — positif) + 601 (Nationalisme positif) + 608.1 |
| **Contre-indicateur** | Réforme policière sans désignation de groupe ; renforcement des effectifs sans critère ethnique ou national |

---

### CF-03 — Assimilation obligatoire comme condition de résidence

| Élément | Contenu |
|---------|---------|
| **Thème** | Intégration, immigration, laïcité |
| **Désignation** | Les immigrés désignés comme refusant de s'intégrer ou menaçant les valeurs nationales |
| **Solution différenciatrice** | Condition culturelle ou comportementale (maîtrise de la langue, adhésion explicite aux « valeurs républicaines ») comme condition de renouvellement de titre de séjour ou de naturalisation, avec contrôle différencié selon l'origine |
| **Catégories CMP** | 608.2 (intégration culturelle forcée) + 605 (valeurs morales traditionnelles) |
| **Contre-indicateur** | Offre de cours de langue ou de formation civique universelle et non contraignante |

---

### CF-04 — Préférence nationale à l'emploi

| Élément | Contenu |
|---------|---------|
| **Thème** | Emploi, chômage, accès à la fonction publique |
| **Désignation** | Les étrangers désignés comme concurrents déloyaux sur le marché du travail ou comme bénéficiaires illégitimes des emplois publics |
| **Solution différenciatrice** | Réservation explicite de postes ou d'avantages aux nationaux ; restriction de l'accès à la fonction publique selon la nationalité au-delà des obligations constitutionnelles existantes |
| **Catégories CMP** | 505 (Limitation of Welfare State) + 608.1 |
| **Contre-indicateur** | Mesures anti-discrimination à l'embauche ; ouverture de la fonction publique |

---

### CF-05 — Identité nationale exclusive comme critère d'appartenance civique

| Élément | Contenu |
|---------|---------|
| **Thème** | Nationalité, citoyenneté, identité nationale |
| **Désignation** | Un groupe (immigrés de première ou deuxième génération, bi-nationaux) désigné comme appartenant insuffisamment à la nation |
| **Solution différenciatrice** | Réforme du droit du sol ou du sang différenciant les citoyens selon l'origine ; déchéance de nationalité pour bi-nationaux ; création d'une citoyenneté de second rang |
| **Catégories CMP** | 601 (Nationalisme positif) + 608 (Immigration négative) |
| **Contre-indicateur** | Réforme de la nationalité pour simplification administrative sans critère d'origine ; extension du droit de vote |

---

## Note sur le seuil d'applicabilité

Un texte déclenche (c1) s'il correspond à l'un des cadres CF-01 à CF-05 **dans
sa combinaison complète** (thème + désignation + solution différenciatrice).
La présence du thème seul (ex. sécurité sans désignation de groupe) ne suffit
pas. La présence de la désignation sans solution différenciatrice ne suffit
pas non plus.

L'Agent 4 doit vérifier les trois éléments simultanément avant de conclure à
la présence d'un cadre caractéristique.

---

## À faire avant mise en production (v0.2)

- [ ] Validation empirique des cadres CF-01 à CF-05 par codage manuel de 10
  fiches RN/FN (2007, 2012, 2017, 2022, 2024) selon les catégories CMP
- [ ] Ajout de contre-exemples empiriques pour chaque cadre (textes de gauche
  traitant les mêmes thèmes sans cadre différenciateur)
- [ ] Vérification de la non-applicabilité à des textes PS/EELV pour les 5 cadres
- [ ] Calibration de l'Agent 4 sur les 5 cadres avec des fiches test

---

*Artefact v0.1 — draft — à ne pas utiliser en production avant validation empirique.*
*Synchronisé avec methode-labascule.md v0.2.1-draft.*
