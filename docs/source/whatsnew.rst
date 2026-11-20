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
installing panflute 2.3.1. As before, pandoc 2.11 or later is required (the
oldest version tested is 2.11.4): older versions use an older format for
documents, and panflute stops with an "invalid api version" error.

``MetaList.index`` is now a method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every element has a ``.position`` attribute: its position in the list that
holds it. On most elements, ``.index`` remains an alias of it, so filters
that read or assign ``elem.index`` work as before.

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

Beware that ``if metalist.index is not None:`` no longer fails, but is
always true.

Pickles of a :class:`.MetaList`, or of anything that contains one (such as
a :class:`.Doc` whose metadata has a list), made with panflute 2.x cannot be
loaded with 3.0. Store documents as pandoc JSON (:func:`.dump` and
:func:`.load`) to keep them across versions.

Slices of a list of elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``elem.content[1:3]`` still returns a new container that holds the same
elements, but it is now an instance of a private subclass of
:class:`.ListContainer`. Code that checks ``type(s) is ListContainer``
should use ``isinstance(s, ListContainer)`` instead, or convert the slice
with ``list(s)``.

Reading a slice no longer changes the ``.parent`` or ``.position`` of the
elements in it: they keep referring to the original list.

Table cells
~~~~~~~~~~~

:class:`.TableCell` requires integer ``rowspan`` and ``colspan``; a float
now raises ``TypeError`` (it used to be written into the document, which
pandoc then rejected). Use ``int(...)`` if you compute them.

Smaller differences
~~~~~~~~~~~~~~~~~~~

These only matter in unusual situations:

- ``import panflute`` no longer imports ``click`` or ``yaml``; they are
  imported when first needed. A missing or broken installation of them is
  therefore reported later, for instance when calling :func:`.yaml_filter`.
- :func:`.dump`, when writing to stdout, no longer replaces ``sys.stdout``
  with a UTF-8 writer, so anything printed to stdout *after* :func:`.dump`
  uses the encoding of the console. (A filter should not print to stdout
  anyway: pandoc reads the document from it. Use :func:`.debug` instead,
  which prints to stderr.)
- With ``strict_yaml=True``, :func:`.yaml_filter` no longer raises an
  exception for YAML that is not a mapping (``key: value`` pairs) or that
  cannot be parsed: it prints a warning and leaves the code block unchanged.
- An element's ``.parent`` is now set when it is added to another element,
  not only when it is read back from it. Code that relied on ``.parent``
  being ``None`` for an element that had just been added will see the parent.
- The "invalid api version" error has a new, more helpful message, and its
  ``args`` are that message.

Type checking your filters
**************************

If your filters are type-checked, they will now be checked against
panflute's own type hints. If you installed a separate stub package for
panflute (such as ``panflute-stubs``), uninstall it, as type checkers would
use it instead of the hints shipped with panflute. See :ref:`type-hints`
for how to annotate an action, and for the few places where the types are
deliberately simplified.
