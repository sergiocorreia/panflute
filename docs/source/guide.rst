User guide
==========


A Simple filter
***************

Suppose we want to create a filter that sets all headers to level 1. For this, write this python script:

.. literalinclude:: header-level-1.py

.. note:: a more complete template is `here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/template.py>`_

More complex filters
********************

We might want filters that replace an element instead of just modifying it.
For instance, suppose we want to replace all emphasized text with striked
out text:

.. literalinclude:: emph2strikeout.py

Or if we want to remove all tables:

.. literalinclude:: remove-tables.py


Globals and backmatter
**********************

Suppose we want to add a table of contents based on all headers, or move all tables to a specific location in the document. This requires tracking global
variables (which can be stored as attributes of ``doc``).

To add a table of contents at the beginning:

.. literalinclude:: toc.py

To move all tables to the place where the string *$tables* is:

.. literalinclude:: move-tables.py


Using the included batteries
****************************

There are several functions and methods that make your life easier, such as
the `replace_keyword <code.html#panflute.base.Element.replace_keyword>`_
method shown above.

Other useful functions include
`convert_text <code.html#panflute.tools.convert_text>`_
(to load and parse markdown or other formatted text),
`stringify <code.html#panflute.tools.stringify>`_ 
(to extract the underlying text from an element and its children)

For instance, you can combine these functions to allow for include directives (so you can include and parse markdown files from other files).

.. literalinclude:: include.py


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

.. literalinclude:: csv-tables.py

.. note:: a more complete template is `here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/fenced-template.py>`_

Calling external programs
******************************

We might also want to embed results from other programs.

One option is to do so through Python's internals.
For instance, we can use fetch data from wikipedia and show it on the document.
Thus, the following script will replace links like these: ``[Pandoc](wiki://)``
With this "Pandoc is a free and open-source software document converter...".

.. literalinclude:: wiki.py

Alternatively, we might want to run other programs through the shell.
For this, explore the `shell <code.html#panflute.tools.shell>`_
function.
