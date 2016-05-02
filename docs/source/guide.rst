User guide
==========


Creating a document from scratch
********************************

.. note:: A guiding principle is that an element can contain lists of
   elements, but not lists of dicts or other objects.

   The most complex example is this:

   - The :class:`DefinitionList` element can contain mutiple :class:`DefinitionItem`.
   - In turn, these contain multiple inlines under the ``.term`` attribute
     and multiple definitions.
   - Finally, each definition can contain multiple blocks.

   Notice that we don't allow a definition item to contain lists of lists of blocks, we need it to be lists of definition elements (which are lists of blocks). This is to preserve the ``.parent`` attribute.


Then you can feed it to pandoc as json...



A Simple filter
***************

EXPLAIN HOW TO CREATE A SINGLE FILTER
EG: REPLACE EMPH TEXT WITH UNFORMATTED TEXT (STR)

Globals and backmatter
**********************

ADD A TOC!
$toc adn then replace it with a list that links to the element

ADD AN INCLUDE DIRECTIVE
$include(introduction.md)

YAML blocks
***********



EXPLAIN THE FIGURES FILTER

Calling external programs
******************************

Through Python's batteries

https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=Stack%20Overflow


Through the shell function


Metadata
********

TODO: Example replacing a Header(Str('Abstract')) and everything after that before the next header with Null and moving the content to the metadata as abstract MetaBlock!? 