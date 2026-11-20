"""
A filter written the way a panflute user would write one, with assertions on
the types that panflute exposes.

This file is type-checked by mypy (see [tool.mypy] in pyproject.toml, and the
lint job in CI) to catch regressions in the *user-visible* types of panflute.
It is not collected by pytest, but it is valid at runtime as well.

- ``assert_type(expr, T)`` fails the type check unless ``expr`` has type ``T``.
- Lines that must be *rejected* by the type checker end with a
  ``# type: ignore[code]`` comment; as ``warn_unused_ignores`` is on, the check
  fails if one of them stops being an error.
"""

from __future__ import annotations

import io
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any, Literal

import panflute as pf

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:
    def assert_type(value, typ):
        return value


# ---------------------------
# Actions
# ---------------------------

def action(elem: pf.Element, doc: pf.Doc) -> pf.Element | list[pf.Element] | None:
    if isinstance(elem, pf.Str):
        assert_type(elem.text, str)
        if elem.text == 'delete-me':
            return []
        return pf.Emph(pf.Str(elem.text.upper()))
    elif isinstance(elem, pf.Header):
        assert_type(elem.level, int)
        assert_type(elem.identifier, str)
        assert_type(elem.classes, list[str])
        assert_type(elem.attributes, dict[str, str])
        assert_type(elem.content, pf.ListContainer)
        assert_type(elem.content[0], pf.Element)
        assert_type(elem.content[1:], pf.ListContainer)
        elem.content.append(pf.Space())
        elem.content = [pf.Str('New'), pf.Space(), pf.Str('title')]
        elem.content[0:1] = [pf.Str('A'), pf.Space(), pf.Str('new')]
    elif isinstance(elem, pf.CodeBlock) and 'hidden' in elem.classes:
        return [pf.Para(pf.Str(elem.text)), pf.HorizontalRule()]
    elif isinstance(elem, pf.Math):
        assert_type(elem.format, Literal['DisplayMath', 'InlineMath'])
    elif isinstance(elem, pf.Link):
        assert_type(elem.url, str)
        assert_type(elem.title, str)
    elif isinstance(elem, pf.Table):
        assert_type(elem.head, pf.TableHead)
        assert_type(elem.caption, pf.Caption)
        assert_type(elem.cols, int)
    return None


def no_op(elem: pf.Element, doc: pf.Doc) -> None:
    pass


def prepare(doc: pf.Doc) -> None:
    doc.counter = 0  # Filters can add their own attributes to the Doc
    assert_type(doc.format, str)
    assert_type(doc.metadata, pf.MetaMap)
    assert_type(doc.content, pf.ListContainer)
    assert_type(doc.get_metadata('title', default=''), Any)


def finalize(doc: pf.Doc) -> None:
    doc.metadata['counter'] = doc.counter
    doc.metadata['list'] = ['a', 1, True]


# ---------------------------
# Navigation
# ---------------------------

def navigation(elem: pf.Element) -> None:
    assert_type(elem.tag, str)
    assert_type(elem.parent, pf.Element | None)
    assert_type(elem.index_in_parent, int | None)
    assert_type(elem.index, int | None)  # (alias of .index_in_parent)
    elem.index = 0
    assert_type(elem.location, str | None)
    assert_type(elem.next, pf.Element | None)
    assert_type(elem.prev, pf.Element | None)
    assert_type(elem.offset(2), pf.Element | None)
    assert_type(elem.ancestor(2), pf.Element | None)
    assert_type(elem.doc, pf.Doc | None)
    assert_type(elem.container, pf.ListContainer | pf.DictContainer | None)
    assert_type(elem.to_json(), Any)


# ---------------------------
# Walking and running filters
# ---------------------------

def walking() -> None:
    doc = pf.Doc(pf.Para(pf.Str('a')), metadata={'title': 'x'}, format='latex')
    assert_type(doc.walk(no_op), pf.Doc)
    assert_type(doc.walk(action), pf.Doc | pf.Element | list[pf.Element])

    para = pf.Para(pf.Str('a'), pf.Space(), pf.Note(pf.Para(pf.Str('b'))))
    assert_type(para.walk(no_op, doc=doc, stop_if=lambda e: isinstance(e, pf.Note)), pf.Para)
    assert_type(para.walk(lambda e, d: None), pf.Para)
    assert_type(doc.replace_keyword('a', pf.Str('b')), pf.Element)


def main(doc: pf.Doc | None = None) -> pf.Doc | None:
    return pf.run_filters([action, no_op], prepare=prepare, finalize=finalize, doc=doc)


def main_with_kwargs(doc: pf.Doc | None = None) -> pf.Doc | None:
    def fenced(options: dict[str, Any], data: str, element: pf.Element, doc: pf.Doc) -> None:
        pass
    return pf.run_filter(pf.yaml_filter, tag='foo', function=fenced, doc=doc)


# ---------------------------
# Loading and dumping
# ---------------------------

def load_and_dump(raw: str) -> str:
    doc = pf.load(io.StringIO(raw))
    assert_type(doc, pf.Doc)
    with io.StringIO() as f:
        pf.dump(doc, f)
        return f.getvalue()


# ---------------------------
# Tools
# ---------------------------

def tools(doc: pf.Doc) -> None:
    assert_type(pf.stringify(doc), str)
    assert_type(pf.stringify(doc.content), str)
    assert_type(pf.convert_text('*a*'), list[pf.Element])
    assert_type(pf.convert_text('*a*', standalone=True), pf.Doc)
    assert_type(pf.convert_text('*a*', 'markdown', 'panflute', True), pf.Doc)
    assert_type(pf.convert_text(pf.Str('a'), input_format='panflute', output_format='latex'), Any)
    assert_type(pf.run_pandoc('*a*', ['--to=html']), str)
    assert_type(pf.shell('echo a'), bytes | None)
    assert_type(pf.get_option({'name': 'x'}, 'name', doc, 'style.name'), Any)
    pf.debug('message', 1, None)


# ---------------------------
# Elements and metadata
# ---------------------------

def elements() -> None:
    pf.Header(pf.Str('Title'), level=2, identifier='id', classes=['a'], attributes={'k': 'v'})
    pf.Div(pf.Para(pf.Str('a')), classes=('a', 'b'), attributes={'k': 'v'})
    pf.Quoted(pf.Str('a'), quote_type='SingleQuote')
    pf.OrderedList(pf.ListItem(pf.Plain(pf.Str('a'))), style='LowerRoman', delimiter='OneParen')
    pf.Cite(pf.Str('@a'), citations=[pf.Citation('a', mode='AuthorInText')])
    pf.TableCell(pf.Plain(pf.Str('a')), alignment='AlignLeft', colspan=2)
    pf.Table(pf.TableBody(pf.TableRow(pf.TableCell())), colspec=[('AlignLeft', 0.5)])


def metadata() -> None:
    ml = pf.MetaList('a', 1, True, pf.MetaString('b'))
    assert_type(ml[0], pf.MetaValue)
    assert_type(ml[1:], MutableSequence[pf.MetaValue])
    assert_type(ml.index_in_parent, int | None)  # The index of ml in its container
    assert_type(ml.index(pf.MetaString('b')), int)  # The sequence method (see #258)
    assert_type(ml.index(pf.MetaString('b'), 1, -1), int)
    ml.remove(pf.MetaString('b'))
    ml.append('c')
    ml.extend([pf.MetaBool(False), 'd'])
    ml[0] = {'key': 'value'}
    ml[0:1] = ['x', True]
    del ml[1:]

    mm = pf.MetaMap(('a', 'b'), c=True)
    assert_type(mm['a'], pf.MetaValue)
    assert_type(mm.content, pf.DictContainer)
    mm['d'] = [1, 2]
    mm.content = {'e': pf.MetaString('f')}
    mm.content = [('g', pf.MetaBool(True))]
    for key in mm:
        assert_type(key, str)


# ---------------------------
# Mistakes that the type checker must catch (these would fail at runtime)
# ---------------------------

def rejected(doc: pf.Doc) -> None:
    def one_argument(elem: pf.Element) -> None:
        pass

    doc.walk(one_argument)  # type: ignore[arg-type]
    pf.Para(pf.Para())  # type: ignore[arg-type]
    pf.Str(1)  # type: ignore[arg-type]
    pf.Quoted(pf.Str('a'), quote_type='Single')  # type: ignore[arg-type]
    pf.Header(pf.Str('a'), level='2')  # type: ignore[arg-type]
    pf.dump([pf.Para()])  # type: ignore[arg-type]
    doc.format = 1  # type: ignore[assignment]
    doc.metadata = 1  # type: ignore[assignment]
    pf.Str('a').text = None  # type: ignore[assignment]

