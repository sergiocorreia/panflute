Panflute API
============

.. contents:: Contents:
   :local:


Base elements
****************

.. autoclass:: panflute.base.Element

   .. attribute:: parent
      
      Element that contains the current one.

      **Note:** the ``.parent`` and related
      attributes are not implemented for metadata elements.


      :rtype: :class:`Element` | ``None``

   .. attribute:: location

     ``None`` unless the element is in a non--standard location of its
     parent, such as the ``.caption`` or ``.header`` attributes of a table.

     In those cases, ``.location`` will be equal to a string.

      :rtype: ``str`` | ``None``

   .. attribute:: position

      Position of the element in the list container that holds it: in
      ``elem.parent.content``, or in another list attribute of the parent
      (such as ``.citations`` of a :class:`.Cite`), so that
      ``elem.container[elem.position] is elem``.
      ``None`` if the element is not in a list container: it has no parent,
      it is the value of a single-element attribute (such as ``.caption``
      of a table), or a value of a :class:`.MetaMap`.

      Kept up to date by the containers: it is set when the element is
      added to a container or read from it (``elem.content[i]``, iterating,
      walking), and updated when elements are inserted or deleted before it.
      :meth:`offset`, :attr:`next` and :attr:`prev` are based on it.

      :rtype: ``int`` | ``None``

   .. automethod:: panflute.base.Element.walk
   .. autoattribute:: panflute.base.Element.content
   .. autoattribute:: panflute.base.Element.index
   .. automethod:: panflute.base.Element.ancestor
   .. automethod:: panflute.base.Element.offset
   .. autoattribute:: panflute.base.Element.prev
   .. autoattribute:: panflute.base.Element.next
   .. automethod:: panflute.base.Element.replace_keyword
   .. autoattribute:: panflute.base.Element.container
   .. autoattribute:: panflute.base.Element.doc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following elements inherit from :class:`.Element`:

.. automodule:: panflute.base
   :members: Block, Inline, MetaValue

Low-level classes
~~~~~~~~~~~~~~~~~~

*(Skip unless you want to understand the internals)*


.. automodule:: panflute.containers
   :members:

.. note::
   To keep track of every element's parent we do some
   class magic. Namely, ``Element.content`` is not a list attribute
   but a property accessed via getter and setters. Why?

       >>> e = Para(Str('Hello'), Space(), Str('World!'))

   This creates a ``Para`` element, which stores the three
   inline elements (Str, Space and Str) inside an ``.content`` attribute.
   If we add ``.parent`` attributes to these elements,
   there are two ways they can be made obsolete:

   1. By replacing or inserting specific elements: ``e.content[0] = Str('Bye')``
   2. By replacing the entire list: ``e.content = other_items``

   We deal with the first problem by wrapping the list of items
   with a ListContainer class of type :class:`collections.abc.MutableSequence`.
   This class sets the ``.parent``, ``.location`` and ``.position`` attributes
   of the elements added to it, and updates the ``.position`` of the
   elements that move when others are inserted or deleted.

   For the second problem, we use setters and getters which update the
   ``.parent`` attribute.

   A slice of a ListContainer (``e.content[0:2]``) is a new container,
   an instance of a private subclass of ListContainer, which holds the same
   elements but does not change their ``.parent`` or ``.position``.


Standard elements
********************************************

These are the standard Pandoc elements, as described `here <https://hackage.haskell.org/package/pandoc-types/docs/Text-Pandoc-Definition.html>`_. Consult the `repo <https://github.com/jgm/pandoc-types/commits/master/src/Text/Pandoc/Definition.hs>`_ for the latest updates.

.. note::
   The attributes of every element object will be
   i) the parameters listed below, plus
   ii) the attributes of :class:`.Element`.
   Example:

       >>> h = Str(text='something')
       >>> h.text
       'something'
       >>> hasattr(h, 'parent')
       True

   **Exception:** the ``.content`` attribute only exists
   in elements that take ``*args``
   (so we can do ``Para().content`` but not ``Str().content``).

.. autoclass:: panflute.elements.Doc
   :members:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: panflute.elements
   :members:
   :exclude-members: Doc

Table-specific elements
********************************************

.. automodule:: panflute.table_elements
   :members:


Standard functions
********************************************

.. currentmodule:: panflute.io

.. autosummary::

   run_filters
   run_filter
   toJSONFilter
   toJSONFilters
   load
   dump

.. currentmodule:: panflute.base

.. seealso::
   The ``walk()`` function has been replaced by the :meth:`.Element.walk`
   method of each element. To walk through the entire document,
   do ``altered = doc.walk(action)``.

.. automodule:: panflute.io
   :members:

.. note::
   The *action* functions have a few rules:

   - They are called as ``action(element, doc)`` so they must accept at
     least two arguments. (With type hints, annotate them as
     ``def action(elem: Element, doc: Doc) -> Element | list[Element] | None``.)
   - Additional arguments can be passed through the ``**kwargs**`` of
     ``toJSONFilter`` and ``toJSONFilters``.
   - They can return either an element, a list, or ``None``.
   - If they return ``None``, the document will keep the same element
     as before (although it might have been modified).
   - If they return another element, it will take the place of the
     received element.
   - If they return ``[]`` (an empty list), they will be deleted from the
     document. Note that you can delete a row from a table or an item from
     a list, but you cannot delete the caption from a table (you can
     make it empty though).
   - If the received element is a block or inline element, they may return
     a list of elements of the same base class, which will take the place
     of the received element.

"Batteries included" functions
******************************

These are functions commonly used when writing more complex filters

.. currentmodule:: panflute.tools

.. autosummary::

   stringify
   convert_text
   yaml_filter
   shell
   run_pandoc
   get_option

.. currentmodule:: panflute.utils

.. autosummary::

   debug

See also :meth:`.Doc.get_metadata` and :meth:`.Element.replace_keyword`

.. automodule:: panflute.tools
   :members:

.. autofunction:: panflute.utils.debug


Command line interfaces
******************************

Installing panflute installs two programs, ``panflute`` and ``panfl``,
which run the filters listed in a document's metadata, or given on the
command line (see :ref:`the guide <running-filters-automatically>`).
``panflute --help`` and ``panfl --help`` describe them.
They are implemented in ``panflute.autofilter``, which is only imported
when one of these functions is first used.

.. autofunction:: panflute.autofilter.main
.. autofunction:: panflute.autofilter.stdio
.. autofunction:: panflute.autofilter.get_filter_dirs
