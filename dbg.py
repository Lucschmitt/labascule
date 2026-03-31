from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

c = Anthropic()
prompt = "Reponds avec ce JSON exact sans rien dautre: {\"source\": {\"type\": \"test\"}}"

r = c.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": prompt}]
)

print("stop_reason:", r.stop_reason)
print("nb blocs:", len(r.content))
for i, b in enumerate(r.content):
    text = getattr(b, "text", None)
    print(f"bloc[{i}] type={b.type} text={repr(text[:100]) if text else 'None'}")

raw = "".join(getattr(b, "text", "") for b in r.content)
print("raw vide:", not raw.strip())
print("raw:", repr(raw[:300]))
