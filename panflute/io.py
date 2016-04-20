"""
Serialize JSON dump into AST and vice versa

For the Pandoc element definitions, see:
- Readable format:
  https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html
- Recent updates:
  https://github.com/jgm/pandoc-types/commits/master/Text/Pandoc/Definition.hs
"""
# ---------------------------
# Imports
# ---------------------------

import io
import sys
import json

from .elements import from_json


# ---------------------------
# Functions
# ---------------------------

def split_metadata(doc):
    if len(doc) == 1:
        return {}, doc

    old_meta, doc = doc
    old_meta = old_meta['unMeta']
    meta = {}
    for k, v in old_meta.items():
        meta[k] = walk_meta(v)
    return meta, doc

def walk_meta(element):
    t = element['t']
    c = element['c']

    if t == 'MetaList':
        return [walk_meta(item) for item in c]
    elif t == 'MetaMap':
        return {k: walk_meta(v) for k, v in c.items()}
    elif t == 'MetaInlines':
        return c  # stringify(c)
    elif t == 'MetaBool':
        assert c in {'true', 'false'}
        return c == 'true'
    elif t == 'MetaBlocks':
        return c
    else:
        raise Exception(t, c)







def load():
    input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    doc = json.load(input_stream, object_hook=from_json)
    output_format = sys.argv[1] if len(sys.argv) > 1 else ""
    return doc, output_format


def to_element(json_doc):
    return None  # Element(json_doc)


def dumper(obj):
    try:
        return obj.to_json()
    except:
        print(obj)
    # except AttributeError:
    #    return obj.__dict__


def dump(doc):
    json.dump(doc, sys.stdout, default=dumper)  # , indent=2)


if __name__ == '__main__':
    pass

    # p1 = Para(Str('a'), Space, Str('b'))
    # print(type(p1))
    # print(list(el.tag for el in p1.items))

    row1 = [Plain(Str('a'), Space, Str('b'))]
    row2 = [Plain(Str("c"))]
    bl = OrderedList(row1, row2, start=3, delimiter='OneParen')

    print(bl.to_json())

    # Build AST from stdin
    # doc, fmt = load()
    # print(doc)
    # json_doc = [block.dump() for block in doc]

    # Manipulate the AST
    # ...

    # Dump the AST into stdout
    # dump(doc)
