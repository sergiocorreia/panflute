What's new in 3.0
=================

Panflute 3.0 is the first release since 2.3.1. It requires **Python 3.10 or
later** and supports pandoc 2.11.4 to 3.14. Most filters run unchanged;
the exceptions are below, with what to change in them. The :doc:`changelog`
lists every change.

Upgrading from panflute 2.x
***************************

Python and pandoc versions
~~~~~~~~~~~~~~~~~~~~~~~~~~

On Python 3.9 or older, pip keeps installing panflute 2.3.1; a project that
must keep working there can require ``panflute<3`` for those Pythons. As
before, pandoc 2.11 or later is required (the oldest version tested is
2.11.4): older versions write documents in an older format, and panflute
stops with an "invalid api version" error.

``MetaList.index`` is now a method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What 2.x called ``.index``, the index of an element within the list
container that holds it, is now ``.index_in_parent`` on every element. It
is ``None`` when no list container holds the element (the caption of a
table, for instance, or a value of a :class:`.MetaMap`). On every element
except :class:`.MetaList`, ``.index`` remains an alias of it, so filters
that read or assign ``elem.index`` work as before.

A :class:`.MetaList`, a list of metadata values, behaves like a Python
list: ``index()`` is now the standard list method, as is ``remove()`` (in
2.x both raised ``TypeError``). If your filter reads the index of a
:class:`.MetaList` in its container, use ``.index_in_parent``:

.. code-block:: python

    # panflute 2.x
    if metalist.index == 0:
        ...

    # panflute 3.0 (works for every element)
    if metalist.index_in_parent == 0:
        ...

    # and now this works as for a list:
    metalist.index(MetaString('value'))

Beware of two old uses: ``if metalist.index is not None:`` raises no error
but is now always true (``index`` is a method), and assigning to
``metalist.index`` raises ``AttributeError``.

Pickles of a :class:`.MetaList` made with panflute 2.x, or of anything that
contains one (such as a :class:`.Doc` whose metadata has a list), cannot be
loaded with 3.0 (``AttributeError``); other pickled elements still load.
Re-create such pickles with 3.0, or store documents as pandoc JSON
(:func:`.dump` and :func:`.load`), which does not depend on the panflute
version.

Slices of a list container
~~~~~~~~~~~~~~~~~~~~~~~~~~

``elem.content`` is a :class:`.ListContainer`, a list that accepts only
elements of the right type. A slice of it, such as ``elem.content[1:3]``,
is still a new container that holds the same elements, but it is now an
instance of a private subclass of :class:`.ListContainer`. Replace
``type(s) is ListContainer`` with ``isinstance(s, ListContainer)``, or
convert the slice with ``list(s)``.

Reading, iterating or changing a slice no longer changes the ``.parent`` or
``.index_in_parent`` of its elements (reading it used to re-index them
relative to the slice): they keep referring to the original container.

Table cells
~~~~~~~~~~~

:class:`.TableCell` requires integer ``rowspan`` and ``colspan``. Anything
else, such as a float, now raises ``TypeError``; it used to be written into
the document, which pandoc then rejected. Use ``int(...)`` if you compute
them.

Type-checked filters
~~~~~~~~~~~~~~~~~~~~

Type checkers now check your filters against the type hints that ship with
panflute. If you installed a separate stub package for panflute (such as
``panflute-stubs``), uninstall it: type checkers would use it instead.
Where the hints are strict, type-checked filters may see new errors, for
instance for an element class passed instead of an instance
(``Para(Space)``), or for a misspelled value of an argument such as
``quote_type``. :ref:`type-hints` shows how to annotate an action, and
lists the few places where the types are deliberately simplified.

Smaller differences
~~~~~~~~~~~~~~~~~~~

These only matter in unusual situations:

- ``import panflute`` no longer imports ``click``, ``yaml`` (and
  ``yamlloader``) or ``panflute.autofilter``; panflute imports them when it
  first needs them. A missing or broken installation of them is therefore
  reported later, for instance when you call :func:`.yaml_filter`.
  ``from panflute import *`` still imports click, so
  ``import panflute as pf`` starts faster.
- :func:`.dump`, when writing to stdout, no longer replaces ``sys.stdout``
  with a UTF-8 writer (it writes UTF-8 bytes to ``sys.stdout.buffer``), so
  anything printed to stdout *after* :func:`.dump` uses the encoding of
  ``sys.stdout``. Likewise, :func:`.load` no longer closes
  ``sys.stdin.buffer``. (A filter should not print to stdout anyway: pandoc
  reads the document from it. Use :func:`.debug`, which prints to stderr.)
- With ``strict_yaml=True``, :func:`.yaml_filter` no longer raises an
  exception for YAML that cannot be parsed or that is not a mapping
  (``key: value`` pairs): it prints a warning to stderr and leaves the code
  block unchanged. A block with only comments counts as no options.
- An element's ``.parent`` is now set when the element is added to another
  one, not only when it is read back from it. Code that relied on
  ``.parent`` being ``None`` for an element just added will see the parent.
- The "invalid api version" ``TypeError`` has a new, more helpful message,
  which still starts with "invalid api version". Its ``args`` are now just
  that message, instead of ``('invalid api version', [1, 20])``.

What 3.0 adds
*************

- **Type hints**: panflute is fully annotated, so type checkers and IDEs
  can check filters and complete the attributes of elements (see
  :ref:`type-hints`).
- **Any raw format**: :class:`.RawBlock` and :class:`.RawInline` accept any
  format, as pandoc does (``typst``, ``comment``, Quarto's ``latex-merge``,
  custom writers, ...). Documents with such raw elements could not be
  loaded before.
- **Reliable navigation**: ``.parent`` is set as soon as an element is added
  to another one, and ``.index_in_parent``, ``.next``, ``.prev`` and
  ``.offset()`` stay correct after insertions and deletions (see
  :ref:`navigation`).
- **Faster filters**: ``import panflute`` takes about a quarter of the time
  it took, and walking a document about 40% less when the filter changes
  nothing, so a simple filter on a small document runs in less than half the
  time.
- **Bug fixes**: for instance, ``convert_text()`` no longer modifies the
  ``extra_args`` list it is given, and ``panfl --no-sys-path`` works again
  with recent versions of click. The :doc:`changelog` lists them all.
