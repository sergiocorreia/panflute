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

   .. automethod:: panflute.base.Element.walk
   .. autoattribute:: panflute.base.Element.content
   .. autoattribute:: panflute.base.Element.index
   .. automethod:: panflute.base.Element.ancestor
   .. automethod:: panflute.base.Element.offset
   .. autoattribute:: panflute.base.Element.prev
   .. autoattribute:: panflute.base.Element.next
   .. automethod:: panflute.base.Element.replace_keyword
   .. autoattribute:: panflute.base.Element.container

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following elements inherit from :class:`Element`:

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
   
       >>> e = Para(Str(Hello), Space, Str(World!))
   
   This creates a ``Para`` element, which stores the three
   inline elements (Str, Space and Str) inside an ``.content`` attribute.
   If we add ``.parent`` attributes to these elements,
   there are three ways they can be made obsolete:
   
   1. By replacing specific elements: ``e.content[0] = Str('Bye')``
   2. By replacing the entire list: ``e.contents = other_items``
   
   We deal with the first problem with wrapping the list of items
   with a ListContainer class of type :class:`collections.MutableSequence`.
   This class updates the ``.parent`` attribute to elements returned
   through ``__getitem__`` calls.
   
   For the second problem, we use setters and getters which update the
   ``.parent`` attribute.


Standard elements
*****************

These are the standard Pandoc elements, as described `here <https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html>`_. Consult the `repo <https://github.com/jgm/pandoc-types/commits/master/Text/Pandoc/Definition.hs>`_ for the latest updates.

.. note::
   The attributes of every element object will be
   i) the parameters listed below, plus
   ii) the attributes of :class:`Element`.
   Example:

       >>> h = Str(text='something')
       >>> h.text
       'something'
       >>> hasattr(h, 'parent')
       True

   **Exception:** the ``.content`` attribute only exists
   in elements that take ``*args``
   (so we can do ``Para().content`` but not ``Str().content``).

.. automodule:: panflute.elements
   :noindex:
   :members: Doc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: panflute.elements
   :members:
   :exclude-members: Doc


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
   do ``altered = doc.walk()``.

.. automodule:: panflute.io
   :members:

.. note::
   The *action* functions have a few rules:

   - They are called as ``action(element, doc)`` so they must accept at
     least two arguments.
   - Additional arguments can be passed through the ``**kwargs** of
     ``toJSONFilter`` and ``toJSONFilters``.
   - They can return either an element, ``None``, or ``[]``.
   - If they return ``None``, the document will keep the same document
     as before (although it might have been modified).
   - If they return another element, it will take the place of the
     received element.
   - If they return ``[]`` (an empty list), they will be deleted from the
     document. Note that you can delete a row from a table or an item from
     a list, but you cannot delete the caption from a table (you can
     make it empty though).

"Batteries included" functions
******************************

These are functions commonly used when writing more complex filters

.. currentmodule:: panflute.tools

.. autosummary::

   stringify
   convert_text
   yaml_filter
   debug
   shell


See also ``Doc.get_metadata`` and ``Element.replace_keyword``

.. automodule:: panflute.tools
   :members:
