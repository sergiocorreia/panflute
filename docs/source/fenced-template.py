"""
Pandoc filter using panflute, for fenced code blocks
"""

import panflute as pf


def prepare(doc):
    pass


def fenced_action(options, data, element, doc):
    if doc.format == 'latex':
        pass
        # return None -> element unchanged
        # return [] -> delete element


def finalize(doc):
    pass


if __name__ == '__main__':
    pf.toJSONFilter(pf.yaml_filter, prepare=prepare, finalize=finalize, tag='sometag', function=fenced_action)
    # tags = {'sometag': fenced_action, 'another_tag': another_action}
    # pf.toJSONFilter(pf.yaml_filter, prepare, finalize, tags=tags)
