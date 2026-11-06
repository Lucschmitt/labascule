# Observatoire du gouvernement — méthode d'analyse des prises de parole

**Version 0.1.0 — brouillon à discuter.** Complète la méthode La Bascule (`methode-labascule-v0.2.2.md`), dont elle
reprend les principes : extraction factuelle d'abord, symétrie, « en cas de doute : non », validation humaine avant
publication.

## 1. Objet

Rendre comparable ce que disent les membres du gouvernement : sur quels sujets, avec quelles positions, quels mots,
quels engagements chiffrés, quels procédés — pour pouvoir croiser ensuite par ministre, ministère, parti, thème,
période et source, et suivre l'apparition et la diffusion de nouveaux concepts.

L'observatoire **décrit et compte** ; il ne juge pas les personnes. Aucune étiquette idéologique n'est attribuée à un
orateur. Les signaux (procédés, critères La Bascule, affirmations à vérifier) sont des **pistes à examiner**, toujours
accompagnés du verbatim qui les fonde.

## 2. Corpus

Prises de parole publiques **tenues en fonction** par les membres du gouvernement en exercice (35 au 6 novembre 2026),
depuis le début de la XVIIe législature (18 juillet 2024), y compris celles tenues avant leur entrée au gouvernement
(la qualité au moment des propos est conservée) :

| Source | Contenu | Texte |
|---|---|---|
| Assemblée — comptes rendus de séance | interventions en séance, rattachées à l'orateur par identifiant | intégral |
| Assemblée — questions au gouvernement | réponses orales, avec le groupe de l'auteur de la question | intégral |
| Assemblée — questions écrites | réponses écrites publiées au JO au nom du ministère | intégral |
| DILA — discours publics | discours, déclarations, entretiens (vie-publique.fr) | métadonnées seulement |

Limites : le texte intégral des discours n'est pas publié en open data (le site vie-publique est protégé contre les
robots, ce que l'on ne contourne pas) ; le Sénat et le Parlement européen viendront ensuite ; les réseaux sociaux ne
sont pas couverts (API X payante), Bluesky pourra l'être.

## 3. Unité d'analyse : l'affirmation

Chaque prise de parole est découpée en **affirmations** : une idée, une position ou une annonce portant sur un objet.
Pour chacune :

| Champ | Contenu | Référentiel |
|---|---|---|
| `verbatim` | extrait **exact** de la prise de parole (≤ 300 caractères) | vérifié automatiquement mot pour mot |
| `resume` | reformulation neutre en une phrase | — |
| `theme` | thème majeur et sous-thème | CAP (21 thèmes, 213 sous-thèmes) |
| `tags` | mots-clés libres normalisés (objets précis : « narcotrafic », « budget 2027 »…) | libre, consolidé chaque semaine |
| `entites` | personnes, organisations, textes juridiques, lieux nommés | — |
| `acte` | annonce, engagement, bilan, diagnostic, justification, réfutation, mise en cause, appel, avis procédural, hommage | `codebook.types_acte` |
| `position` | objet nommé + sens (soutient, s'oppose, nuance, sagesse) + référence (n° d'amendement, texte) | si explicite |
| `cadrage` | principal (+ secondaire) | Policy Frames Codebook (14 cadres) + souveraineté |
| `chiffres` | valeur, unité, objet, échéance, source citée | — |
| `verifiable` | affirmation factuelle vérifiable ? type (chiffre, fait, comparaison, causalité, prévision) | statut « non vérifié » |
| `procedes` | procédés rhétoriques repérés dans le verbatim, avec explication | `codebook.procedes` (14) |
| `bascule` | signaux des critères La Bascule observables dans un discours | C-01, C-02, C-09c, C-10, C-13, C-15, C-17, C-18, C-19 |
| `lexique` | termes du lexique présents, et **usage** : emploi assumé, mention critique, citation d'un tiers | `lexique-v0.1.json` |

Le lien au ministre, à son ministère, à son parti et à la source est porté par la prise de parole.

## 4. Chaîne d'analyse

1. **Découpage et extraction** (IA locale 7B) : affirmations, verbatim, résumé, acte, position, chiffres, entités, tags.
2. **Thèmes CAP** en deux temps (IA locale) : thème majeur, puis sous-thème parmi ceux de ce thème seulement.
3. **Cadrage, procédés, signaux La Bascule** (IA locale, consignes prudentes : en cas de doute, rien).
4. **Contrôles déterministes** : chaque verbatim doit figurer mot pour mot dans le texte source (sinon l'affirmation est
   rejetée) ; codes hors référentiel rejetés ; termes du lexique détectés par motif exact.
5. **Vérification des faits** (étape séparée, plus tard) : seulement les affirmations vérifiables jugées importantes ;
   un modèle fort cherche une source officielle ; statut « confirmé / inexact selon [source] / trompeur selon [source] /
   invérifiable » ; **relecture humaine obligatoire** avant publication. Le mot « mensonge » n'est jamais employé.
6. **Liens et croisements** : proximité entre ministres par thème (affirmations comparées par similarité de sens),
   cohérence dans le temps (changement de position sur un même objet signalé « à vérifier »), diffusion d'un terme
   (qui l'emploie le premier, qui le reprend).

## 5. Nouveaux concepts

- Chaque semaine : expressions dont la fréquence augmente nettement (fenêtre de 12 semaines) + tags nouveaux.
- Claude examine, recherche l'origine des candidats pertinents et propose une entrée **sourcée** au lexique ; Luc valide.
- Le lexique décrit des termes, avec leur origine documentée, jamais des personnes ; il doit rester **équilibré** entre
  bords politiques (règle de symétrie). État v0.1 : 7 termes associés à la droite ou à l'extrême droite, 3 à la gauche,
  2 au camp présidentiel — **à rééquilibrer avant toute publication**.

## 6. Qualité : examen, leçons, fine-tuning

- **Échantillon de 200 prises de parole**, stratifié : par source (séance, QAG, questions écrites), par membre du
  gouvernement, par longueur, et en surreprésentant les textes contenant un terme du lexique.
- **Référence (« or »)** : un modèle fort (Claude) annote les 200 avec la même consigne détaillée ; Claude audite
  ensuite les désaccords avec l'IA locale et tranche ; Luc relit un sous-échantillon de 20.
- **Mesures** par champ : validité des verbatim (doit être 100 %), accord sur le thème majeur et le sous-thème, sur
  l'acte, la position, le cadrage ; faux positifs sur procédés et signaux (doivent rester rares) ; rappel des chiffres.
- **Seuils v0.1** avant analyse du corpus entier : verbatim 100 %, thème majeur ≥ 85 %, sous-thème ≥ 65 %,
  acte ≥ 75 %, faux positifs procédés/signaux ≤ 5 %.
- **Leçons** : chaque erreur récurrente devient une leçon du carnet de stage, testée à l'examen avant activation ; les
  cas d'examen sont tirés de l'échantillon.
- **Fine-tuning** : les annotations de référence validées forment le jeu d'entraînement (JSONL) d'un modèle local
  spécialisé ; il n'est adopté que s'il fait mieux que le modèle actuel à l'examen.

## 7. Neutralité, droit, publication

- Seuls des propos publics tenus en fonction ; aucune personne privée (les auteurs de questions sont des députés,
  identifiés par leur groupe).
- Toute donnée affichée renvoie à sa source officielle ; les codes produits par une IA sont signalés comme tels.
- Mêmes règles et mêmes seuils pour tous les orateurs ; les signaux sont publiés avec leur verbatim et la règle appliquée.
- Les opinions politiques relèvent des données sensibles (RGPD, art. 9) : le traitement porte sur des propos rendus
  publics par des élus dans l'exercice de leurs fonctions ; la base légale et les mentions d'information sont à faire
  valider (avis juridique conseillé avant publication).

## 8. Versions

| Version | Date | Changements |
|---|---|---|
| 0.1.0 | 2026-11-06 | Première version : unité « affirmation », CAP, Policy Frames, procédés, lexique v0.1, protocole qualité. |
