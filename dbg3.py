from anthropic import Anthropic
from dotenv import load_dotenv
import json
load_dotenv()

c = Anthropic()
tools = [{"type": "web_search_20250305", "name": "web_search"}]

TEXTE = """
Loi n 2024-TEST du 1er janvier 2024 relative a la securite nationale.
Article 1 : En cas de menace grave a l ordre public, le ministre de l Interieur
peut, par decret, suspendre le droit de reunion dans les zones concernees.
Article 2 : Les etrangers en situation irreguliere presents sur le territoire
national depuis moins de cinq ans ne pourront beneficier des aides au logement.
"""

TEMPLATE = {
    "source": {"type": None, "reference": None, "url_source": None, "date_publication": None, "institution": None},
    "auteurs": [],
    "vote": {"pour": None, "contre": None, "abstentions": None, "groupes_pour": [], "groupes_contre": [], "note": None},
    "texte_extrait": {"extrait_pertinent": None, "url_texte_integral": None},
    "contexte_procedural": {"note": None}
}

prompt = f"""Voici un document a analyser. Extrait toutes les informations factuelles
disponibles et complete le schema JSON ci-dessous.

URL source : non fournie

DOCUMENT :
---
{TEXTE}
---

SCHEMA A COMPLETER (reponds uniquement avec le JSON rempli) :
{json.dumps(TEMPLATE, ensure_ascii=False, indent=2)}"""

SYSTEM = """Tu es un agent d extraction de donnees factuelles.
Tu reponds UNIQUEMENT avec du JSON valide, sans markdown ni explication."""

messages = [{"role": "user", "content": prompt}]

for turn in range(10):
    r = c.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM,
        tools=tools,
        messages=messages,
    )
    blocs = [(b.type, repr(getattr(b, "text", "")[:80])) for b in r.content]
    print(f"Tour {turn}: stop_reason={r.stop_reason}")
    for b_type, b_text in blocs:
        print(f"  bloc type={b_type} text={b_text}")

    if r.stop_reason == "end_turn":
        raw = "".join(getattr(b, "text", "") for b in r.content)
        print(f"\nFIN — raw vide: {not raw.strip()}")
        print(f"raw: {repr(raw[:300])}")
        break

    if r.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": r.content})
        tool_uses = [b for b in r.content if b.type == "tool_use"]
        print(f"  -> {len(tool_uses)} tool_use(s), renvoi des resultats")
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": ""} for b in tool_uses]
        messages.append({"role": "user", "content": results})
