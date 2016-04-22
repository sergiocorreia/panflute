import panflute

input_fn = '../tests/1/benchmark.json'
output_fn = '../tests/2/panflute.json'


with open(input_fn, encoding='utf-8') as f:
	doc = panflute.load(f)

with open(output_fn, mode='w', encoding='utf-8') as f:
	panflute.dump(doc, f)
	f.write('\n')

print('Done!')

print('\nComparing...')

with open(input_fn, encoding='utf-8') as f:
	input_data = f.read()

with open(output_fn, encoding='utf-8') as f:
	output_data = f.read()

print('Are both files the same?')
print(' - Ans:', input_data == output_data)
