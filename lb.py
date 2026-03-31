#!/usr/bin/env python3
"""
lb.py — Raccourcis CLI pour le pipeline La Bascule sous Docker.

Usage :
  python lb.py build                              # construit l'image Docker
  python lb.py run --url URL                      # analyse une URL
  python lb.py run --file texte.txt               # analyse un fichier local
  python lb.py run --url URL --id MON_ID          # avec identifiant personnalisé
  python lb.py patch --fiche fiches/FR-xxx.json   # patch une fiche existante
  python lb.py shell                              # ouvre un shell dans le container

Exemples :
  python lb.py run --url https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049040245
  python lb.py run --url https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049040245 --id FR-2024-LOI-042-v2
"""

import subprocess
import sys
import argparse
from pathlib import Path


def build():
    print("Construction de l'image labascule-pipeline...")
    subprocess.run(["docker", "compose", "build"], check=True)
    print("✓ Image construite.")


def run_pipeline(url=None, file=None, fiche_id=None):
    cmd = ["docker", "compose", "run", "--rm", "pipeline"]

    if url:
        cmd += ["--url", url]
    elif file:
        file_path = Path(file).resolve()
        cmd += ["--file", f"/app/input/{file_path.name}"]
    else:
        print("Erreur : --url ou --file requis.")
        sys.exit(1)

    if fiche_id:
        cmd += ["--id", fiche_id]

    if file:
        file_path = Path(file).resolve()
        cmd = (
            cmd[:4]
            + ["-v", f"{file_path.parent}:/app/input"]
            + cmd[4:]
        )

    subprocess.run(cmd, check=True)


def patch(fiche_path):
    fiche = Path(fiche_path).resolve()
    fiche_name = fiche.name
    cmd = [
        "docker", "compose", "run", "--rm",
        "-v", f"{fiche.parent}:/app/fiches",
        "pipeline",
        "--fiche", f"/app/fiches/{fiche_name}",
        "--patch"
    ]
    subprocess.run(cmd, check=True)


def shell():
    subprocess.run([
        "docker", "compose", "run", "--rm",
        "--entrypoint", "/bin/bash",
        "pipeline"
    ])


def main():
    parser = argparse.ArgumentParser(description="Raccourcis CLI pour La Bascule Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build", help="Construire l'image Docker")

    run_parser = subparsers.add_parser("run", help="Analyser un texte")
    run_parser.add_argument("--url", help="URL du texte")
    run_parser.add_argument("--file", help="Fichier texte local")
    run_parser.add_argument("--id", help="Identifiant de la fiche")

    patch_parser = subparsers.add_parser("patch", help="Patcher une fiche existante")
    patch_parser.add_argument("--fiche", required=True, help="Chemin vers la fiche JSON")

    subparsers.add_parser("shell", help="Shell interactif dans le container")

    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "run":
        run_pipeline(url=args.url, file=args.file, fiche_id=args.id)
    elif args.command == "patch":
        patch(args.fiche)
    elif args.command == "shell":
        shell()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
