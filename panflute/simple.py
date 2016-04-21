import json
#from elements import from_json, to_json
from elements import *

input_fn = '../tests/pandoc_benchmark.json'
output_fn = '../tests/pandoc_panflute.json'

with open(input_fn, encoding='utf-8') as f:
	data = f.read()

print(len(data))

doc = json.loads(data, object_pairs_hook=from_json)

print('xxxx')
print(doc[1][1])
print('xxxx')


x = doc[1][1]
y = to_json(x)
#print(y)

#x = to_json(Str('Gruber’s'))
#x = json.dumps(x) + '\n'
#x = x.encode('utf-8')
#with open('../tests/pandoc_panflute.json', mode='w', encoding='utf-8') as f:
#	f.write(x)
#
#assert 0

# Use compact separators, like Pandoc
json_doc = json.dumps(doc, default=to_json,
                      separators=(',', ':'), ensure_ascii=False)

with open(output_fn, mode='w', encoding='utf-8') as f:
	f.write(json_doc + '\n')

print('Done!')

print('\nComparing...')

with open(input_fn, encoding='utf-8') as f:
	input_data = f.read()

with open(output_fn, encoding='utf-8') as f:
	output_data = f.read()

print('Are both files the same?')
print(' - Ans:', input_data == output_data)