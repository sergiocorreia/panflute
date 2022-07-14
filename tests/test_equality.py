import panflute as pf

text = '''---
title: my title
author: Bob
---

# SomeHeader
 
Some text
'''

def test_equality():
    doc1 = pf.convert_text(text, standalone=True)
    doc2 = pf.convert_text(text, standalone=True)
    doc3 = pf.convert_text(text, standalone=True)

    assert doc1 == doc2
    assert doc1 == doc2 == doc3

    doc2.content[0].content[0].text = 'Changed'
    assert doc1 != doc2
    assert doc2 != doc3
    assert doc1 == doc3

    doc3.metadata['author'] = pf.MetaInlines(pf.Str('John'))
    assert doc1 != doc3
    doc3.metadata['author'] = pf.MetaInlines(pf.Str('Bob'))
    assert doc1 == doc3

    assert doc1.content != doc2.content
    assert doc1.content == doc3.content


if __name__ == "__main__":
    test_equality()
