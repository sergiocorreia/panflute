Panflute API
============

.. contents:: Contents:
   :local:



Base elements
****************



.. autoclass:: panflute.base.Element

   .. attribute:: parent
      
      Element that contains the current one.

      :rtype: :class:`Element` | ``None``

   .. autoattribute:: panflute.base.Element.content
   .. autoattribute:: panflute.base.Element.index
   .. automethod:: panflute.base.Element.ancestor
   .. automethod:: panflute.base.Element.offset
   .. autoattribute:: panflute.base.Element.prev
   .. autoattribute:: panflute.base.Element.next

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These two elements inherit from :class:`Element`:

.. automodule:: panflute.base
   :members: Block, Inline

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. note:: To keep track of every element's parent we do some 
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
     with an Items class of type :class:`collections.MutableSequence`.
     This class updates the ``.parent`` attribute to elements returned
     through ``__getitem__`` calls.

     For the second problem, we use setters and getters which update the
     ``.parent`` attribute.


Standard elements
*****************

These are the standard Pandoc elements, as described `here <https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html>`_. Consult the `repo <https://github.com/jgm/pandoc-types/commits/master/Text/Pandoc/Definition.hs>`_ for the latest updates.

.. note::
   Unless noted otherwise, the attributes of an element are the same as the
   arguments used when creating the element, plus the attributes of :class:`Element`. Example:

       >>> h = Str(text='something')
       >>> h.text
       'something'
       >>> hasattr(h, 'parent')
       True

.. warning::
   Exception: the ``.content`` attribute is only
   inherited by elements that accept the ``*args`` argument.

.. automodule:: panflute.elements
   :members: Doc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: panflute.elements
   :members:
   :exclude-members: Doc


Standard functions
********************************************

These are the same functions exposed by `pandocfilters <https://github.com/jgm/pandocfilters>`_, although with different arguments.

.. currentmodule:: panflute.io

.. autosummary::

   toJSONFilter
   toJSONFilters
   load
   dump
   walk
   stringify


.. automodule:: panflute.io
   :members:


"Batteries included" functions
******************************

These are functions commonly used when writing more complex filters

.. currentmodule:: panflute.tools

.. autosummary::

   replace_keyword
   debug
   convert_markdown
   yaml_filter
   shell

.. automodule:: panflute.tools
   :members:
