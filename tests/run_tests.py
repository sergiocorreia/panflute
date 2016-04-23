import panflute as pf

input_fn = '../tests/1/benchmark.json'
output_fn = '../tests/1/panflute.json'

def test_filter(element, doc):
	if type(element)==pf.Header:
		return []
	if type(element)==pf.Str:
		element.text = element.text + '!!'
		return element


print('\nLoading JSON...')

with open(input_fn, encoding='utf-8') as f:
	doc = pf.load(f)

print('Dumping JSON...')
with open(output_fn, mode='w', encoding='utf-8') as f:
	pf.dump(doc, f)
	f.write('\n')

print(' - Done!')


print('\nComparing...')

with open(input_fn, encoding='utf-8') as f:
	input_data = f.read()

with open(output_fn, encoding='utf-8') as f:
	output_data = f.read()

print('Are both files the same?')
print(' - Length:', len(input_data) == len(output_data), len(input_data), len(output_data))
print(' - Content:', input_data == output_data)

print('\nApplying filter...')
doc.items = pf.walk(element=doc.items, action=test_filter, doc=doc)
print(' - Done!')


print('Dumping JSON...')
with open(output_fn, mode='w', encoding='utf-8') as f:
	pf.dump(doc, f)
	f.write('\n')