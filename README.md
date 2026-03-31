# La Bascule — Observatoire démocratique

[![CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-sa/4.0/)
[![MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-CODE)

**Projet citoyen indépendant** — Luc Schmitt

Observatoire de similitudes structurelles entre les mécanismes politiques
contemporains français et les séquences historiques de bascule vers des
régimes autoritaires.

> Ce projet documente des **similitudes de mécanismes**, non une équivalence
> de nature. La France contemporaine est en phase 3 — pas en 1933.

---

## Résultats de calibration

| Texte | Bord | Score | Signal |
|-------|------|-------|--------|
| Décret du Reichstag 28 fév. 1933 | Nazisme | 100% | 🔴 Critique |
| Lois fascistissimes 1926 | Fascisme | 100% | 🔴 Critique |
| Ordonnance travail 2017 | Centre-gauche | 7% | 🟢 Aucun |
| Loi immigration jan. 2024 | Centre-droit + RN | 44–50% | 🟠 Modéré |
| PPL Yadan antisémitisme 2024 | Transpartisan | 8% | 🟡 Faible |
| Programme NFP juin 2024 | Gauche radicale | 12.5% | 🟡 Faible |

---

## Architecture

```
labascule/
├── pipeline/               # Pipeline 4 agents IA
│   ├── agent1_extract.py   # Extraction + web_search (Sonnet)
│   ├── agent2_favorable.py # Arguments pro (Haiku)
│   ├── agent3_defavorable.py # Arguments contre (Haiku)
│   ├── agent4_scoring.py   # Scoring aveugle (Sonnet)
│   ├── orchestrator.py
│   ├── legifrance_fetcher.py
│   └── utils.py
├── run_pipeline.py
├── lb.py                   # Raccourcis Docker CLI
├── Dockerfile
├── docker-compose.yml
├── site/                   # Site Astro (frise + baromètre)
├── fiches/                 # Analyses JSON
└── methode-labascule.md    # Méthode complète
```

---

## Lancer le pipeline

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...

python lb.py build
python lb.py run --url https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049040245
```

## Lancer le site

```bash
cd site
docker compose build && docker compose up
# → http://localhost:4321
```

---

## Méthode

Grille de 17 critères opérationnels — Paxton (2004), Gramsci, Chapoutot (2025).
Voir [`methode-labascule.md`](methode-labascule.md).

**4 principes éthiques :**
1. Symétrie partisane — analyse symétrique sous 30 jours
2. Bénéfice du doute — en cas d'incertitude, réponse Non
3. Similitude de mécanisme — jamais de qualification fasciste d'un acteur
4. Scoring aveugle au parti

---

## Licences

- Contenu : [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)
- Code : MIT

*Luc Schmitt — projet citoyen indépendant — 2026*
