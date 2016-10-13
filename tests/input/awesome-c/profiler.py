import cProfile
import timeit
import panflute as pf


def empty_test(element, doc):
    return

def test_filter(element, doc):
    if type(element)==pf.Header:
        return []
    if type(element)==pf.Str:
        element.text = element.text + '!!'
        return element


def run():
    print('\nLoading JSON...')
    input_fn = 'benchmark.json'
    output_fn = 'panflute.json'

    with open(input_fn, encoding='utf-8') as f:
        doc = pf.load(f)

    print('\nApplying trivial filter...')
    doc = doc.walk(action=empty_test, doc=doc)

    print('Dumping JSON...')
    with open(output_fn, mode='w', encoding='utf-8') as f:
        pf.dump(doc, f)
        f.write('\n')

    print(' - Done!')


if __name__ == "__main__":
    #cProfile.run('run()')
    t = timeit.repeat('run()', setup="from __main__ import run",
                      number=1, repeat=3)

    print('Times:')
    print(t)
    print('minimum:')
    print(min(t))
