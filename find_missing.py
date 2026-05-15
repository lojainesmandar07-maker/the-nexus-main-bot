import json
with open('data/stories/fu_hunter.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data['nodes']
missing = set()
for node_id, node in nodes.items():
    for choice in node.get('choices', []):
        nxt = choice.get('next')
        if nxt and nxt not in nodes:
            missing.add(nxt)

print("Missing nodes count:", len(missing))
print("Missing nodes:", missing)
