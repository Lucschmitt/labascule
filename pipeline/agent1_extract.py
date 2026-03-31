"""
Agent 1 — Extraction factuelle — version DEBUG
Identique à l'original + 3 prints pour diagnostiquer raw vide.
"""

import json
from datetime import datetime
from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = """Tu es un agent d'extraction de données factuelles pour l'Observatoire La Bascule.

Ton rôle : construire un dossier factuel complet sur un texte politique.
Tu disposes d'un outil de recherche web — utilise-le activement pour enrichir la fiche.

ÉTAPES À SUIVRE :
1. Lis le texte source fourni et extrais les données de base (référence, auteurs, vote, articles clés).
2. Recherche sur le web les éléments de contexte manquants :
   - Déclarations publiques des auteurs du texte (citations exactes si possible)
   - Réactions de l'opposition et des partis tiers
   - Avis d'institutions indépendantes (Conseil constitutionnel, CNCDH, Défenseur des droits...)
   - Articles de presse de référence sur le vote et son contexte
   - Réactions des syndicats et associations concernés
3. Compile tout dans le schéma JSON fourni.

RÈGLES :
- Tu ne fais aucune interprétation ni jugement de valeur
- Chaque information doit être attribuée à sa source
- Les champs non renseignables sont à null — jamais inventés
- Si deux sources se contredisent, inclus les deux versions avec leur source

Tu reponds UNIQUEMENT avec du JSON valide, sans markdown ni explication."""

EXTRACTION_TEMPLATE = {
    "source": {"type": None, "reference": None, "url_source": None, "date_publication": None, "institution": None},
    "auteurs": [],
    "vote": {"pour": None, "contre": None, "abstentions": None, "groupes_pour": [], "groupes_contre": [], "note": None},
    "texte_extrait": {"extrait_pertinent": None, "url_texte_integral": None},
    "contexte_procedural": {"note": None}
}


def run(texte_source: str, url_source: str = None, fiche_id: str = None) -> dict:
    if not fiche_id:
        fiche_id = f"FR-{datetime.now().strftime('%Y-%m%d-%H%M%S')}"

    prompt = f"""Voici un document a analyser. Extrait toutes les informations factuelles
disponibles et complete le schema JSON ci-dessous.

URL source : {url_source or 'non fournie'}

DOCUMENT :
---
{texte_source[:8000]}
---

SCHEMA A COMPLETER (reponds uniquement avec le JSON rempli) :
{json.dumps(EXTRACTION_TEMPLATE, ensure_ascii=False, indent=2)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    print(f"  [DBG] stop_reason={response.stop_reason} nb_blocs={len(response.content)}", flush=True)
    for i, b in enumerate(response.content):
        text = getattr(b, "text", None)
        print(f"  [DBG] bloc[{i}] type={b.type} has_text={text is not None} text={repr((text or '')[:80])}", flush=True)

    raw = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw += block.text

    print(f"  [DBG] raw avant nettoyage={repr(raw[:100])}", flush=True)

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        depth = 0; last_valid = 0; in_string = False; escape_next = False
        for i, ch in enumerate(raw):
            if escape_next: escape_next = False; continue
            if ch == '\\' and in_string: escape_next = True; continue
            if ch == '"' and not escape_next: in_string = not in_string
            if not in_string:
                if ch in '{[': depth += 1
                elif ch in '}]':
                    depth -= 1
                    if depth == 0: last_valid = i + 1
        if last_valid > 0: raw = raw[:last_valid]
        else:
            open_count = raw.count('{') - raw.count('}')
            raw = raw + ('}' * max(0, open_count))
        extracted = json.loads(raw)

    fiche = {
        "fiche_id": fiche_id,
        "schema_version": "0.1.0",
        "grille_version": "0.1.0-draft",
        "modele_ia": "claude-sonnet-4-6",
        "date_analyse": datetime.now().isoformat(),
        "statut": "draft",
        "analyse_symetrique_prevue": None,
        "agent1_run_id": response.id,
        **extracted
    }
    return fiche
