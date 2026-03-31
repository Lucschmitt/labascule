"""
Routeur de modèles — attribution aléatoire Agents 2 et 3.

Principe : contrebalancement aléatoire (Winer, Brown & Michels, 1991).
Les biais de génération propres à chaque LLM sont distribués uniformément
entre les rôles favorable/défavorable sur l'ensemble du corpus.
Sur N fiches, chaque modèle joue chaque rôle ~N/2 fois.

Références :
  [WIT91] Winer et al., Statistical Principles in Experimental Design, 3e éd.
  [PER23] Perez et al., Discovering Language Model Behaviors with
          Model-Written Evaluations, ACL 2023.
"""

import random
from dataclasses import dataclass


# ── Pool de modèles disponibles ──────────────────────────────────────────────

MODELS = {
    "sonnet": {
        "id":       "claude-sonnet-4-6",
        "provider": "anthropic",
        "role":     "fixed",          # Agents 1 et 4 uniquement
        "cost_per_1k_input":  0.003,
        "cost_per_1k_output": 0.015,
    },
    "haiku": {
        "id":       "claude-haiku-4-5-20251001",
        "provider": "anthropic",
        "role":     "pool",           # Agents 2 ou 3
        "cost_per_1k_input":  0.00025,
        "cost_per_1k_output": 0.00125,
    },
    "gemini_flash": {
        "id":       "google/gemini-flash-1.5",
        "provider": "openrouter",
        "role":     "pool",           # Agents 2 ou 3
        "cost_per_1k_input":  0.000075,
        "cost_per_1k_output": 0.0003,
    },
}

# Modèles éligibles au pool argumentatif (Agents 2 et 3)
POOL = [m["id"] for m in MODELS.values() if m["role"] == "pool"]

# Modèle fixe pour Agents 1 et 4
FIXED = next(m["id"] for m in MODELS.values() if m["role"] == "fixed")


# ── Fonction principale ───────────────────────────────────────────────────────

@dataclass
class ModelAssignment:
    agent1_model: str
    agent2_model: str
    agent3_model: str
    agent4_model: str
    assignment_mode: str = "randomized"

    def to_dict(self) -> dict:
        return {
            "agent1_model":     self.agent1_model,
            "agent2_model":     self.agent2_model,
            "agent3_model":     self.agent3_model,
            "agent4_model":     self.agent4_model,
            "assignment_mode":  self.assignment_mode,
        }


def assign_models(seed: int = None) -> ModelAssignment:
    """
    Tire aléatoirement l'attribution des modèles pour les Agents 2 et 3.

    Contrebalancement uniforme : sur N appels successifs avec seed=None,
    chaque modèle du pool occupe chaque rôle environ N/2 fois.

    Args:
        seed: graine optionnelle pour reproductibilité (tests, re-run).
              En production, laisser None pour un tirage vraiment aléatoire.

    Returns:
        ModelAssignment avec les 4 modèles attribués et le mode d'attribution.
    """
    if len(POOL) < 2:
        raise RuntimeError(
            f"Le pool ne contient qu'un seul modèle ({POOL}). "
            "Ajoutez au moins un second modèle pour activer la randomisation."
        )

    rng = random.Random(seed)

    # Tirage uniforme : 50/50 entre les deux configurations possibles
    if rng.random() < 0.5:
        model_a, model_b = POOL[0], POOL[1]   # Haiku Pour, Gemini Contre
    else:
        model_a, model_b = POOL[1], POOL[0]   # Gemini Pour, Haiku Contre

    return ModelAssignment(
        agent1_model=FIXED,
        agent2_model=model_a,
        agent3_model=model_b,
        agent4_model=FIXED,
    )


def get_client_for_model(model_id: str):
    """
    Retourne le client API approprié selon le fournisseur du modèle.

    Anthropic → client Anthropic standard
    OpenRouter → client Anthropic avec base_url OpenRouter
    """
    from anthropic import Anthropic

    provider = next(
        (m["provider"] for m in MODELS.values() if m["id"] == model_id),
        None
    )

    if provider == "anthropic":
        return Anthropic()

    if provider == "openrouter":
        import os
        return Anthropic(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://labascule.eu",
                "X-Title":      "La Bascule — Observatoire démocratique",
            },
        )

    raise ValueError(
        f"Modèle inconnu ou fournisseur non configuré : {model_id}"
    )
