#!/usr/bin/env python3
"""
test_pipeline.py — Tests du pipeline La Bascule v0.2.2

Trois niveaux :
  Niveau 1 — Tests unitaires sans API (imports, logique pure)
  Niveau 2 — Test d'intégration avec API réelle (texte court, seed fixe)
  Niveau 3 — Test de régression sur la fiche de calibration CAL-DE-1933-001

Usage :
  python test_pipeline.py              # niveaux 1 et 2
  python test_pipeline.py --all        # niveaux 1, 2 et 3 (appels API complets)
  python test_pipeline.py --level 1    # niveau 1 uniquement (sans API)
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ── Couleurs terminal ─────────────────────────────────────────────────────────
OK   = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m⚠\033[0m"
INFO = "\033[94m·\033[0m"

results = []

def check(name: str, passed: bool, detail: str = ""):
    status = OK if passed else FAIL
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    results.append((name, passed))
    return passed

def section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


# ══════════════════════════════════════════════════════════════════════════════
# NIVEAU 1 — Tests unitaires (sans API)
# ══════════════════════════════════════════════════════════════════════════════

def test_level1():
    section("Niveau 1 — Imports et logique pure")

    # 1.1 Import model_router
    try:
        from pipeline.model_router import assign_models, get_client_for_model, POOL, FIXED, ModelAssignment
        check("Import model_router", True)
    except Exception as e:
        check("Import model_router", False, str(e))
        return False

    # 1.2 Pool correctement configuré
    check("Pool contient 2 modèles", len(POOL) == 2, f"trouvé : {POOL}")

    # 1.3 Reproductibilité par seed
    r1 = assign_models(seed=42)
    r2 = assign_models(seed=42)
    check("Seed reproductible", r1.agent2_model == r2.agent2_model)

    # 1.4 Différenciation sans seed
    configs = set()
    for _ in range(20):
        r = assign_models()
        configs.add((r.agent2_model, r.agent3_model))
    check("Randomisation active (2 configs sur 20 tirages)", len(configs) == 2,
          f"configs vues : {len(configs)}")

    # 1.5 Distribution ~50/50 sur 200 tirages
    from collections import Counter
    c = Counter(assign_models().agent2_model for _ in range(200))
    ratio = min(c.values()) / max(c.values())
    check("Distribution 50/50 (ratio min/max > 0.7)", ratio > 0.7,
          f"ratio : {ratio:.2f}")

    # 1.6 to_dict() complet
    d = r1.to_dict()
    expected_keys = {"agent1_model", "agent2_model", "agent3_model", "agent4_model", "assignment_mode"}
    check("ModelAssignment.to_dict() complet", set(d.keys()) == expected_keys)
    check("assignment_mode = 'randomized'", d["assignment_mode"] == "randomized")

    # 1.7 Import agents sans crash (pas d'instanciation API au module level)
    try:
        import pipeline.agent2_favorable as a2
        import pipeline.agent3_defavorable as a3
        check("Import agent2/agent3 sans API key", True)
    except Exception as e:
        check("Import agent2/agent3 sans API key", False, str(e))

    # 1.8 Signatures des run() agents 2 et 3
    import inspect
    sig2 = inspect.signature(a2.run)
    sig3 = inspect.signature(a3.run)
    check("Agent 2 run() accepte client + model_id",
          "client" in sig2.parameters and "model_id" in sig2.parameters)
    check("Agent 3 run() accepte client + model_id",
          "client" in sig3.parameters and "model_id" in sig3.parameters)

    # 1.9 Import agent4 sans crash (client lazy)
    try:
        import pipeline.agent4_scoring as a4
        check("Import agent4 sans API key (client lazy)", True)
    except Exception as e:
        check("Import agent4 sans API key (client lazy)", False, str(e))
        return False

    # 1.10 Grille C-01 à C-19
    from pipeline.agent4_scoring import CRITERES, IDS_L, IDS_C
    check("Grille contient 19 critères", len(CRITERES) == 19, f"trouvé : {len(CRITERES)}")
    check("C-18 et C-19 en sous-grille L", "C-18" in IDS_L and "C-19" in IDS_L)
    check("C-09 en sous-grille C", "C-09" in IDS_C)
    check("C-03 et C-04 en sous-grille C", "C-03" in IDS_C and "C-04" in IDS_C)
    check("C-13 en sous-grille L", "C-13" in IDS_L)
    l_count = len(IDS_L)
    c_count = len(IDS_C)
    check(f"Répartition L={l_count} C={c_count} (L=9, C=10)", l_count == 9 and c_count == 10,
          f"L={l_count}, C={c_count}")

    # 1.11 Partiel possible sur C-09, C-12, C-16, C-18, C-19
    partiel_ids = {c["id"] for c in CRITERES if c.get("partiel_possible")}
    expected_partiel = {"C-09", "C-12", "C-16", "C-18", "C-19"}
    check("Partiel configuré sur C-09/C-12/C-16/C-18/C-19",
          partiel_ids == expected_partiel, f"trouvé : {partiel_ids}")

    # 1.12 Import orchestrateur
    try:
        import pipeline.orchestrator as orch
        import inspect
        sig = inspect.signature(orch.run)
        check("Orchestrateur run() accepte seed", "seed" in sig.parameters)
    except Exception as e:
        check("Import orchestrateur", False, str(e))

    return True


# ══════════════════════════════════════════════════════════════════════════════
# NIVEAU 2 — Test d'intégration avec API réelle (texte court)
# ══════════════════════════════════════════════════════════════════════════════

TEXTE_TEST = """
Loi n° 2024-TEST du 1er janvier 2024 relative à la sécurité nationale.

Article 1 : En cas de menace grave à l'ordre public, le ministre de l'Intérieur
peut, par décret, suspendre le droit de réunion dans les zones concernées.

Article 2 : Les étrangers en situation irrégulière présents sur le territoire
national depuis moins de cinq ans ne pourront bénéficier des aides au logement.

Article 3 : Toute organisation dont l'activité est jugée contraire aux valeurs
fondamentales de la République peut faire l'objet d'une dissolution administrative.
"""

def test_level2():
    section("Niveau 2 — Test d'intégration API (seed=42, texte court)")

    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"  {WARN} ANTHROPIC_API_KEY non définie — niveau 2 ignoré")
        return True

    try:
        from pipeline.orchestrator import run as orch_run

        print(f"  {INFO} Lancement pipeline (seed=42, ~60s)...")
        fiche = orch_run(
            texte_source=TEXTE_TEST,
            url_source="https://test.labascule.local/texte-test",
            fiche_id="TEST-INTEGRATION-001",
            output_dir="fiches/test",
            seed=42,
        )

        # Vérifications structurelles
        check("Fiche produite", isinstance(fiche, dict))
        check("fiche_id présent", fiche.get("fiche_id") == "TEST-INTEGRATION-001")

        ma = fiche.get("model_assignment", {})
        check("model_assignment présent", bool(ma))
        check("agent2_model et agent3_model différents",
              ma.get("agent2_model") != ma.get("agent3_model"),
              f"{ma.get('agent2_model')} vs {ma.get('agent3_model')}")
        check("assignment_mode = randomized", ma.get("assignment_mode") == "randomized")

        scoring = fiche.get("scoring", {})
        check("scoring présent", bool(scoring))

        score_L = scoring.get("score_L", {})
        check("score_L présent", bool(score_L))
        check("score_L entre 0 et 1",
              0 <= score_L.get("score", -1) <= 1,
              f"score : {score_L.get('score')}")

        score_C = scoring.get("score_C", {})
        check("score_C présent (même si null)", "score" in score_C)
        if score_C.get("score") is None:
            print(f"    {INFO} score_C=null — attendu (module contextuel non alimenté)")

        check("19 critères scorés",
              len(scoring.get("criteres", [])) == 19,
              f"trouvé : {len(scoring.get('criteres', []))}")

        check("agent2_model dans scoring",
              scoring.get("agent2_model") == ma.get("agent2_model"))
        check("grille_version = 0.2.2", scoring.get("grille_version") == "0.2.2")

        # Vérification que les arguments_favorables/défavorables ont bien agent_model
        fav = fiche.get("arguments_favorables", {})
        defav = fiche.get("arguments_defavorables", {})
        check("arguments_favorables.agent_model présent", bool(fav.get("agent_model")))
        check("arguments_defavorables.agent_model présent", bool(defav.get("agent_model")))

        # Vérification sémantique minimale
        # Articles 1 et 3 devraient déclencher C-13 et C-17
        criteres_dict = {c["id"]: c for c in scoring.get("criteres", [])}
        c13 = criteres_dict.get("C-13", {})
        c17 = criteres_dict.get("C-17", {})
        if c13.get("applicable"):
            print(f"    {INFO} C-13 applicable : {c13.get('reponse')} — {c13.get('score')}")
        if c17.get("applicable"):
            print(f"    {INFO} C-17 applicable : {c17.get('reponse')} — {c17.get('score')}")

        # Sauvegarde JSON lisible
        fiche_path = Path("fiches/test/TEST-INTEGRATION-001.json")
        if fiche_path.exists():
            check("Fiche JSON sauvegardée sur disque", True, str(fiche_path))
        else:
            check("Fiche JSON sauvegardée sur disque", False, "fichier absent")

        print(f"\n    Score L : {round(score_L.get('score', 0) * 100, 1)}% — {score_L.get('signal', '?')}")
        print(f"    Agent 2 : {ma.get('agent2_model')}")
        print(f"    Agent 3 : {ma.get('agent3_model')}")

        return True

    except Exception as e:
        check("Pipeline complet sans exception", False, str(e))
        import traceback
        traceback.print_exc()
        return False


# ══════════════════════════════════════════════════════════════════════════════
# NIVEAU 3 — Régression sur CAL-DE-1933-001
# ══════════════════════════════════════════════════════════════════════════════

def test_level3():
    section("Niveau 3 — Régression calibration CAL-DE-1933-001")

    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"  {WARN} ANTHROPIC_API_KEY non définie — niveau 3 ignoré")
        return True

    cal_path = Path("fiches/calibration/CAL-DE-1933-001.json")
    if not cal_path.exists():
        check("Fiche CAL-DE-1933-001 trouvée", False, str(cal_path))
        return False

    with open(cal_path) as f:
        cal = json.load(f)

    texte_cal = cal.get("texte_extrait", {}).get("extrait_pertinent", "")
    if not texte_cal:
        check("Texte de calibration disponible", False)
        return False

    check("Texte de calibration disponible", True, f"{len(texte_cal)} chars")

    # Score attendu : 100% sur critères L applicables (C-01, C-02, C-13, C-15, C-16, C-17)
    ATTENDU_OUI_L = {"C-01", "C-02", "C-13", "C-15", "C-16", "C-17"}
    ATTENDU_SCORE_L_MIN = 0.8  # tolère un partiel sur un critère

    print(f"  {INFO} Lancement pipeline calibration (seed=1933, ~60s)...")

    try:
        from pipeline.orchestrator import run as orch_run
        fiche = orch_run(
            texte_source=texte_cal,
            url_source=cal.get("source", {}).get("url_source"),
            fiche_id="TEST-CAL-DE-1933-001",
            output_dir="fiches/test",
            seed=1933,
        )

        scoring = fiche.get("scoring", {})
        score_L = scoring.get("score_L", {})
        criteres_dict = {c["id"]: c for c in scoring.get("criteres", [])}

        score_val = score_L.get("score", 0)
        check(f"Score L ≥ {int(ATTENDU_SCORE_L_MIN*100)}% (étalon haut)",
              score_val >= ATTENDU_SCORE_L_MIN,
              f"obtenu : {round(score_val*100,1)}%")

        for cid in ATTENDU_OUI_L:
            c = criteres_dict.get(cid, {})
            ok = c.get("applicable") and c.get("score", 0) >= 0.5
            check(f"{cid} applicable et scoré ≥ 0.5",
                  ok, f"applicable={c.get('applicable')} score={c.get('score')}")

        # C-03 et C-04 doivent être non applicables (critères contextuels)
        for cid in ["C-03", "C-04"]:
            c = criteres_dict.get(cid, {})
            check(f"{cid} non applicable sur texte isolé", not c.get("applicable"))

        print(f"\n    Score L calibration : {round(score_val*100,1)}%")
        print(f"    Signal : {score_L.get('signal')}")
        return True

    except Exception as e:
        check("Pipeline calibration sans exception", False, str(e))
        import traceback
        traceback.print_exc()
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Tests pipeline La Bascule v0.2.2")
    parser.add_argument("--all", action="store_true", help="Inclut le niveau 3 (régression CAL)")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], help="Niveau unique à exécuter")
    args = parser.parse_args()

    print(f"\n{'═'*50}")
    print(f"  La Bascule — Tests pipeline v0.2.2")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═'*50}")

    from dotenv import load_dotenv
    load_dotenv()

    if args.level == 1:
        test_level1()
    elif args.level == 2:
        test_level2()
    elif args.level == 3:
        test_level3()
    else:
        test_level1()
        test_level2()
        if args.all:
            test_level3()

    # Résumé
    total   = len(results)
    passed  = sum(1 for _, ok in results if ok)
    failed  = total - passed

    print(f"\n{'═'*50}")
    print(f"  Résultat : {passed}/{total} tests passés", end="")
    if failed:
        print(f"  —  {FAIL} {failed} échec(s)")
    else:
        print(f"  —  {OK} tous OK")
    print(f"{'═'*50}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
