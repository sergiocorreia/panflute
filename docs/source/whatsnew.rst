What's new in 3.0
=================

Panflute 3.0 is the first release since 2.3.1. It requires **Python 3.10 or
later**, and supports pandoc 2.11.4 to 3.14. The highlights are:

- **Type hints**: panflute is fully annotated, so type checkers and IDEs
  can check filters and complete the attributes of elements (see
  :ref:`type-hints`).
- **Any raw format**: :class:`.RawBlock` and :class:`.RawInline` accept any
  format, as pandoc does (``typst``, ``comment``, Quarto's ``latex-merge``,
  custom writers, ...). Documents with such raw elements could not be
  loaded before.
- **Reliable navigation**: ``.parent`` is set as soon as an element is added
  to another one, and ``.position`` (the new name of ``.index``), ``.next``,
  ``.prev`` and ``.offset()`` stay correct after insertions and deletions
  (see :ref:`navigation`).
- **Faster filters**: ``import panflute`` takes about a quarter of the time
  it took, and walking a document about 40% less, so a simple filter on a
  small document runs in less than half the time.
- **Many bug fixes**, for instance ``convert_text()`` no longer modifies
  the ``extra_args`` list it is given, and ``panfl --no-sys-path`` works
  again with recent versions of click.

Most filters run unchanged. The rest of this page lists what can require
changes; the :doc:`changelog` lists every change.

Upgrading from panflute 2.x
***************************

Python and pandoc versions
~~~~~~~~~~~~~~~~~~~~~~~~~~

Panflute 3.0 requires Python 3.10 or later. On older Pythons, pip keeps
installing panflute 2.3.1 (a project that must keep working there can
require ``panflute<3`` for those Pythons). As before, pandoc 2.11 or later is required (the
oldest version tested is 2.11.4): older versions use an older format for
documents, and panflute stops with an "invalid api version" error.

``MetaList.index`` is now a method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every element has a ``.position`` attribute: its position in the list that
holds it, or ``None`` when it is not in a list (e.g. the caption of a table,
or a value of a :class:`.MetaMap`). On every element except
:class:`.MetaList`, ``.index`` remains an alias of it, so filters that read
or assign ``elem.index`` work as before.

The exception is :class:`.MetaList`, which is a list-like object: there,
``index()`` is now the standard list method, as is ``remove()``
(they raised ``TypeError`` in 2.x). If your filter uses the position of a
:class:`.MetaList`, use ``.position`` instead:

.. code-block:: python

    # panflute 2.x
    if metalist.index == 0:
        ...

    # panflute 3.0 (works for every element)
    if metalist.position == 0:
        ...

    # and now this works as for a list:
    metalist.index(MetaString('value'))

Beware that ``if metalist.index is not None:`` raises no error, but is now
always true (it is a method), and that assigning to ``metalist.index``
raises ``AttributeError``.

Pickles of a :class:`.MetaList`, or of anything that contains one (such as
a :class:`.Doc` whose metadata has a list), made with panflute 2.x cannot be
loaded with 3.0 (``AttributeError``); other pickled elements still load.
Re-create such pickles with 3.0, or store documents as pandoc JSON
(:func:`.dump` and :func:`.load`), which does not depend on the panflute version.

Slices of a list of elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``elem.content[1:3]`` still returns a new container that holds the same
elements, but it is now an instance of a private subclass of
:class:`.ListContainer`. Code that checks ``type(s) is ListContainer``
should use ``isinstance(s, ListContainer)`` instead, or convert the slice
with ``list(s)``.

Reading, iterating or changing a slice no longer changes the ``.parent`` or
``.position`` of the elements in it (reading it used to re-index them
relative to the slice): they keep referring to the original list.

Table cells
~~~~~~~~~~~

:class:`.TableCell` requires integer ``rowspan`` and ``colspan``; anything
else, such as a float, now raises ``TypeError`` (it used to be written into the document, which
pandoc then rejected). Use ``int(...)`` if you compute them.

Smaller differences
~~~~~~~~~~~~~~~~~~~

These only matter in unusual situations:

- ``import panflute`` no longer imports ``click``, ``yaml`` (and
  ``yamlloader``) or ``panflute.autofilter``; they are imported when first
  needed. A missing or broken installation of them is therefore reported
  later, for instance when calling :func:`.yaml_filter`. ``from panflute import *``
  still imports click, so ``import panflute as pf`` starts faster.
- :func:`.dump`, when writing to stdout, no longer replaces ``sys.stdout``
  with a UTF-8 writer (it writes UTF-8 bytes to ``sys.stdout.buffer``), so
  anything printed to stdout *after* :func:`.dump` uses the encoding of
  ``sys.stdout``. Likewise, :func:`.load` no longer closes ``sys.stdin.buffer``. (A filter should not print to stdout
  anyway: pandoc reads the document from it. Use :func:`.debug` instead,
  which prints to stderr.)
- With ``strict_yaml=True``, :func:`.yaml_filter` no longer raises an
  exception for YAML that is not a mapping (``key: value`` pairs) or that
  cannot be parsed: it prints a warning to stderr and leaves the code block
  unchanged. A block with only comments counts as no options.
- An element's ``.parent`` is now set when it is added to another element,
  not only when it is read back from it. Code that relied on ``.parent``
  being ``None`` for an element that had just been added will see the parent.
- The "invalid api version" ``TypeError`` has a new, more helpful message
  (still starting with "invalid api version"); its ``args`` are now just that
  message, instead of ``('invalid api version', [1, 20])``.

Type checking your filters
**************************

If your filters are type-checked, they will now be checked against
panflute's own type hints. If you installed a separate stub package for
panflute (such as ``panflute-stubs``), uninstall it, as type checkers would
use it instead of the hints shipped with panflute. Type-checked filters may
see new errors where the hints are strict, for instance an element class
passed instead of an instance (``Para(Space)``), or a misspelled value of an
argument such as ``quote_type``. See :ref:`type-hints`
for how to annotate an action, and for the few places where the types are
deliberately simplified.
