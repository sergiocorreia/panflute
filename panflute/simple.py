import json
from elements import from_json, to_json

with open('../tests/pandoc.json', encoding='utf-8') as f:
	data = f.read()

print(len(data))
print(data[:100])
print()
print()

doc = json.loads(data, object_hook=from_json)

print('xxxx')
print(doc[1][1])
print('xxxx')


x = doc[1][1]
y = to_json(x)
#print(y)


json_doc = json.dumps(doc, default=to_json)

with open('../tests/output_pandoc.json', mode='w', encoding='utf-8') as f:
	f.write(json_doc)

print('Done!')