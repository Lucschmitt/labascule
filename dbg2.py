from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

c = Anthropic()
tools = [{"type": "web_search_20250305", "name": "web_search"}]
messages = [{"role": "user", "content": "Reponds uniquement avec ce JSON sans markdown: {\"test\": true}"}]

for turn in range(5):
    r = c.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        tools=tools,
        messages=messages,
    )
    blocs = [(b.type, repr(getattr(b, "text", "")[:60])) for b in r.content]
    print(f"Tour {turn}: stop_reason={r.stop_reason}, blocs={blocs}")

    if r.stop_reason == "end_turn":
        raw = "".join(getattr(b, "text", "") for b in r.content)
        print("FIN — raw:", repr(raw[:200]))
        break

    if r.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": r.content})
        tool_uses = [b for b in r.content if b.type == "tool_use"]
        print(f"  tool_use blocs: {len(tool_uses)}")
        if tool_uses:
            results = [{"type": "tool_result", "tool_use_id": b.id, "content": ""} for b in tool_uses]
            messages.append({"role": "user", "content": results})
        else:
            print("  AUCUN tool_use — sortie")
            break
