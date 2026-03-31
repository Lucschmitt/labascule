"""
Orchestrateur — assemble les 4 agents dans l'ordre correct.
Gère l'état de la fiche, la randomisation des modèles, les erreurs
et la sortie finale.

Principe de randomisation (v0.2.2) :
  Contrebalancement aléatoire (Winer, Brown & Michels, 1991) appliqué
  aux LLMs. À chaque fiche, un tirage uniforme détermine quel modèle
  du pool joue le rôle favorable et lequel joue le rôle défavorable.
  Sur N fiches, chaque modèle occupe chaque rôle ~N/2 fois — les biais
  propres à chaque modèle se distribuent symétriquement entre les deux
  côtés du débat.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from pipeline import agent1_extract, agent2_favorable, agent3_defavorable, agent4_scoring
from pipeline.model_router import assign_models, get_client_for_model


def run(
    texte_source: str,
    url_source: str = None,
    fiche_id: str = None,
    output_dir: str = "fiches",
    seed: int = None,
) -> dict:
    """
    Lance le pipeline complet sur un texte source.

    Ordre garanti :
    1. Tirage aléatoire des modèles Agents 2 et 3
    2. Agent 1 — extraction factuelle (modèle fixe)
    3. Agents 2 et 3 — arguments (modèles randomisés, contextes isolés)
    4. Agent 4 — scoring aveugle au parti (modèle fixe)

    Args:
        texte_source : texte brut du document
        url_source   : URL d'origine
        fiche_id     : identifiant (auto-généré si absent)
        output_dir   : dossier de sortie pour les fiches JSON
        seed         : graine pour la randomisation (None = production,
                       entier = reproductibilité pour tests et re-runs)

    Returns:
        dict de la fiche complète
    """
    if not fiche_id:
        fiche_id = f"FR-{datetime.now().strftime('%Y')}-AUTO-{str(uuid.uuid4())[:8].upper()}"

    print(f"\n{'='*60}")
    print(f"Pipeline La Bascule — {fiche_id}")
    print(f"{'='*60}\n")

    # ── Tirage aléatoire des modèles ─────────────────────────────────────────
    assignment = assign_models(seed=seed)
    print(f"→ Attribution des modèles [{'seed=' + str(seed) if seed else 'aléatoire'}]")
    print(f"  Agent 2 (favorable)   : {assignment.agent2_model}")
    print(f"  Agent 3 (défavorable) : {assignment.agent3_model}")

    client_a2 = get_client_for_model(assignment.agent2_model)
    client_a3 = get_client_for_model(assignment.agent3_model)

    # ── ÉTAPE 1 — Extraction factuelle ───────────────────────────────────────
    print("→ Agent 1 : extraction factuelle...")
    fiche = agent1_extract.run(
        texte_source=texte_source,
        url_source=url_source,
        fiche_id=fiche_id,
    )
    print(f"  ✓ Source : {fiche.get('source', {}).get('reference', 'inconnue')[:60]}")

    # Enregistre l'attribution dans la fiche dès l'étape 1
    fiche["model_assignment"] = assignment.to_dict()

    # ── ÉTAPE 2 — Arguments favorables (contexte A) ──────────────────────────
    print(f"→ Agent 2 : arguments favorables [{assignment.agent2_model}]...")
    result_favorable = agent2_favorable.run(
        fiche_partielle=fiche,
        client=client_a2,
        model_id=assignment.agent2_model,
    )
    fiche.update(result_favorable)
    n_fav = len(fiche.get("arguments_favorables", {}).get("arguments", []))
    print(f"  ✓ {n_fav} argument(s) favorable(s) produit(s)")

    # ── ÉTAPE 3 — Arguments défavorables (contexte B) ────────────────────────
    print(f"→ Agent 3 : arguments défavorables [{assignment.agent3_model}]...")
    result_defavorable = agent3_defavorable.run(
        fiche_partielle=fiche,
        client=client_a3,
        model_id=assignment.agent3_model,
    )
    fiche.update(result_defavorable)
    n_def = len(fiche.get("arguments_defavorables", {}).get("arguments", []))
    print(f"  ✓ {n_def} argument(s) défavorable(s) produit(s)")

    # ── ÉTAPE 4 — Scoring (bord politique masqué) ────────────────────────────
    print("→ Agent 4 : scoring [parti masqué]...")
    result_scoring = agent4_scoring.run(fiche=fiche)
    fiche.update(result_scoring)

    score = fiche.get("scoring", {})
    pct    = round(score.get("score_total", 0) * 100, 1)
    signal = score.get("position_frise", {}).get("signal", "?")
    print(f"  ✓ Score : {pct}% — signal : {signal}")

    # ── Validation humaine ───────────────────────────────────────────────────
    fiche["validation"] = {
        "validateur":         None,
        "date_validation":    None,
        "signature_git":      None,
        "decision":           "pending",
        "corrections_apportees": [],
    }

    symetrie_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    fiche["symetrie"] = {
        "statut":              "planifiee",
        "fiche_symetrique_id": None,
        "date_limite":         symetrie_date,
        "note":                "À compléter : identifier le texte symétrique",
    }

    fiche["patches"] = []

    # ── Sauvegarde ───────────────────────────────────────────────────────────
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    fiche_path = output_path / f"{fiche_id}.json"

    with open(fiche_path, "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Fiche sauvegardée : {fiche_path}")
    print(f"{'='*60}\n")

    return fiche


def patch(fiche_path: str, nouveau_texte: str = None, seed: int = None) -> dict:
    """
    Cas non-nominal : met à jour une fiche existante.

    Si nouveau_texte : relance Agent 1 uniquement.
    Sinon : propose un menu interactif.

    Un nouveau tirage aléatoire est effectué pour les Agents 2 et 3
    si ceux-ci sont relancés — sauf si seed est fourni pour reproduire
    l'attribution d'origine (ex. correction d'un bug, pas d'un biais).
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
                fiche_id=fiche.get("fiche_id"),
            )
            fiche.update({k: v for k, v in result.items()
                          if k in ["source", "auteurs", "vote", "texte_extrait", "contexte_procedural"]})

    if choix in ("2", "3", "tous"):
        # Nouveau tirage pour les agents argumentatifs relancés
        assignment = assign_models(seed=seed)
        fiche["model_assignment"] = assignment.to_dict()
        print(f"  Nouveau tirage — Agent 2 : {assignment.agent2_model} / Agent 3 : {assignment.agent3_model}")

        client_a2 = get_client_for_model(assignment.agent2_model)
        client_a3 = get_client_for_model(assignment.agent3_model)

        if choix == "2" or choix == "tous":
            result = agent2_favorable.run(
                fiche_partielle=fiche,
                client=client_a2,
                model_id=assignment.agent2_model,
            )
            fiche.update(result)

        if choix == "3" or choix == "tous":
            result = agent3_defavorable.run(
                fiche_partielle=fiche,
                client=client_a3,
                model_id=assignment.agent3_model,
            )
            fiche.update(result)

    if choix == "4" or choix == "tous":
        result = agent4_scoring.run(fiche=fiche)
        fiche.update(result)

    patch_entry = {
        "patch_id": f"PATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date":     datetime.now().isoformat(),
        "agents_relances": [choix],
        "motif":    input("Motif du patch : ").strip() or "Non précisé",
        "auteur":   "pipeline",
    }
    fiche.setdefault("patches", []).append(patch_entry)

    with open(fiche_path, "w", encoding="utf-8") as f:
        json.dump(fiche, f, ensure_ascii=False, indent=2)

    print(f"✓ Patch appliqué : {patch_entry['patch_id']}")
    return fiche
