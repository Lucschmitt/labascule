"""
Agent 4 — Synthèse et scoring
Reçoit les deux jeux d'arguments SANS avoir vu leur production.
Le bord politique de l'auteur est masqué dans l'input.
Applique la grille C-01 à C-19 (v0.2.2).

Calcule deux scores distincts :
  score_L  — sous-grille Législative (testable sur texte isolé)
  score_C  — sous-grille Contextuelle (nécessite fenêtre 12 mois)
             → null si le module contextuel trimestriel n'a pas encore tourné

Enregistre les modèles des Agents 2 et 3 pour la traçabilité.
"""

import json
from anthropic import Anthropic
from pipeline.utils import parse_json_robust

# Client instancié à la demande (lazy) pour éviter un plantage à l'import
# si ANTHROPIC_API_KEY n'est pas encore dans l'environnement (tests unitaires)
_client: Anthropic | None = None

def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client

# ── Grille complète C-01 à C-19 (v0.2.2) ────────────────────────────────────
#
# Chaque critère porte :
#   sous_grille : "L" (législatif, scorable sur texte isolé)
#               | "C" (contextuel, nécessite données externes sur 12 mois)
#   partiel_possible : True si une réponse 0.5 est explicitement prévue
#                      par la définition (conditions a/b = Oui, condition c = Partiel)

CRITERES = [
    {
        "id": "C-01",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Discours de déclin et victimisation nationale",
        "definition": (
            "Le texte mobilise-t-il un discours de déclin national, de victimisation collective "
            "ou de menace existentielle pesant sur l'identité ou la communauté nationale ? "
            "Oui si le texte contient au moins 2 éléments parmi : "
            "(a) référence à une époque passée meilleure ; "
            "(b) désignation d'un groupe interne ou externe responsable du déclin ; "
            "(c) urgence existentielle justifiant des mesures exceptionnelles ; "
            "(d) vocabulaire de survie ou de dernier recours. "
            "Seuil : acteurs institutionnels uniquement."
        ),
    },
    {
        "id": "C-02",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Culte de l'unité et désignation de l'ennemi intérieur",
        "definition": (
            "Le texte présente-t-il l'unité nationale comme valeur suprême ET désigne-t-il "
            "un groupe interne comme obstacle à cette unité ? Les DEUX conditions sont requises."
        ),
    },
    {
        "id": "C-03",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Existence de milices ou groupuscules para-étatiques violents",
        "definition": (
            "INAPPLICABLE_SUR_TEXTE_ISOLE. Critère contextuel — évalue l'état de la société "
            "sur 12 mois glissants, pas un texte législatif isolé. "
            "Répondre systématiquement applicable=false sur une fiche législative."
        ),
    },
    {
        "id": "C-04",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Crise économique et déclassement des classes moyennes",
        "definition": (
            "INAPPLICABLE_SUR_TEXTE_ISOLE. Critère contextuel — évalue l'état macroéconomique "
            "sur 12 mois glissants, pas un texte législatif isolé. "
            "Répondre systématiquement applicable=false sur une fiche législative."
        ),
    },
    {
        "id": "C-05",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Financement bourgeois ou patronal de groupes d'extrême droite",
        "definition": (
            "Liens documentés entre acteurs économiques et financement de partis ou groupuscules "
            "d'extrême droite. Source primaire vérifiable requise. "
            "Si la fiche ne contient pas ces données explicitement : applicable=false."
        ),
    },
    {
        "id": "C-06",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Laissé-faire judiciaire asymétrique",
        "definition": (
            "L'État laisse se développer la violence d'extrême droite sans poursuites, "
            "tout en poursuivant la violence d'autres bords. "
            "L'asymétrie est la condition nécessaire. "
            "Documenter sur au moins 3 cas dans 12 mois glissants. "
            "Si la fiche ne contient pas ces données : applicable=false."
        ),
    },
    {
        "id": "C-07",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Concentration médiatique au profit de l'extrême droite",
        "definition": (
            "Un acteur économique contrôle plusieurs médias d'audience nationale avec "
            "(a) au moins 2 médias, (b) sanctions régulateur pour déséquilibre, "
            "(c) ligne éditoriale favorisant l'extrême droite de manière récurrente. "
            "Si la fiche ne contient pas ces données : applicable=false."
        ),
    },
    {
        "id": "C-08",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Légitimation électorale croissante de l'extrême droite",
        "definition": (
            "Parti d'extrême droite obtenant >15% aux élections nationales, "
            "progression continue sur au moins 2 scrutins consécutifs, "
            "programme incluant préférence nationale ou restriction droits minorités. "
            "RÈGLE SPÉCIALE : si la fiche documente explicitement qu'un parti d'extrême droite "
            "a voté ce texte ET revendiqué la victoire, C-08 est applicable → score Oui."
        ),
    },
    {
        "id": "C-09",
        "sous_grille": "C",
        "partiel_possible": True,
        "libelle": "Ralliement ou accommodation rhétorique du centre-droit à l'extrême droite",
        "definition": (
            "Oui si : (a) accord électoral formel entre droite traditionnelle et extrême droite ; "
            "OU (b) refus public d'un responsable de droite d'appeler à voter contre l'extrême droite "
            "au second tour face à un candidat républicain. "
            "RÈGLE SPÉCIALE : un gouvernement de centre-droit faisant adopter sa loi grâce aux voix "
            "de l'extrême droite constitue un ralliement de facto → Oui si documenté dans la fiche. "
            "Partiel si, sans (a) ni (b), les deux sous-conditions suivantes sont réunies : "
            "(c1) le texte ou la déclaration traite d'un thème dont l'extrême droite détient le cadre "
            "interprétatif caractéristique — désignation d'un groupe responsable + solution impliquant "
            "une différenciation de droits selon l'origine ou le statut — ET "
            "(c2) ce cadre est reproduit sans distanciation critique : sans attribution nominale à un "
            "acteur tiers (α), sans mention des contraintes constitutionnelles ou conventionnelles (β), "
            "sans qualification de la mesure comme dérogation au principe d'égalité (γ). "
            "En cas de doute entre Partiel et Non, répondre Non."
        ),
    },
    {
        "id": "C-10",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Ostracisation asymétrique de l'extrême gauche",
        "definition": (
            "Mesures d'exclusion appliquées à l'extrême gauche SANS mesures équivalentes "
            "appliquées à l'extrême droite pour des comportements comparables dans la même période. "
            "L'asymétrie est la condition nécessaire. "
            "Si la fiche ne contient pas ces données : applicable=false."
        ),
    },
    {
        "id": "C-11",
        "sous_grille": "C",
        "partiel_possible": False,
        "libelle": "Division interne de la gauche face à la montée de l'extrême droite",
        "definition": (
            "Au moins 2 partis de gauche représentés au Parlement refusent de s'allier au second tour "
            "face à l'extrême droite OU dirigeants d'un même parti avec positions contradictoires "
            "sur l'opportunité d'alliance. "
            "Si la fiche ne contient pas ces données : applicable=false."
        ),
    },
    {
        "id": "C-12",
        "sous_grille": "C",
        "partiel_possible": True,
        "libelle": "Accommodation des partis modérés face à l'extrême droite au pouvoir",
        "definition": (
            "Oui si un ou plusieurs partis républicains : "
            "(a) votent la confiance ou s'abstiennent lors d'un vote de censure permettant à un "
            "gouvernement à participation d'extrême droite de se maintenir ; "
            "OU (b) refusent de rejoindre une coalition d'opposition alors que le gouvernement "
            "a documenté des atteintes à des libertés fondamentales. "
            "Partiel si, sans (a) ni (b) : (c) des partis républicains refusent systématiquement "
            "de nommer l'extrême droite comme adversaire prioritaire tout en participant à des "
            "coalitions ou votes qui lui sont favorables. "
            "Inapplicable en l'absence de toute participation ou influence d'extrême droite "
            "au niveau gouvernemental national."
        ),
    },
    {
        "id": "C-13",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Mesures d'exception répétées restreignant les libertés",
        "definition": (
            "Mesures restreignant droits de réunion, expression, grève ou presse, prises par "
            "ordonnance ou décret sans vote parlementaire préalable, ET usage récurrent "
            "(>3 fois en 12 mois) pour des mesures de même nature. "
            "NOTE v0.2.2 : ce critère doit être évalué en contexte d'ensemble (C-13 seul ne suffit pas)."
        ),
    },
    {
        "id": "C-14",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Restriction ou destruction des syndicats indépendants",
        "definition": (
            "Réduction financement syndicats >20% sans mesure compensatoire "
            "OU création syndicats-maison financés par l'employeur "
            "OU restriction droit de grève hors obligations constitutionnelles de service minimum."
        ),
    },
    {
        "id": "C-15",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Restriction de la liberté de la presse",
        "definition": (
            "Loi restreignant accès journalistes à sources d'intérêt public "
            "OU pressions documentées conduisant à autocensure ou fermeture de médias indépendants "
            "OU moins de 3 acteurs contrôlent plus de 60% de l'audience nationale dans un même segment."
        ),
    },
    {
        "id": "C-16",
        "sous_grille": "L",
        "partiel_possible": True,
        "libelle": "Hégémonie ou capture institutionnelle d'un parti ou bloc",
        "definition": (
            "Oui si un même parti ou bloc contrôle au moins 3 des 4 éléments suivants pendant >12 mois : "
            "(a) présidence ou gouvernement, (b) majorité stable à l'Assemblée nationale, "
            "(c) nominations dans les institutions indépendantes orientées vers des profils loyaux, "
            "(d) direction éditoriale des médias audiovisuels publics. "
            "Une majorité parlementaire ordinaire seule ne suffit pas. "
            "Partiel si contrôle de (a) et (b) ET tentatives documentées d'influer sur (c) ou (d), "
            "signalées par une institution indépendante, une juridiction ou une organisation "
            "de défense de l'État de droit."
        ),
    },
    {
        "id": "C-17",
        "sous_grille": "L",
        "partiel_possible": False,
        "libelle": "Dissolution des corps intermédiaires",
        "definition": (
            "Plus de 5 organisations de la société civile dissoutes par décret en 24 mois "
            "ET ces dissolutions touchent de manière disproportionnée un bord politique identifiable."
        ),
    },
    {
        "id": "C-18",
        "sous_grille": "L",
        "partiel_possible": True,
        "libelle": "Instrumentalisation différentielle des institutions indépendantes",
        "definition": (
            "Des institutions formellement indépendantes (justice, autorités de régulation, "
            "Conseil constitutionnel, HATVP, etc.) sont mobilisées de manière asymétrique "
            "contre des opposants politiques. "
            "Oui si : (a) une institution indépendante prend une décision affectant un acteur politique ; "
            "ET (b) des comportements comparables du camp opposé n'ont pas donné lieu à procédures "
            "équivalentes dans la même période (12 mois glissants) ; "
            "ET (c) au moins une source qualifiante (journaliste, juriste, organisation de défense "
            "de l'État de droit) a explicitement qualifié cette asymétrie. "
            "Partiel si asymétrie documentée sur 1 seul cas. "
            "Oui si asymétrie documentée sur 3+ cas distincts en 12 mois "
            "ou si une réforme organique modifie le mode de nomination d'une institution indépendante."
        ),
    },
    {
        "id": "C-19",
        "sous_grille": "L",
        "partiel_possible": True,
        "libelle": "Rejet de la légitimité des opposants",
        "definition": (
            "Des acteurs institutionnels au pouvoir remettent en cause le droit des opposants "
            "à participer au jeu démocratique. "
            "Oui si un acteur institutionnel (membre du gouvernement, parlementaire de la majorité) "
            "tient publiquement l'un des discours suivants : "
            "(a) un parti d'opposition est qualifié d'illégitime, d'antirépublicain ou de subversif "
            "sans base juridique établie ; "
            "(b) la victoire électorale d'un parti d'opposition est présentée comme une menace pour "
            "l'État ou l'ordre constitutionnel ; "
            "(c) l'opposition est accusée de servir des intérêts étrangers ou criminels sans preuve. "
            "Partiel dès 1 occurrence documentée. "
            "Oui si 3+ occurrences en 6 mois ou institutionnalisé dans un texte officiel. "
            "SIGNAL PRÉCOCE : un Partiel seul ne constitue pas un signal préoccupant — "
            "sa valeur est dans la combinaison avec d'autres critères."
        ),
    },
]

# ── Index rapide par sous-grille ─────────────────────────────────────────────
IDS_L = {c["id"] for c in CRITERES if c["sous_grille"] == "L"}
IDS_C = {c["id"] for c in CRITERES if c["sous_grille"] == "C"}

SEUILS = [
    (0.80, "critique", "rouge foncé", 5),
    (0.60, "fort",     "rouge",       4),
    (0.40, "modéré",   "orange",      3),
    (0.20, "faible",   "jaune",       1),
    (0.00, "aucun",    "vert",        0),
]


def _signal_from_score(score_pct: float) -> tuple:
    for seuil, signal, couleur, phase in SEUILS:
        if score_pct >= seuil:
            return signal, couleur, phase
    return "aucun", "vert", 0


SYSTEM_PROMPT = """Tu es un agent de scoring pour l'Observatoire La Bascule.

Tu reçois une fiche d'analyse avec des arguments favorables et défavorables sur un texte politique.
Tu ne connais pas le parti ou le bord politique de l'auteur — ce champ est masqué.

Ta mission : appliquer la grille de critères C-01 à C-19 pour produire un score de similitude
structurelle avec les séquences historiques de bascule vers des régimes autoritaires.

RÈGLES IMPÉRATIVES :

1. Tout critère dont la définition contient INAPPLICABLE_SUR_TEXTE_ISOLE reçoit applicable=false
   sans exception.

2. Les critères de sous-grille C (C-03 à C-12) nécessitent des données contextuelles sur 12 mois.
   Si la fiche ne les contient pas explicitement : applicable=false.
   Exception : C-08 et C-09 peuvent être applicables si la fiche documente explicitement
   des soutiens ou votes de l'extrême droite (voir définitions).

3. C-09 admet une réponse Partiel (0.5) via les sous-conditions c1+c2 — lire la définition
   complète avant de scorer. En cas de doute entre Partiel et Non : Non.

4. C-12 admet une réponse Partiel (0.5) via la condition (c) — lire la définition complète.
   Inapplicable si aucune participation ou influence d'extrême droite au niveau gouvernemental.

5. C-16 admet une réponse Partiel (0.5) pour la capture institutionnelle en cours — lire la
   définition complète.

6. C-18 admet Partiel sur 1 cas documenté, Oui sur 3+ cas ou réforme organique.

7. C-19 admet Partiel dès 1 occurrence. Signal précoce — ne pas surévaluer seul.

8. C-01 évalue le discours des auteurs. Utilise les déclarations publiques documentées dans la fiche.

9. En cas de doute sur oui/non/partiel, réponds Non.
   Le bénéfice du doute va dans le sens de la non-similitude.

10. Tu ne qualifies jamais un parti ou un acteur de fasciste.
    Tu documentes une similitude de mécanisme, pas une équivalence de nature.

Score : Partiel = 0.5, Oui = 1.0, Non = 0.0, Non applicable = null

Tu réponds UNIQUEMENT avec du JSON valide dans ce format :
{
  "criteres": [
    {
      "id": "C-01",
      "applicable": true,
      "reponse": "oui|non|partiel",
      "score": 0.0,
      "justification": "..."
    }
  ],
  "note_agent": "Observation générale sur l'analyse"
}"""


def run(fiche: dict) -> dict:
    """
    Lance l'Agent 4 sur la fiche complète.

    - Reçoit les arguments favorables ET défavorables
    - Le champ auteurs[].parti est masqué
    - N'a pas accès au processus de production des arguments
    - Calcule score_L (sous-grille Législative) et score_C (sous-grille Contextuelle) séparément
    - Enregistre les modèles des Agents 2 et 3 pour la traçabilité

    Args:
        fiche: dict complet avec source, arguments_favorables, arguments_defavorables,
               et model_assignment (produit par l'orchestrateur)

    Returns:
        dict contenant la section scoring
    """
    auteurs_masques = []
    for a in fiche.get("auteurs", []):
        auteurs_masques.append({
            "nom":      a.get("nom"),
            "fonction": a.get("fonction"),
            "parti":    "[masqué]",
            "mandat":   a.get("mandat"),
        })

    input_scoring = {
        "source": {
            "type":             fiche.get("source", {}).get("type"),
            "reference":        fiche.get("source", {}).get("reference"),
            "date_publication": fiche.get("source", {}).get("date_publication"),
        },
        "auteurs":               auteurs_masques,
        "texte_extrait":         fiche.get("texte_extrait", {}),
        "arguments_favorables":  fiche.get("arguments_favorables", {}).get("arguments", []),
        "arguments_defavorables": fiche.get("arguments_defavorables", {}).get("arguments", []),
    }

    criteres_str = json.dumps(
        [{k: v for k, v in c.items() if k != "partiel_possible"} for c in CRITERES],
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""Voici une fiche d'analyse à scorer.

DONNÉES (parti masqué) :
{json.dumps(input_scoring, ensure_ascii=False, indent=2)}

GRILLE DE CRITÈRES C-01 à C-19 (applique chacun selon sa définition exacte) :
{criteres_str}

Applique la grille et produis le scoring JSON demandé."""

    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    parsed = parse_json_robust(response.content[0].text)
    criteres_scores = parsed.get("criteres", [])

    # ── Calcul score_L (sous-grille Législative) ─────────────────────────────
    criteres_L = [c for c in criteres_scores if c.get("id") in IDS_L and c.get("applicable")]
    points_L   = sum(c.get("score", 0) for c in criteres_L)
    total_L    = len(criteres_L)
    score_L    = round(points_L / total_L, 4) if total_L > 0 else 0

    # ── Calcul score_C (sous-grille Contextuelle) ────────────────────────────
    # Null si aucun critère C applicable — signifie que le module contextuel
    # trimestriel n'a pas alimenté la fiche, pas que le score est zéro.
    criteres_C = [c for c in criteres_scores if c.get("id") in IDS_C and c.get("applicable")]
    points_C   = sum(c.get("score", 0) for c in criteres_C)
    total_C    = len(criteres_C)
    score_C    = round(points_C / total_C, 4) if total_C > 0 else None

    # ── Score global (L uniquement pour les fiches législatives isolées) ─────
    signal_L, couleur_L, phase_L = _signal_from_score(score_L)

    # ── Traçabilité des modèles Agents 2 et 3 ────────────────────────────────
    model_assignment = fiche.get("model_assignment", {})

    return {
        "scoring": {
            "agent_run_id":   response.id,
            "agent_model":    "claude-sonnet-4-6",
            "agent2_model":   model_assignment.get("agent2_model"),
            "agent3_model":   model_assignment.get("agent3_model"),
            "assignment_mode": model_assignment.get("assignment_mode", "unknown"),
            "grille_version": "0.2.2",

            # Scores distincts par sous-grille
            "score_L": {
                "score":              score_L,
                "criteres_applicables": total_L,
                "points_obtenus":     points_L,
                "calcul":             f"{points_L}/{total_L} = {round(score_L * 100, 1)}%",
                "signal":             signal_L,
                "couleur":            couleur_L,
                "phase":              phase_L,
            },
            "score_C": {
                "score":              score_C,
                "criteres_applicables": total_C,
                "points_obtenus":     points_C if total_C > 0 else None,
                "calcul":             (
                    f"{points_C}/{total_C} = {round(score_C * 100, 1)}%"
                    if total_C > 0 else "null — module contextuel non alimenté"
                ),
                "note": (
                    "Score contextuel calculé sur critères C explicitement documentés dans la fiche."
                    if total_C > 0
                    else "Aucun critère C applicable — score_C null jusqu'à alimentation trimestrielle."
                ),
            },

            # Score global affiché = score_L (référence principale pour une fiche isolée)
            "score_total":         score_L,
            "criteres_applicables": total_L,
            "points_obtenus":      points_L,
            "calcul":              f"{points_L}/{total_L} = {round(score_L * 100, 1)}%",
            "phase_principale":    f"Phase {phase_L}",
            "position_frise": {
                "phase":   phase_L,
                "signal":  signal_L,
                "couleur": couleur_L,
            },

            # Détail critère par critère
            "criteres": criteres_scores,
            "note_agent": parsed.get("note_agent", ""),
        }
    }
