"""
Utilitaires partagés entre les agents.
"""

import json


def parse_json_robust(raw: str) -> dict:
    """
    Parse du JSON potentiellement tronqué ou mal formaté.
    Essaie plusieurs stratégies avant d'abandonner.
    """
    # Nettoyage des balises markdown
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    # Tentative directe
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Trouve le dernier objet JSON complet
    depth = 0
    last_valid = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(raw):
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
        if not in_string:
            if ch in '{[':
                depth += 1
            elif ch in '}]':
                depth -= 1
                if depth == 0:
                    last_valid = i + 1

    if last_valid > 0:
        try:
            return json.loads(raw[:last_valid])
        except json.JSONDecodeError:
            pass

    # Dernier recours : ferme les accolades manquantes
    open_braces = raw.count('{') - raw.count('}')
    open_brackets = raw.count('[') - raw.count(']')
    raw_fixed = raw + (']' * max(0, open_brackets)) + ('}' * max(0, open_braces))

    try:
        return json.loads(raw_fixed)
    except json.JSONDecodeError as e:
        raise ValueError(f"Impossible de parser le JSON après toutes les tentatives : {e}\n"
                         f"Début du contenu : {raw[:200]}") from e
