# Spécification technique — Pipeline multi-agents La Bascule

**Version** : 0.1.0-draft  
**Date** : 2026-03-30  
**Dépend de** : methode-labascule.md v0.1.0-draft

---

## 1. Schéma JSON — structure de données inter-agents

Ce schéma est le contrat entre tous les agents. L'Agent 1 le produit en
totalité. Les Agents 2 et 3 le reçoivent en lecture seule et y ajoutent
leurs sections. L'Agent 4 le reçoit complet et y ajoute le scoring.
La validation humaine complète les champs `validation`.

```jsonc
{
  // ── MÉTADONNÉES FICHE ──────────────────────────────────────────
  "fiche_id": "FR-2024-LOI-001",           // identifiant unique
  "schema_version": "0.1.0",               // version du schéma
  "grille_version": "0.1.0-draft",         // version methode-labascule.md
  "modele_ia": "claude-sonnet-4-6",        // modèle utilisé
  "date_analyse": "2026-03-30T14:22:00Z",  // ISO 8601
  "statut": "draft",                       // draft | validated | published | archived
  "analyse_symetrique_prevue": "2026-04-29", // J+30 ou null

  // ── EXTRACTION FACTUELLE (Agent 1) ────────────────────────────
  "source": {
    "type": "loi",                         // loi | decret | ordonnance | amendement
                                           // | declaration | programme | deliberation
    "reference": "LOI n° 2024-42 du 26 janvier 2024",
    "url_source": "https://www.legifrance.gouv.fr/...",
    "url_archive": "https://archive.org/...", // copie archivée obligatoire
    "date_publication": "2024-01-26",
    "date_vote": "2024-01-19",
    "institution": "Assemblée nationale"
  },

  "auteurs": [
    {
      "nom": "Gérald Darmanin",
      "fonction": "Ministre de l'Intérieur",
      "parti": "Renaissance",
      "mandat": "Gouvernement Attal"
    }
  ],

  "vote": {
    "pour": 349,
    "contre": 186,
    "abstentions": 29,
    "groupes_pour": ["Renaissance", "Horizons", "MoDem", "LR", "RN"],
    "groupes_contre": ["LFI-NFP", "PS-NFP", "PCF", "Écologistes"],
    "groupes_abstentions": [],
    "url_scrutin": "https://data.assemblee-nationale.fr/..."
  },

  "texte_extrait": {
    "extrait_pertinent": "...",            // extrait ciblé sur les critères potentiels
    "url_texte_integral": "...",
    "archive_locale": "fiches/sources/FR-2024-LOI-001.txt"
  },

  "contexte_procedural": {
    "commission": "Commission des lois",
    "lectures": 3,
    "conseil_constitutionnel": true,
    "decision_cc": "Décision n° 2024-863 DC du 25 janvier 2024",
    "articles_censures": ["article 7", "article 32"]
  },

  // Sources modifiables — copies archivées au moment de l'analyse
  "sources_archivees": [
    {
      "type": "tweet",
      "auteur": "GDarmanin",
      "url_original": "https://x.com/...",
      "url_archive": "fiches/archives/FR-2024-LOI-001-tweet-darmanin.html",
      "date_capture": "2026-03-30T14:00:00Z",
      "contenu": "..."
    }
  ],

  // ── ARGUMENTS FAVORABLES (Agent 2 — contexte isolé) ──────────
  "arguments_favorables": {
    "agent_run_id": "run_abc123",          // identifiant de l'appel API
    "timestamp": "2026-03-30T14:25:00Z",
    "arguments": [
      {
        "id": "ARG-FAV-001",
        "titre": "Renforcement de la maîtrise des flux migratoires",
        "corps": "...",
        "sources_citees": ["Eurostat 2023", "rapport Sénat 2022"]
      }
    ],
    "note_interne": null                   // commentaire du validateur humain
  },

  // ── ARGUMENTS DÉFAVORABLES (Agent 3 — contexte isolé) ────────
  "arguments_defavorables": {
    "agent_run_id": "run_def456",          // run_id différent — appel séparé
    "timestamp": "2026-03-30T14:28:00Z",
    "arguments": [
      {
        "id": "ARG-DEF-001",
        "titre": "Atteinte au droit d'asile constitutionnellement garanti",
        "corps": "...",
        "sources_citees": ["Conseil constitutionnel 2024", "CNCDH 2024"]
      }
    ],
    "note_interne": null
  },

  // ── SCORING (Agent 4 — reçoit les deux sans avoir vu leur production)
  "scoring": {
    "agent_run_id": "run_ghi789",
    "timestamp": "2026-03-30T14:35:00Z",
    "criteres": [
      {
        "id": "C-01",
        "libelle": "Discours de déclin et victimisation nationale",
        "applicable": true,
        "reponse": "oui",                  // oui | non | partiel
        "score": 1.0,                      // 0 | 0.5 | 1
        "justification": "Le texte s'inscrit explicitement dans un discours...",
        "source_historique_citee": "PAX04"
      },
      {
        "id": "C-02",
        "libelle": "Culte de l'unité / ennemi intérieur",
        "applicable": true,
        "reponse": "partiel",
        "score": 0.5,
        "justification": "La condition (a) est satisfaite mais la condition (b)...",
        "source_historique_citee": "GEN04"
      },
      {
        "id": "C-03",
        "libelle": "Milices para-étatiques violentes",
        "applicable": false,              // critère non applicable à ce type de texte
        "reponse": null,
        "score": null,
        "justification": "Critère non applicable : texte législatif sans lien...",
        "source_historique_citee": null
      }
      // ... C-04 à C-17
    ],
    "score_total": 0.42,                   // somme / critères applicables
    "criteres_applicables": 12,
    "phase_principale": "Phase 2",         // phase dominante selon les critères actifs
    "position_frise": {
      "phase": 2,
      "label": "Légitimation médiatique et politique",
      "signal": "modéré",                  // aucun | faible | modéré | fort | critique
      "couleur": "orange"
    },
    "note_agent": "Attention particulière sur C-09 — le vote avec les voix RN..."
  },

  // ── VALIDATION HUMAINE ────────────────────────────────────────
  "validation": {
    "validateur": null,                    // nom du directeur de publication
    "date_validation": null,
    "signature_git": null,                 // hash du commit de validation
    "decision": null,                      // approved | rejected | patch_required
    "motif_rejet": null,
    "corrections_apportees": []
  },

  // ── SYMÉTRIE ─────────────────────────────────────────────────
  "symetrie": {
    "statut": "planifiee",                 // planifiee | en_cours | publiee | non_applicable
    "fiche_symetrique_id": null,           // id de la fiche symétrique une fois créée
    "date_limite": "2026-04-29",
    "texte_symetrique_identifie": null,
    "note": "Texte comparable à identifier : texte LFI restreignant..."
  },

  // ── PATCHES ──────────────────────────────────────────────────
  "patches": []                            // liste des mises à jour post-publication
  // {
  //   "patch_id": "PATCH-001",
  //   "date": "...",
  //   "agent_concerne": "agent_1 | agent_2 | agent_3 | agent_4",
  //   "motif": "...",
  //   "champs_modifies": [...],
  //   "auteur": "..."
  // }
}
```

---

## 2. Spécification des agents

### Agent 1 — Extraction factuelle

**Rôle** : produire la structure JSON complète à partir d'une source brute.
Ne connaît pas les critères de la grille. Ne fait aucune interprétation.

**Input** : URL ou texte brut du document source.

**Output** : objet JSON sections `source`, `auteurs`, `vote`, `texte_extrait`,
`contexte_procedural`, `sources_archivees` complétés.

**Prompt système** :
```
Tu es un agent d'extraction de données factuelles pour l'Observatoire La Bascule.

Ton unique rôle est d'extraire des informations factuelles vérifiables
à partir d'un document source. Tu ne fais aucune analyse, aucune
interprétation, aucun jugement de valeur.

Pour chaque source modifiable (réseaux sociaux, sites de partis,
déclarations en ligne), tu produis une copie locale du contenu au moment
de l'analyse. Si la source est inaccessible, tu l'indiques explicitement.

Tu complètes le schéma JSON fourni. Les champs que tu ne peux pas remplir
de manière certaine sont laissés à null — jamais inventés.

Si une information est ambiguë ou contestée par deux sources, tu inclus
les deux versions avec leur source respective.
```

**Contraintes techniques** :
- Appel API séparé, contexte vierge
- Archivage automatique des sources modifiables via `wget` ou équivalent
- Validation du JSON produit contre le schéma avant transmission

---

### Agent 2 — Arguments favorables

**Rôle** : produire le meilleur argumentaire possible en faveur du texte.

**Input** : sections `source`, `texte_extrait`, `contexte_procedural`
de la fiche JSON. **Ne reçoit pas** `arguments_defavorables` ni `scoring`.

**Output** : section `arguments_favorables` complétée.

**Prompt système** :
```
Tu es un agent d'analyse argumentative pour l'Observatoire La Bascule.

Ta mission dans cette passe : produire le meilleur argumentaire possible
EN FAVEUR du texte qui t'est soumis.

Tu n'es pas en train d'exprimer ton opinion. Tu construis le cas
le plus solide possible pour défendre ce texte, comme un avocat
défendrait son client.

Règles :
- Chaque argument doit être sourcé (lien, rapport, texte officiel)
- Tu cites les arguments des partisans réels du texte quand ils existent
- Tu inclus les arguments de droit, d'efficacité, de comparaison
  internationale, de sécurité, d'ordre public — tout ce qui est pertinent
- Tu ne fais aucune mention des arguments contre
- Si tu n'as pas d'argument solide sur un point, tu ne l'inventes pas

Tu produis entre 3 et 7 arguments structurés.
```

**Contraintes techniques** :
- Appel API séparé, contexte ne contenant PAS la sortie de l'Agent 3
- Le bord politique de l'auteur du texte n'est pas mentionné dans l'input
- `run_id` de l'appel enregistré pour traçabilité

---

### Agent 3 — Arguments défavorables

**Rôle** : produire le meilleur argumentaire possible contre le texte.

**Input** : identique à l'Agent 2. **Ne reçoit pas** `arguments_favorables`.

**Output** : section `arguments_defavorables` complétée.

**Prompt système** :
```
Tu es un agent d'analyse argumentative pour l'Observatoire La Bascule.

Ta mission dans cette passe : produire le meilleur argumentaire possible
CONTRE le texte qui t'est soumis.

Tu n'es pas en train d'exprimer ton opinion. Tu construis le cas
le plus solide possible contre ce texte, comme un avocat
défendrait la partie adverse.

Règles :
- Chaque argument doit être sourcé (lien, rapport, texte officiel,
  décision de justice, avis d'institution indépendante)
- Tu cites les arguments des opposants réels du texte quand ils existent
- Tu inclus les arguments de droit constitutionnel, de libertés
  fondamentales, d'efficacité, de comparaison internationale,
  de précédents historiques — tout ce qui est pertinent
- Tu ne fais aucune mention des arguments pour
- Si tu n'as pas d'argument solide sur un point, tu ne l'inventes pas

Tu produis entre 3 et 7 arguments structurés.
```

**Contraintes techniques** : identiques à l'Agent 2, appel séparé.

---

### Agent 4 — Synthèse et scoring

**Rôle** : appliquer la grille de critères et positionner sur la frise.

**Input** : fiche JSON complète avec `arguments_favorables` ET
`arguments_defavorables`. **Ne connaît pas** le bord politique de
l'auteur — ce champ est masqué dans l'input transmis à cet agent.

**Output** : section `scoring` complétée.

**Prompt système** :
```
Tu es un agent de scoring pour l'Observatoire La Bascule.

Tu reçois une fiche d'analyse avec des arguments favorables et défavorables
sur un texte politique. Tu ne sais pas quel parti l'a produit.

Ta mission : appliquer la grille de critères C-01 à C-17 de la méthode
La Bascule (version [GRILLE_VERSION]) pour produire un score de similitude
structurelle avec les séquences historiques de référence.

Pour chaque critère :
1. Détermine s'il est applicable à ce type de texte
2. Si applicable, réponds Oui / Non / Partiel selon la définition
   opérationnelle exacte du critère
3. En cas de doute, réponds Non — le bénéfice du doute va toujours
   dans le sens de la non-similitude
4. Justifie ta réponse en une phrase sourcée

Tu calcules le score total et positionnes la fiche sur la frise.

Tu ne qualifies jamais un parti ou un acteur de fasciste.
Tu documentes une similitude de mécanisme, pas une équivalence de nature.
```

**Contrainte critique** : le champ `auteurs[].parti` est remplacé par
`"[masqué]"` dans l'input transmis à cet agent. Le scoring est aveugle
au bord politique.

---

### Orchestrateur

**Technologie recommandée** : LangGraph (Python) ou n8n (no-code).

**Responsabilités** :
- Routing des inputs vers les agents dans l'ordre
- Gestion de l'état de la fiche JSON entre les étapes
- Gestion des cas non-nominaux (patch, re-scoring, symétrie)
- Déclenchement des alertes sur les flux Légifrance / data.gouv
- Versionnement Git automatique des fiches produites
- Interface de validation humaine (webhook ou interface web simple)

**Cas non-nominaux** :

| Cas | Agents relancés | Données réutilisées |
|-----|----------------|---------------------|
| Nouveau fait sur fiche publiée | Agent 1 uniquement | Agents 2, 3, 4 inchangés sauf si l'extraction change |
| Analyse symétrique | Agents 2, 3, 4 sur texte B | Agent 4 reçoit aussi scoring du texte A pour comparaison |
| Nouvelle version de grille | Agent 4 uniquement | Agents 1, 2, 3 inchangés |
| Source disparue | Agent 1 sur archive locale | Reste inchangé |
| Désaccord validateur | Patch ciblé sur section concernée | Reste inchangé |

---

## 3. Structure des dossiers GitHub

```
labascule/
├── methode-labascule.md          # Méthode — source de vérité
├── README.md
├── .gitignore
│
├── agents/                       # Spécification technique agents
│   ├── spec-agents.md            # Ce fichier
│   ├── schema-fiche.json         # Schéma JSON de référence (JSON Schema draft-07)
│   └── orchestrateur/            # Code orchestrateur (à venir)
│       ├── README.md
│       └── ...
│
├── prompts/                      # Prompts système versionnés
│   ├── system-agent1-v0.1.md
│   ├── system-agent2-v0.1.md
│   ├── system-agent3-v0.1.md
│   └── system-agent4-v0.1.md
│
├── fiches/                       # Analyses publiées
│   ├── archives/                 # Copies sources modifiables
│   ├── sources/                  # Textes sources archivés
│   └── FR-2024-LOI-001.json      # Exemple fiche (à venir)
│
└── site/                         # Code source site web (à venir)
```

---

## 4. Cas limites identifiés en V1

| # | Cas | Impact | Solution |
|---|-----|--------|----------|
| L1 | Texte touchant plusieurs phases simultanément | Agent 4 doit scorer tous les critères sans biais de phase | Agent 1 extrait tout sans filtrer — Agent 4 applique tous les critères applicables |
| L2 | Source disparue après archivage | Perte de traçabilité | Archive locale obligatoire à l'étape Agent 1 — `url_archive` toujours rempli |
| L3 | Bord politique déduit par l'Agent 4 malgré le masquage | Biais de scoring | Test de cohérence : mêmes textes, noms masqués différemment → scores doivent converger |
| L4 | Mise à jour de la grille mid-pipeline | Incohérence de version | `grille_version` verrouillée à l'ouverture de la fiche — re-scoring explicite si mise à jour |
| L5 | Pas de texte symétrique identifiable | Asymétrie non couverte | Mention obligatoire dans `symetrie.note` — délai étendu à 90 jours si besoin |
| L6 | Agent 2 ou 3 produit un argument contaminé par le bord politique | Biais introduit par l'IA | Validation humaine obligatoire — critère de rejet si un argument mentionne explicitement le parti |
| L7 | Score élevé sur critère unique (ex. C-09 seul à 1.0) | Score global faible mais signal fort | Publication du score par critère en plus du score global — signal critique unitaire visible |

---

*Fin du document spec-agents.md — version 0.1.0-draft*

[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
