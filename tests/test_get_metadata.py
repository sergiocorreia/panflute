import panflute as pf


def test():
    # chcp 65001 --> might be required if running from cmd on Windows

    print('\nLoading JSON...')
    fn = "./tests/input/heavy_metadata/benchmark.json"

    with open(fn, encoding='utf-8') as f:
        doc = pf.load(f)

    meta = doc.get_metadata('title')
    assert meta == "Lorem Ipsum: Title"

    meta = doc.get_metadata('title', builtin=False)
    assert type(meta) == pf.MetaInlines

    # foobar key doesn't exist
    meta = doc.get_metadata('foobar', True)
    assert meta == True

    meta = doc.get_metadata('foobar', 123)
    assert meta == 123

    meta = doc.get_metadata('abstract')
    assert meta.startswith('Bring to the table win-win')

    meta = doc.get_metadata('key1.key1-1')
    assert meta == ['value1-1-1', 'value1-1-2']

    meta = doc.get_metadata('amsthm.plain')
    assert type(meta) == list
    assert meta[0]['Theorem'] == 'Lemma'

    print('--')
    meta = doc.get_metadata('')
    assert len(meta) > 10

    print('\nDone...')

if __name__ == "__main__":
    test()
