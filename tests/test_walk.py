"""
Test how Element.walk() behaves with different return types of action functions
"""

import panflute as pf


def compare_docs(doc_a, doc_b):
    doc_a_json = pf.convert_text(doc_a,
                                 input_format='panflute',
                                 output_format='json',
                                 standalone=True)
    doc_b_json = pf.convert_text(doc_b,
                                 input_format='panflute',
                                 output_format='json',
                                 standalone=True)
    return doc_a_json == doc_b_json


"""
Action functions to use in testing
"""


# Action that always returns None, changing nothing
def do_nothing(elem, doc):
    return None


# Action that returns an empty list, deleting pf.Str elements
def remove_elem(elem, doc):
    if isinstance(elem, pf.Str):
        return []


# Action that returns a single inline element, writing over pf.Str elements
def inline_replace_elem(elem, doc):
    if isinstance(elem, pf.Str):
        return pf.Str("b")


# Action that returns a list of inline elements, writing over pf.Str elements
def inline_replace_list(elem, doc):
    if isinstance(elem, pf.Str):
        return [pf.Str("a"), pf.Space, pf.Str("b")]


# Action that returns a single inline element, writing over pf.Para elements
def block_replace_elem(elem, doc):
    if isinstance(elem, pf.Para):
        return pf.CodeBlock("b")


# Action that returns a list of block elements, writing over pf.Para elements
def block_replace_list(elem, doc):
    if isinstance(elem, pf.Para):
        return [pf.Para(pf.Str("a")), pf.Para(pf.Str("b"))]


"""
Test functions for above action functions
"""


def test_none():
    in_doc = expected_doc = pf.Doc(pf.Para(pf.Str("a")))
    in_doc.walk(do_nothing)
    assert compare_docs(in_doc, expected_doc)


def test_empty_list():
    in_doc = pf.Doc(pf.Para(pf.Str("a"), pf.Space))
    in_doc.walk(remove_elem)
    expected_doc = pf.Doc(pf.Para(pf.Space))
    assert compare_docs(in_doc, expected_doc)

def test_inline_elem():
    in_doc = pf.Doc(pf.Para(pf.Str("a")))
    in_doc.walk(inline_replace_elem)
    expected_doc = pf.Doc(pf.Para(pf.Str("b")))
    assert compare_docs(in_doc, expected_doc)

def test_inline_list():
    in_doc = pf.Doc(pf.Para(pf.Str("a")))
    in_doc.walk(inline_replace_list)
    expected_doc = pf.Doc(pf.Para(pf.Str("a"), pf.Space, pf.Str("b")))
    assert compare_docs(in_doc, expected_doc)


def test_block_elem():
    in_doc = pf.Doc(pf.Para(pf.Str("a")))
    in_doc.walk(block_replace_elem)
    expected_doc = pf.Doc(pf.CodeBlock("b"))
    assert compare_docs(in_doc, expected_doc)


def test_block_list():
    in_doc = pf.Doc(pf.Para(pf.Str("c")))
    in_doc.walk(block_replace_list)
    expected_doc = pf.Doc(pf.Para(pf.Str("a")), pf.Para(pf.Str("b")))
    assert compare_docs(in_doc, expected_doc)
