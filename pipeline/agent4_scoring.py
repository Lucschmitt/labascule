"""
Agent 4 — Synthèse et scoring
Reçoit les deux jeux d'arguments SANS avoir vu leur production.
Le bord politique de l'auteur est masqué dans l'input.
Applique la grille C-01 à C-17.
"""

import json
from anthropic import Anthropic
from pipeline.utils import parse_json_robust

client = Anthropic()

CRITERES = [
    {"id": "C-01", "libelle": "Discours de déclin et victimisation nationale",
     "definition": "Le texte mobilise-t-il un discours de déclin national, de victimisation collective ou de menace existentielle pesant sur l'identité ou la communauté nationale ? Oui si le texte contient au moins 2 éléments parmi : (a) référence à une époque passée meilleure ; (b) désignation d'un groupe interne ou externe responsable du déclin ; (c) urgence existentielle justifiant des mesures exceptionnelles ; (d) vocabulaire de survie ou de dernier recours. Seuil : acteurs institutionnels uniquement."},
    {"id": "C-02", "libelle": "Culte de l'unité et désignation de l'ennemi intérieur",
     "definition": "Le texte présente-t-il l'unité nationale comme valeur suprême ET désigne-t-il un groupe interne comme obstacle à cette unité ? Les DEUX conditions sont requises."},
    {"id": "C-03", "libelle": "Existence de milices ou groupuscules para-étatiques violents",
     "definition": "INAPPLICABLE_SUR_TEXTE_ISOLE. Ce critère est contextuel — il évalue l'état de la société, pas un texte législatif. Répondre systématiquement applicable=false sur une fiche législative."},
    {"id": "C-04", "libelle": "Crise économique et déclassement des classes moyennes",
     "definition": "INAPPLICABLE_SUR_TEXTE_ISOLE. Ce critère est contextuel — il évalue l'état macroéconomique, pas un texte législatif. Répondre systématiquement applicable=false sur une fiche législative."},
    {"id": "C-05", "libelle": "Financement bourgeois ou patronal de groupes d'extrême droite",
     "definition": "Liens documentés entre acteurs économiques et financement de partis/groupuscules d'extrême droite. Source primaire vérifiable requise."},
    {"id": "C-06", "libelle": "Laissé-faire judiciaire asymétrique",
     "definition": "L'État laisse se développer la violence d'extrême droite sans poursuites, tout en poursuivant la violence d'autres bords. L'asymétrie est la condition nécessaire. Documenter sur au moins 3 cas dans 12 mois glissants."},
    {"id": "C-07", "libelle": "Concentration médiatique au profit de l'extrême droite",
     "definition": "Un acteur économique contrôle plusieurs médias d'audience nationale avec (a) au moins 2 médias, (b) sanctions régulateur pour déséquilibre, (c) ligne éditoriale favorisant l'extrême droite de manière récurrente."},
    {"id": "C-08", "libelle": "Légitimation électorale croissante de l'extrême droite",
     "definition": "Parti d'extrême droite obtenant >15% aux élections nationales, progression continue sur au moins 2 scrutins consécutifs, programme incluant préférence nationale ou restriction droits minorités."},
    {"id": "C-09", "libelle": "Ralliement du centre-droit à l'extrême droite",
     "definition": "Accord électoral formel entre droite traditionnelle et extrême droite OU refus d'un responsable de droite d'appeler à voter contre l'extrême droite au second tour face à un candidat républicain."},
    {"id": "C-10", "libelle": "Ostracisation asymétrique de l'extrême gauche",
     "definition": "Mesures d'exclusion appliquées à l'extrême gauche SANS mesures équivalentes appliquées à l'extrême droite pour des comportements comparables dans la même période. L'asymétrie est la condition nécessaire."},
    {"id": "C-11", "libelle": "Division interne de la gauche face à la montée de l'extrême droite",
     "definition": "Au moins 2 partis de gauche représentés au Parlement refusent de s'allier au second tour face à l'extrême droite OU dirigeants d'un même parti avec positions contradictoires sur l'opportunité d'alliance."},
    {"id": "C-12", "libelle": "Ralliement des partis modérés après la prise du pouvoir",
     "definition": "Partis républicains votant la confiance à un gouvernement d'extrême droite, ou s'abstenant lors d'un vote de censure. S'applique UNIQUEMENT après prise de pouvoir effective de l'extrême droite au niveau national."},
    {"id": "C-13", "libelle": "Mesures d'exception répétées restreignant les libertés",
     "definition": "Mesures restreignant droits de réunion, expression, grève ou presse, prises par ordonnance/décret sans vote parlementaire préalable, ET usage récurrent (>3 fois en 12 mois) pour des mesures de même nature."},
    {"id": "C-14", "libelle": "Restriction ou destruction des syndicats indépendants",
     "definition": "Réduction financement syndicats >20% sans mesure compensatoire OU création syndicats-maison financés par l'employeur OU restriction droit de grève hors obligations constitutionnelles de service minimum."},
    {"id": "C-15", "libelle": "Restriction de la liberté de la presse",
     "definition": "Loi restreignant accès journalistes à sources d'intérêt public OU pressions documentées conduisant à autocensure/fermeture de médias indépendants OU <3 acteurs contrôlent >60% de l'audience nationale dans un même segment."},
    {"id": "C-16", "libelle": "Hégémonie institutionnelle d'un parti ou bloc",
     "definition": "Contrôle simultané pendant >12 mois d'au moins 3 des 4 éléments : (a) présidence/gouvernement, (b) majorité stable AN, (c) nominations institutions indépendantes, (d) direction médias audiovisuels publics. Une majorité ordinaire seule ne suffit pas."},
    {"id": "C-17", "libelle": "Dissolution des corps intermédiaires",
     "definition": ">5 organisations de la société civile dissoutes par décret en 24 mois ET ces dissolutions touchent de manière disproportionnée un bord politique identifiable."}
]

SYSTEM_PROMPT = """Tu es un agent de scoring pour l'Observatoire La Bascule.

Tu reçois une fiche d'analyse avec des arguments favorables et défavorables sur un texte politique.
Tu ne connais pas le parti ou le bord politique de l'auteur — ce champ est masqué.

Ta mission : appliquer la grille de critères C-01 à C-17 pour produire un score de similitude
structurelle avec les séquences historiques de bascule vers des régimes autoritaires.

RÈGLES IMPÉRATIVES :

1. Tout critère marqué INAPPLICABLE_SUR_TEXTE_ISOLE dans sa définition doit recevoir
   applicable=false sans exception.

2. Les critères C-05, C-06, C-07, C-10, C-11, C-12, C-16 nécessitent des données externes
   (financements, statistiques judiciaires, résultats électoraux détaillés). Si la fiche ne
   contient pas ces données explicitement, applicable=false.

3. RÈGLE SPÉCIALE C-08 et C-09 : ces critères évaluent la dynamique politique au moment du vote,
   pas le texte lui-même. Si la fiche ou les arguments documentent explicitement le soutien
   d'un parti d'extrême droite au texte, ses déclarations de victoire, ou la convergence entre
   droite traditionnelle et extrême droite — alors C-08 et C-09 sont APPLICABLES.
   - C-08 : un parti d'extrême droite qui vote une loi gouvernementale ET revendique cette victoire
     constitue une légitimation électorale de ses thèmes → score oui si documenté dans la fiche.
   - C-09 : un gouvernement de centre-droit qui fait adopter sa loi grâce aux voix de l'extrême droite
     constitue un ralliement de facto → score oui si documenté dans la fiche.

4. C-01 évalue le discours des auteurs. Utilise les déclarations publiques documentées dans la fiche
   (sections auteurs.declarations_publiques ou contexte_procedural.reactions_partis_opposants).

5. En cas de doute sur oui/non/partiel, réponds Non.
   Le bénéfice du doute va dans le sens de la non-similitude.

6. Tu ne qualifies jamais un parti ou un acteur de fasciste.
   Tu documentes une similitude de mécanisme, pas une équivalence de nature.

Score : Partiel = 0.5, Oui = 1.0, Non = 0.0

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
    
    IMPORTANT :
    - Reçoit les arguments favorables ET défavorables
    - Le champ auteurs[].parti est masqué
    - N'a pas accès au processus de production des arguments
    
    Args:
        fiche: dict complet avec source, arguments_favorables, arguments_defavorables
    
    Returns:
        dict contenant la section scoring
    """
    auteurs_masques = []
    for a in fiche.get("auteurs", []):
        auteurs_masques.append({
            "nom": a.get("nom"),
            "fonction": a.get("fonction"),
            "parti": "[masqué]",
            "mandat": a.get("mandat")
        })

    input_scoring = {
        "source": {
            "type": fiche.get("source", {}).get("type"),
            "reference": fiche.get("source", {}).get("reference"),
            "date_publication": fiche.get("source", {}).get("date_publication"),
        },
        "auteurs": auteurs_masques,
        "texte_extrait": fiche.get("texte_extrait", {}),
        "arguments_favorables": fiche.get("arguments_favorables", {}).get("arguments", []),
        "arguments_defavorables": fiche.get("arguments_defavorables", {}).get("arguments", [])
    }

    criteres_str = json.dumps(CRITERES, ensure_ascii=False, indent=2)

    prompt = f"""Voici une fiche d'analyse à scorer.

DONNÉES (parti masqué) :
{json.dumps(input_scoring, ensure_ascii=False, indent=2)}

GRILLE DE CRITÈRES (applique chacun selon sa définition exacte) :
{criteres_str}

Applique la grille et produis le scoring JSON demandé."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    parsed = parse_json_robust(response.content[0].text)
    criteres = parsed.get("criteres", [])

    applicables = [c for c in criteres if c.get("applicable")]
    points = sum(c.get("score", 0) for c in applicables)
    total = len(applicables)
    score_pct = round(points / total, 4) if total > 0 else 0

    SEUILS = [
        (0.80, "critique", "rouge foncé", 5),
        (0.60, "fort", "rouge", 4),
        (0.40, "modéré", "orange", 3),
        (0.20, "faible", "jaune", 1),
        (0.00, "aucun", "vert", 0),
    ]
    signal, couleur, phase = "aucun", "vert", 0
    for seuil, s, c, p in SEUILS:
        if score_pct >= seuil:
            signal, couleur, phase = s, c, p
            break

    return {
        "scoring": {
            "agent_run_id": response.id,
            "criteres": criteres,
            "score_total": score_pct,
            "criteres_applicables": total,
            "points_obtenus": points,
            "calcul": f"{points}/{total} = {round(score_pct * 100, 1)}%",
            "phase_principale": f"Phase {phase}",
            "position_frise": {
                "phase": phase,
                "signal": signal,
                "couleur": couleur
            },
            "note_agent": parsed.get("note_agent", "")
        }
    }
