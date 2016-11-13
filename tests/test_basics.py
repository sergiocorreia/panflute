import panflute as pf
import pandocfilters, json


def test_all():
    fns = [
        ('./tests/1/api117/benchmark.json', './tests/1/api117/panflute.json'),
        ('./tests/1/api118/benchmark.json', './tests/1/api118/panflute.json'),
        ('./tests/2/api117/benchmark.json', './tests/2/api117/panflute.json'),
        ('./tests/2/api118/benchmark.json', './tests/2/api118/panflute.json'),
        ('./tests/3/api117/benchmark.json', './tests/3/api117/panflute.json'),
        ('./tests/3/api118/benchmark.json', './tests/3/api118/panflute.json'),
        ('./tests/4/api117/benchmark.json', './tests/4/api117/panflute.json'),
        ('./tests/4/api118/benchmark.json', './tests/4/api118/panflute.json')]

    for input_fn, output_fn in fns:
        print()
        print('TESTING:', input_fn)
        print(64 * '<')
        inner_test_idempotent(input_fn, output_fn)
        inner_test_stringify(input_fn, output_fn)
        print(64 * '>')
        print()

    print('DONE!')

def empty_test(element, doc):
    return

def inner_test_filter(element, doc):
    if type(element)==pf.Header:
        return []
    if type(element)==pf.Str:
        element.text = element.text + '!!'
        return element

def inner_test_idempotent(input_fn, output_fn):

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

def inner_test_stringify(input_fn, output_fn):

    output_txt_benchmark = './tests/temp_benchmark.txt'
    output_txt_panflute = './tests/temp_panflute.txt'

    print('Testing stringify()')
    with open(input_fn, encoding='utf-8') as f:
        doc = pf.load(f)
    ans = pf.stringify(doc)
    #print(repr(ans).encode('utf-8'))
    with open(output_txt_panflute, encoding='utf-8', mode='w') as f:
        f.write(ans)

    with open(input_fn, encoding='utf-8') as f:
        doc = json.load(f)
    ans = pandocfilters.stringify(doc)
    with open(output_txt_benchmark, encoding='utf-8', mode='w') as f:
        f.write(ans)


if __name__ == "__main__":
    test_all()
