"""
Point d'entrée CLI du pipeline La Bascule.

Usage :
  python run_pipeline.py --url URL_DU_TEXTE
  python run_pipeline.py --file chemin/vers/texte.txt
  python run_pipeline.py --fiche fiches/FR-2024-LOI-042.json --patch

Exemples :
  python run_pipeline.py --url https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049040245
  python run_pipeline.py --file textes/loi-immigration-2024.txt --id FR-2024-LOI-042-v2
  python run_pipeline.py --fiche fiches/FR-2024-LOI-042.json --patch
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from pipeline import orchestrator


def fetch_text_from_url(url: str) -> str:
    """
    Récupère le texte brut d'une URL.
    - URLs Légifrance → API PISTE (OAuth2, credentials dans .env)
    - Autres URLs     → requête HTTP directe
    """
    from pipeline.legifrance_fetcher import fetch_from_url, fetch_raw
    import urllib.error

    if "legifrance.gouv.fr" in url:
        try:
            print("  Récupération via API PISTE/Légifrance...")
            texte, _ = fetch_from_url(url)
            return texte
        except Exception as e:
            print(f"  API PISTE indisponible ({e}), tentative directe...")

    try:
        return fetch_raw(url)
    except urllib.error.URLError as e:
        print(f"Erreur de récupération URL : {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline d'analyse La Bascule — 4 agents IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--url", help="URL du texte à analyser")
    input_group.add_argument("--file", help="Chemin vers un fichier texte local")
    input_group.add_argument("--fiche", help="Chemin vers une fiche JSON existante (mode patch)")

    parser.add_argument("--id", help="Identifiant de la fiche (auto-généré si absent)")
    parser.add_argument("--output", default="fiches", help="Dossier de sortie (défaut: fiches)")
    parser.add_argument("--patch", action="store_true", help="Mode patch sur une fiche existante")
    parser.add_argument("--seed", type=int, default=None,
                        help="Graine pour la randomisation des modèles (tests reproductibles)")

    args = parser.parse_args()

    if args.patch and args.fiche:
        print(f"Mode patch : {args.fiche}")
        orchestrator.patch(fiche_path=args.fiche)
        return

    if args.url:
        print(f"Récupération de : {args.url}")
        texte = fetch_text_from_url(args.url)
        url_source = args.url
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Erreur : fichier introuvable — {args.file}")
            sys.exit(1)
        texte = path.read_text(encoding="utf-8")
        url_source = str(path.resolve())
    else:
        parser.print_help()
        sys.exit(1)

    if not texte.strip():
        print("Erreur : texte vide.")
        sys.exit(1)

    print(f"Texte récupéré : {len(texte)} caractères")

    fiche = orchestrator.run(
        texte_source=texte,
        url_source=url_source,
        fiche_id=args.id,
        output_dir=args.output,
        seed=args.seed,
    )

    scoring = fiche.get("scoring", {})
    score_L = scoring.get("score_L", {})
    score_C = scoring.get("score_C", {})
    ma      = fiche.get("model_assignment", {})

    pct     = round(score_L.get("score", scoring.get("score_total", 0)) * 100, 1)
    signal  = score_L.get("signal") or scoring.get("position_frise", {}).get("signal", "?")
    couleur = score_L.get("couleur") or scoring.get("position_frise", {}).get("couleur", "?")

    print("\n" + "="*40)
    print("RÉSULTAT")
    print("="*40)
    print(f"Fiche ID    : {fiche.get('fiche_id')}")
    print(f"Score L     : {pct}%  ({score_L.get('calcul', '?')})")
    if score_C.get("score") is not None:
        print(f"Score C     : {round(score_C['score'] * 100, 1)}%  ({score_C.get('calcul', '?')})")
    else:
        print(f"Score C     : —  (module contextuel non alimenté)")
    print(f"Signal      : {signal} ({couleur})")
    print(f"Phase       : {scoring.get('phase_principale', '?')}")
    print(f"Agent 2     : {ma.get('agent2_model', '?')}")
    print(f"Agent 3     : {ma.get('agent3_model', '?')}")
    print("="*40)
    print("\n⚠️  Rappel : cette fiche est en statut 'draft' — validation humaine requise avant publication.")


if __name__ == "__main__":
    main()
