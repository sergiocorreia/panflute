from __future__ import print_function
from builtins import open

import os
import panflute as pf

current_directory = os.path.dirname(os.path.realpath(__file__))

input_fn = os.path.join(current_directory, '../tests/1/benchmark.json')
output_fn = os.path.join(current_directory, '../tests/1/panflute.json')
output_txt_benchmark = os.path.join(current_directory, '../tests/1/benchmark.txt')
output_txt_panflute = os.path.join(current_directory, '../tests/1/panflute.txt')

def empty_test(element, doc):
    return

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

print('\nApplying trivial filter...')
doc = doc.walk(action=empty_test, doc=doc)
print(' - Done!')

print(' - Dumping JSON...')
with open(output_fn, mode='w', encoding='utf-8') as f:
    pf.dump(doc, f)
    f.write('\n')
print(' - Done!')
print(' - Comparing...')
with open(input_fn, encoding='utf-8') as f:
    input_data = f.read()
with open(output_fn, encoding='utf-8') as f:
    output_data = f.read()
print(' - Are both files the same?')
print('   - Length:', len(input_data) == len(output_data), len(input_data), len(output_data))
print('   - Content:', input_data == output_data)


assert input_data == output_data



print('Testing stringify()')
with open(input_fn, encoding='utf-8') as f:
    doc = pf.load(f)
ans = pf.stringify(doc)
#print(repr(ans).encode('utf-8'))
with open(output_txt_panflute, encoding='utf-8', mode='w') as f:
    f.write(ans)

import pandocfilters, json
with open(input_fn, encoding='utf-8') as f:
    doc = json.load(f)
ans = pandocfilters.stringify(doc)
with open(output_txt_benchmark, encoding='utf-8', mode='w') as f:
    f.write(ans)
