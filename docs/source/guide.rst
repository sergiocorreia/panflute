User guide
==========


A Simple filter
***************

Suppose we want to create a filter that sets all headers to level 1. For this, write this python script:

.. literalinclude:: _static/header-level-1.py

.. note:: a more complete template is `located here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/_static/template.py>`_

More complex filters
********************

We might want filters that replace an element instead of just modifying it.
For instance, suppose we want to replace all emphasized text with striked
out text:

.. literalinclude:: _static/emph2strikeout.py

Or if we want to remove all tables:

.. literalinclude:: _static/remove-tables.py


Globals and backmatter
**********************

Suppose we want to add a table of contents based on all headers, or move all tables to a specific location in the document. This requires tracking global
variables (which can be stored as attributes of ``doc``).

To add a table of contents at the beginning:

.. literalinclude:: _static/toc.py

To move all tables to the place where the string *$tables* is:

.. literalinclude:: _static/move-tables.py


Using the included batteries
****************************

There are several functions and methods that make your life easier, such as
the `replace_keyword <code.html#panflute.base.Element.replace_keyword>`_
method shown above.

Other useful functions include
`convert_text <code.html#panflute.tools.convert_text>`_
(to load and parse markdown or other formatted text) and
`stringify <code.html#panflute.tools.stringify>`_ 
(to extract the underlying text from an element and its children).
For metadata, you can use the `doc.get_metadata <code.html#panflute.elements.Doc.get_metadata>`_ attribute to extract user--specified options (booleans, strings, etc.)

For instance, you can combine these functions to allow for include directives (so you can include and parse markdown files from other files).

.. literalinclude:: _static/include.py


YAML code blocks
****************

A YAML filter is a filter that parses fenced code blocks
that contain YAML metadata. For instance:

.. code-block:: none

    Some text

    ~~~ csv
    title: Some Title
    has-header: True
    ---
    Col1, Col2, Col3
    1, 2, 3
    10, 20, 30
    ~~~

    More text

Note that fenced code blocks use three or more
`tildes <http://pandoc.org/README.html#extension-fenced_code_blocks>`_
or 
`backticks <http://pandoc.org/README.html#extension-backtick_code_blocks>`_
as separators.
Within a code block, use `three hyphens or three dots <http://pandoc.org/README.html#extension-yaml_metadata_block>`_
to separate the YAML options from the rest of the block.


As an example, we will design a filter that will be applied to
all code blocks with the *csv* class, like the one shown above.
To avoid boilerplate code (such as parsing the YAML part), we use the
useful `yaml_filter <code.html#panflute.tools.yaml_filter>`_ function:

.. literalinclude:: _static/csv-tables.py

.. note:: a more complete template is `here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/_static/fenced-template.py>`_ , a fully developed filter for CSVs is `also available <https://github.com/ickc/pantable>`_.

.. note:: `yaml_filter` now allows a `strict_yaml=True` option, which allows multiple YAML blocks, but with the caveat that all YAML blocks must start with `---` and end with `---` or `...`.


Calling external programs
******************************

We might also want to embed results from other programs.

One option is to do so through Python's internals.
For instance, we can use fetch data from wikipedia and show it on the document.
Thus, the following script will replace links like these: ``[Pandoc](wiki://)``
With this "Pandoc is a free and open-source software document converter...".

.. literalinclude:: _static/wiki.py

Alternatively, we might want to run other programs through the shell.
For this, explore the `shell <code.html#panflute.tools.shell>`_
function.

Navigating through the document tree
************************************

You might wish to apply a filter that depends on the parent or sibling objects of an element. For instance, Modify the first row (`TableRow`) of a table, or all the `Str` items nested within a header.

For this, every element has a `.parent` attribute (and the related `.next`, `.prev`, `.ancestor(#), `.index`, `.offset(#)` attributes).

For example, the code below will emphasize all text in the last row of every table:

.. literalinclude:: _static/emph-last-row.py


Running filters automatically
******************************

If you run panflute as a filter (``pandoc ... -F panflute``), then panflute will run all filters specified in the metadata field ``panflute-filters``. This is faster and more convenient than typing the precise list and order of filters used every time the document is run.

You can also specify the location of the filters with the ``panflute-path`` field, which will take precedence over Pandoc's search `locations <https://pandoc.org/MANUAL.html#reader-options>`_ (``.``, ``$datadir/filters``, and ``$path``).

Example:

.. literalinclude:: _static/autofilters.md

For this to work, the filters need to have a very specific
structure, with a `main()` function of the following form:

.. literalinclude:: _static/template.py

.. note:: To be able to run filters automatically, the main function needs to be exactly as shown, with an optional argument ``doc``, that gets passed to ``run_filter``, and which is ``return`` ed back.

.. note:: You can add ``panflute-verbose: true`` to the metadata to display debugging information, including the folders searched and the filters executed.
