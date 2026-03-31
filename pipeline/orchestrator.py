"""
Orchestrateur — assemble les 4 agents dans l'ordre correct.
Gère l'état de la fiche, les erreurs, et la sortie finale.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from pipeline import agent1_extract, agent2_favorable, agent3_defavorable, agent4_scoring


def run(
    texte_source: str,
    url_source: str = None,
    fiche_id: str = None,
    output_dir: str = "fiches"
) -> dict:
    """
    Lance le pipeline complet sur un texte source.
    
    Ordre garanti :
    1. Agent 1 — extraction factuelle
    2. Agents 2 et 3 — arguments (appels séparés, contextes isolés)
    3. Agent 4 — scoring aveugle au parti
    
    Args:
        texte_source: texte brut du document
        url_source: URL d'origine
        fiche_id: identifiant (auto-généré si absent)
        output_dir: dossier de sortie pour les fiches JSON
    
    Returns:
        dict de la fiche complète
    """
    if not fiche_id:
        fiche_id = f"FR-{datetime.now().strftime('%Y')}-AUTO-{str(uuid.uuid4())[:8].upper()}"

    print(f"\n{'='*60}")
    print(f"Pipeline La Bascule — {fiche_id}")
    print(f"{'='*60}\n")

    # ── ÉTAPE 1 — Extraction factuelle ──────────────────────────
    print("→ Agent 1 : extraction factuelle...")
    fiche = agent1_extract.run(
        texte_source=texte_source,
        url_source=url_source,
        fiche_id=fiche_id
    )
    print(f"  ✓ Source : {fiche.get('source', {}).get('reference', 'inconnue')[:60]}")

    # ── ÉTAPE 2 — Arguments favorables (contexte A) ─────────────
    print("→ Agent 2 : arguments favorables [contexte isolé]...")
    result_favorable = agent2_favorable.run(fiche_partielle=fiche)
    fiche.update(result_favorable)
    n_fav = len(fiche.get("arguments_favorables", {}).get("arguments", []))
    print(f"  ✓ {n_fav} argument(s) favorable(s) produit(s)")

    # ── ÉTAPE 3 — Arguments défavorables (contexte B) ───────────
    print("→ Agent 3 : arguments défavorables [contexte isolé]...")
    result_defavorable = agent3_defavorable.run(fiche_partielle=fiche)
    fiche.update(result_defavorable)
    n_def = len(fiche.get("arguments_defavorables", {}).get("arguments", []))
    print(f"  ✓ {n_def} argument(s) défavorable(s) produit(s)")

    # ── ÉTAPE 4 — Scoring (bord politique masqué) ───────────────
    print("→ Agent 4 : scoring [parti masqué]...")
    result_scoring = agent4_scoring.run(fiche=fiche)
    fiche.update(result_scoring)

    score = fiche.get("scoring", {})
    pct = round(score.get("score_total", 0) * 100, 1)
    signal = score.get("position_frise", {}).get("signal", "?")
    print(f"  ✓ Score : {pct}% — signal : {signal}")

    # ── Validation humaine ───────────────────────────────────────
    fiche["validation"] = {
        "validateur": None,
        "date_validation": None,
        "signature_git": None,
        "decision": "pending",
        "corrections_apportees": []
    }

    symetrie_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    fiche["symetrie"] = {
        "statut": "planifiee",
        "fiche_symetrique_id": None,
        "date_limite": symetrie_date,
        "note": "À compléter : identifier le texte symétrique"
    }

    fiche["patches"] = []

    # ── Sauvegarde ───────────────────────────────────────────────
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fiche_path = output_path / f"{fiche_id}.json"

    with open(fiche_path, "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Fiche sauvegardée : {fiche_path}")
    print(f"{'='*60}\n")

    return fiche


def patch(fiche_path: str, nouveau_texte: str = None) -> dict:
    """
    Cas non-nominal : met à jour une fiche existante.
    
    Si nouveau_texte : relance Agent 1 uniquement.
    Sinon : propose un menu interactif.
    """
    with open(fiche_path, "r", encoding="utf-8") as f:
        fiche = json.load(f)

    print(f"\nPatch de la fiche : {fiche.get('fiche_id')}")
    print("Agents disponibles : [1] Extraction  [2] Favorable  [3] Défavorable  [4] Scoring")
    choix = input("Quel agent relancer ? (1/2/3/4/tous) : ").strip()

    if choix == "1" or choix == "tous":
        if nouveau_texte:
            result = agent1_extract.run(
                texte_source=nouveau_texte,
                url_source=fiche.get("source", {}).get("url_source"),
                fiche_id=fiche.get("fiche_id")
            )
            fiche.update({k: v for k, v in result.items()
                          if k in ["source", "auteurs", "vote", "texte_extrait", "contexte_procedural"]})

    if choix == "2" or choix == "tous":
        result = agent2_favorable.run(fiche_partielle=fiche)
        fiche.update(result)

    if choix == "3" or choix == "tous":
        result = agent3_defavorable.run(fiche_partielle=fiche)
        fiche.update(result)

    if choix == "4" or choix == "tous":
        result = agent4_scoring.run(fiche=fiche)
        fiche.update(result)

    patch_entry = {
        "patch_id": f"PATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": datetime.now().isoformat(),
        "agents_relances": [choix],
        "motif": input("Motif du patch : ").strip() or "Non précisé",
        "auteur": "pipeline"
    }
    fiche.setdefault("patches", []).append(patch_entry)

    with open(fiche_path, "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)

    print(f"✓ Patch appliqué : {patch_entry['patch_id']}")
    return fiche
