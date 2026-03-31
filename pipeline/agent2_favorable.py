"""
Agent 2 — Arguments favorables
Contexte ISOLÉ — ne reçoit pas la sortie de l'Agent 3.
Produit le meilleur argumentaire possible EN FAVEUR du texte.
Le bord politique de l'auteur n'est pas dans l'input.
"""

import json
from anthropic import Anthropic
from pipeline.utils import parse_json_robust

client = Anthropic()

SYSTEM_PROMPT = """Tu es un agent d'analyse argumentative pour l'Observatoire La Bascule.

Ta mission dans cette passe : produire le meilleur argumentaire possible EN FAVEUR
du texte qui t'est soumis.

Tu n'es pas en train d'exprimer ton opinion. Tu construis le cas le plus solide
possible pour défendre ce texte, comme un avocat défendrait son client.

Règles :
- Chaque argument doit être sourcé (lien, rapport, texte officiel)
- Tu cites les arguments des partisans réels du texte quand ils existent
- Tu inclus les arguments de droit, d'efficacité, de comparaison internationale — tout ce qui est pertinent
- Tu ne fais AUCUNE mention des arguments contre
- Si tu n'as pas d'argument solide sur un point, tu ne l'inventes pas
- Tu produis entre 3 et 5 arguments structurés

Tu réponds UNIQUEMENT avec du JSON valide dans ce format :
{
  "arguments": [
    {
      "id": "ARG-FAV-001",
      "titre": "Titre court de l'argument",
      "corps": "Développement de l'argument en 2-4 phrases.",
      "sources_citees": ["source 1", "source 2"]
    }
  ]
}"""


def run(fiche_partielle: dict) -> dict:
    """
    Lance l'Agent 2 sur la fiche produite par l'Agent 1.
    
    IMPORTANT : reçoit uniquement les sections factuelles.
    Ne reçoit PAS les arguments défavorables.
    Le parti de l'auteur est masqué.
    
    Args:
        fiche_partielle: dict contenant source, texte_extrait, contexte_procedural
    
    Returns:
        dict contenant la section arguments_favorables
    """
    input_masque = {
        "source": {
            "type": fiche_partielle.get("source", {}).get("type"),
            "reference": fiche_partielle.get("source", {}).get("reference"),
            "date_publication": fiche_partielle.get("source", {}).get("date_publication"),
            "institution": fiche_partielle.get("source", {}).get("institution"),
        },
        "texte_extrait": fiche_partielle.get("texte_extrait", {}),
        "contexte_procedural": fiche_partielle.get("contexte_procedural", {}),
        "vote": {
            "pour": fiche_partielle.get("vote", {}).get("pour"),
            "contre": fiche_partielle.get("vote", {}).get("contre"),
            "abstentions": fiche_partielle.get("vote", {}).get("abstentions"),
            "note": fiche_partielle.get("vote", {}).get("note"),
        }
    }

    prompt = f"""Voici un texte politique à analyser.

DONNÉES FACTUELLES :
{json.dumps(input_masque, ensure_ascii=False, indent=2)}

Produis le meilleur argumentaire possible EN FAVEUR de ce texte.
Réponds uniquement avec le JSON demandé."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    parsed = parse_json_robust(response.content[0].text)

    return {
        "arguments_favorables": {
            "agent_run_id": response.id,
            "arguments": parsed.get("arguments", [])
        }
    }
