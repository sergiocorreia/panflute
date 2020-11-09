"""
Pandoc filter using panflute
"""

import panflute as pf


def prepare(doc):
    pf.debug(f'  Pandoc version: {doc.pandoc_version}')
    pf.debug('  Pandoc reader options:')
    for k, v in doc.pandoc_reader_options.items():
        pf.debug(f'    {k}={v}')

    assert doc.pandoc_version >= (2, 11, 0)
    assert doc.pandoc_reader_options['readerStandalone'] is False


def action(elem, doc):
    if isinstance(elem, pf.Element) and doc.format == 'latex':
        pass
        # return None -> element unchanged
        # return [] -> delete element


def finalize(doc):
    pass


def main(doc=None):
    return pf.run_filters([action],
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc) 


if __name__ == '__main__':
    main()
