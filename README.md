# La Bascule

[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]
[![Status](https://img.shields.io/badge/status-projet%20citoyen%20indépendant-blue)]()
[![Method](https://img.shields.io/badge/method-v0.1.0--draft-blue)]()

> Méthode open source de détection de signaux de bascule démocratique.  
> Grille historique comparative (Paxton, Gramsci, Chapoutot) × analyse IA × baromètre législatif français.

---

## Ce que c'est

**La Bascule** est un projet de recherche citoyenne qui documente les similitudes
structurelles entre des mécanismes politiques contemporains en France et les
séquences historiques conduisant à des régimes autoritaires (Italie fasciste
1919-1926, Allemagne nazie 1919-1934).

Ce n'est pas un projet militant. C'est une méthode.

Le projet repose sur trois composantes :

1. **Une frise historique comparative** — Italie, Allemagne, France en parallèle,
   organisée par points de bascule (financement des milices, ralliement du
   centre-droit, isolement de l'extrême gauche, destruction des syndicats…)

2. **Une grille de 17 critères** — fondée sur la bibliographie académique
   (Paxton, Gramsci, Gentile, Chapoutot, Tasca), formulée en questions binaires
   applicables à des textes législatifs contemporains

3. **Un baromètre législatif** — chaque texte de loi, décret ou amendement
   significatif est analysé avec la grille, de manière symétrique quel que soit
   le bord politique de son auteur

---

## Pourquoi ce projet

Les régimes fascistes historiques ne se sont pas installés par coup d'État.
Ils se sont installés progressivement, légalement, avec le consentement actif
ou passif des partis modérés — pendant que les contemporains débattaient pour
savoir si la comparaison était légitime.

Ce projet part d'une conviction méthodologique simple : **documenter les
mécanismes avant qu'ils ne soient irréversibles** est plus utile que de
les nommer une fois qu'ils ont produit leurs effets.

La méthode est assumée non-neutre sur un seul point : elle considère que
la démocratie libérale, ses contre-pouvoirs et ses libertés fondamentales
sont des biens à protéger. Elle est en revanche strictement symétrique sur
le plan partisan — aucun parti n'est exempté de la grille.

---

## Structure du dépôt

```
labascule/
├── methode-labascule.md     # Source de vérité — méthode complète versionnée
├── README.md                # Ce fichier
├── .gitignore
│
├── fiches/                  # Analyses du baromètre (à venir)
│   └── ...
│
├── prompts/                 # Prompts système pour l'agent IA (à venir)
│   └── ...
│
└── site/                    # Code source du site web (à venir)
    └── ...
```

---

## État d'avancement

| Composante | Statut |
|-----------|--------|
| Section 1 — Préambule épistémique | ✅ Rédigée |
| Section 2 — Bibliographie opérationnelle | ✅ Rédigée |
| Section 3 — Grille de 17 critères (C-01 à C-17) | ✅ Rédigée |
| Section 4 — Protocole d'application | 🔄 En cours |
| Section 5 — Journal des versions | 🔄 En cours |
| Prompt système agent IA | ⬜ À faire |
| Fiches baromètre pilotes (x5) | ⬜ À faire |
| Site web (2 pages) | ⬜ À faire |

---

## Contribuer

Le projet est en phase de construction. Les contributions sont les bienvenues
sous deux formes :

**Relecture critique de la méthode** — historiens, juristes, politologues :
ouvrez une issue avec le label `méthode` pour signaler une erreur, un manque
ou un désaccord argumenté.

**Validation de fiches** — pour chaque analyse du baromètre, des relecteurs
externes peuvent valider ou contester via les Pull Requests. Leur contribution
apparaît séparément, identifiée, sous leur propre responsabilité.

Ce que je ne cherche pas : des contributeurs qui partagent mes convictions
politiques. Ce que je cherche : des contributeurs qui partagent ma rigueur
méthodologique.

---

## Références clés

- Paxton, Robert O. *The Anatomy of Fascism*. Knopf, 2004.
- Gramsci, Antonio. *Socialisme et fascisme. L'Ordine Nuovo 1921-1922*. Éd. sociales, 1978.
- Chapoutot, Johann. *Les Irresponsables*. Gallimard, 2025.
- Chapoutot, Johann. *Fascisme, nazisme et régimes autoritaires en Europe*. PUF, 2013.
- Tasca, Angelo. *Naissance du fascisme*. Gallimard, 1938 (rééd. 1995).
- Evans, Richard J. *The Coming of the Third Reich*. Penguin, 2003.

Bibliographie complète → [`methode-labascule.md`](./methode-labascule.md#section-2--bibliographie-opérationnelle)

---

## Auteur

**Luc Schmitt** — projet citoyen indépendant  
GitHub : [@lucschmitt](https://github.com/lucschmitt)

---

## Licence

[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

Ce projet est publié sous licence
[Creative Commons Attribution-ShareAlike 4.0 International][cc-by-sa].

Vous pouvez réutiliser, adapter et redistribuer ce travail à condition de
citer la source et de publier toute œuvre dérivée sous la même licence.

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
