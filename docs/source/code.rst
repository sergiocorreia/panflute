Panflute API
============

.. contents:: Contents:
   :local:


Standard functions
********************************************

These are the same functions exposed by `pandocfilters <https://github.com/jgm/pandocfilters>`_, although with different arguments

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

   toJSONFilter
   toJSONFilters
   load
   dump
   walk
   stringify

.. automodule:: panflute.tools
   :members:


Special elements
****************

.. automodule:: panflute.elements
   :members: Doc, Element, Inline, Block

Standard elements
*****************

These are the standard Pandoc elements, as described `here <https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html>`_. Consult the `repo <https://github.com/jgm/pandoc-types/commits/master/Text/Pandoc/Definition.hs>`_ for the latest updates.

.. automodule:: panflute.elements
   :members:
   :exclude-members: Doc, Element, Inline, Block

