Installation
===================

To install panflute from PyPI, open the command line and type::

    pip install panflute

- Works with Python 3.10+, and PyPy (panflute 2.3.1 is the last version
  that works with Python 3.7 to 3.9; pip installs it automatically there)
- Requires `pandoc <https://pandoc.org/installing.html>`_ 2.11 or later;
  panflute |version| supports pandoc 2.11.4 to 3.14
- Depends on `click <https://pypi.org/project/click/>`_ (for the command line
  tools) and `PyYAML <https://pypi.org/project/PyYAML/>`_ (for :func:`.yaml_filter`).
  To also install the optional `yamlloader <https://pypi.org/project/yamlloader/>`_,
  which keeps the order of YAML mappings, type ``pip install "panflute[extras]"``
- On Windows, you might need to open the command line (``cmd``)  as administrator (`ctrl+shift+enter`).

Panflute is also available on `conda-forge <https://anaconda.org/conda-forge/panflute>`_,
which can install a matching pandoc with it::

    conda install -c conda-forge pandoc panflute

To install the latest Github version of panflute, type::

    pip install git+https://github.com/sergiocorreia/panflute.git

To upgrade from panflute 2.x, see :doc:`whatsnew`.


Dev Install
***************

After cloning the Github repo into your computer, you can install the package locally::

    python -m pip install .

Alternatively, you can install it in editable mode, so changes are automatically updated,
together with the development tools (pytest, ruff, mypy)::

    python -m pip install -e ".[dev]"

To build this documentation, install the ``docs`` extra and run Sphinx
from the root of the repository::

    python -m pip install -e ".[docs]"
    sphinx-build -W -b html docs/source docs/build/html

Source Code
***************

To browse the source code, report issues or contribute, check the `github repository <https://github.com/sergiocorreia/panflute/>`_.
