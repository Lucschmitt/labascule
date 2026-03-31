"""
Agent 3 — Arguments défavorables
Contexte ISOLÉ — ne reçoit pas la sortie de l'Agent 2.
Produit le meilleur argumentaire possible CONTRE le texte.
Input identique à l'Agent 2.

Modèle : injecté par l'orchestrateur via model_id + client.
Ne crée jamais son propre client — garantit la séparation de configuration.
"""

import json
from pipeline.utils import parse_json_robust

SYSTEM_PROMPT = """Tu es un agent d'analyse argumentative pour l'Observatoire La Bascule.

Ta mission dans cette passe : produire le meilleur argumentaire possible CONTRE
le texte qui t'est soumis.

Tu n'es pas en train d'exprimer ton opinion. Tu construis le cas le plus solide
possible contre ce texte, comme un avocat défendrait la partie adverse.

Règles :
- Chaque argument doit être sourcé (lien, rapport, texte officiel, décision de justice, avis institutionnel)
- Tu cites les arguments des opposants réels du texte quand ils existent
- Tu inclus les arguments de droit constitutionnel, de libertés fondamentales,
  d'efficacité, de comparaison internationale, de précédents historiques
- Tu ne fais AUCUNE mention des arguments pour
- Si tu n'as pas d'argument solide sur un point, tu ne l'inventes pas
- Tu produis entre 3 et 5 arguments structurés

Tu réponds UNIQUEMENT avec du JSON valide dans ce format :
{
  "arguments": [
    {
      "id": "ARG-DEF-001",
      "titre": "Titre court de l'argument",
      "corps": "Développement de l'argument en 2-4 phrases.",
      "sources_citees": ["source 1", "source 2"]
    }
  ]
}"""


def run(fiche_partielle: dict, client, model_id: str) -> dict:
    """
    Lance l'Agent 3 sur la fiche produite par l'Agent 1.

    IMPORTANT : reçoit EXACTEMENT le même input que l'Agent 2.
    Ne reçoit PAS les arguments favorables.
    Appel API séparé — contexte entièrement distinct de l'Agent 2.

    Le modèle et le client sont injectés par l'orchestrateur (randomisation).
    L'agent ne choisit pas son propre modèle.

    Args:
        fiche_partielle : dict contenant source, texte_extrait, contexte_procedural
        client          : instance API (Anthropic ou OpenRouter) — différent de l'Agent 2
        model_id        : identifiant du modèle attribué par assign_models()

    Returns:
        dict contenant la section arguments_defavorables
    """
    input_masque = {
        "source": {
            "type":             fiche_partielle.get("source", {}).get("type"),
            "reference":        fiche_partielle.get("source", {}).get("reference"),
            "date_publication": fiche_partielle.get("source", {}).get("date_publication"),
            "institution":      fiche_partielle.get("source", {}).get("institution"),
        },
        "texte_extrait":       fiche_partielle.get("texte_extrait", {}),
        "contexte_procedural": fiche_partielle.get("contexte_procedural", {}),
        "vote": {
            "pour":        fiche_partielle.get("vote", {}).get("pour"),
            "contre":      fiche_partielle.get("vote", {}).get("contre"),
            "abstentions": fiche_partielle.get("vote", {}).get("abstentions"),
            "note":        fiche_partielle.get("vote", {}).get("note"),
        },
    }

    prompt = f"""Voici un texte politique à analyser.

DONNÉES FACTUELLES :
{json.dumps(input_masque, ensure_ascii=False, indent=2)}

Produis le meilleur argumentaire possible CONTRE ce texte.
Réponds uniquement avec le JSON demandé."""

    response = client.messages.create(
        model=model_id,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    parsed = parse_json_robust(response.content[0].text)

    return {
        "arguments_defavorables": {
            "agent_run_id": response.id,
            "agent_model":  model_id,
            "arguments":    parsed.get("arguments", []),
        }
    }
