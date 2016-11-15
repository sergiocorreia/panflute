# To create the JSON file, run
# pandoc --smart --parse-raw --to=json fenced/input.md > fenced/input.json

import panflute as pf
import pandocfilters, json


def fenced_action(options, data, element, doc):
    bar = options.get('foo')
    assert bar is None or bar == 'bar'
    assert not data or data == 'raw text' or \
        data == """raw1\nraw2\nthis\n...\nis\n...\nall raw"""
    # assert bar or data, (bar,data)
    return


def empty_filter(element, doc):
    return


def test_all():
    input_fn = './tests/fenced/input.json'
    output_fn = './tests/fenced/output.json'

    # Test fenced filter

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
    pf.run_filter(empty_filter, doc=doc)
    print(' - Done!')
    dump_and_compare(doc, input_fn, output_fn)

    print('\nApplying YAML filter...')
    pf.run_filter(pf.yaml_filter, tag='spam', function=fenced_action, doc=doc)
    print(' - Done!')
    dump_and_compare(doc, input_fn, output_fn)

    print('\nApplying Strict YAML filter...')
    pf.run_filter(pf.yaml_filter, tag='eggs', function=fenced_action, doc=doc, strict_yaml=True)
    print(' - Done!')
    dump_and_compare(doc, input_fn, output_fn)


def dump_and_compare(doc, input_fn, output_fn):
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


if __name__ == "__main__":
    test_all()
