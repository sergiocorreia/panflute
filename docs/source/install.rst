Install
===================

Panflute requires Python 3.2+. Writing a port for Python 2.7 shouldn't be hard though, as most of the differences lie in a few IO functions.

User Install
***************

Just run::

    pip install git+git://github.com/sergiocorreia/panflute.git

Windows note: open the command line (``cmd``) as administrator.

Dev Install
***************

Install the package locally::

    python setup.py install

Install locally through a symlink, so changes are automatically updated::

    python setup.py develop
