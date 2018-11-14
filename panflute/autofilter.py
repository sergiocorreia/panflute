"""
Allow Panflute to be run as a command line script
(so it can be used as a Pandoc filter)
"""

import os
import sys
from collections import OrderedDict

from .io import load, dump
from .tools import debug, run_pandoc
from .utils import ContextImport


def main():
    doc = load()
    meta = doc.metadata

    verbose = doc.get_metadata('panflute-verbose', False)

    # extra_path can be a list, a string, or missing
    extra_path = doc.get_metadata('panflute-path', [])
    if type(extra_path) != list:
        extra_path = [extra_path]

    # Display message (tests that everything is working ok)
    msg = doc.get_metadata('panflute-echo', False)
    if msg:
        debug(msg)

    # Run filters sequentially
    filters = doc.get_metadata('panflute-filters', [])

    # Allow for a single filter instead of a list
    if type(filters) != list:
        filters = [filters]

    if filters:
        if verbose:
            msg = "panflute: will run the following filters:"
            debug(msg, ' '.join(filters))
        doc = autorun_filters(filters, doc, extra_path, verbose)
    elif verbose:
        debug("panflute: no filters found in metadata")

    dump(doc)


def autorun_filters(filters, doc, searchpath, verbose):
    # Extract $DATADIR
    info = run_pandoc(args=['--version']).splitlines()
    prefix = "Default user data directory: "
    info = [row for row in info if row.startswith(prefix)]
    assert len(info) == 1
    datadir = info[0][len(prefix):]
    filterdir = os.path.join(datadir, 'filters')

    searchpath = searchpath + ['.', filterdir] + sys.path
    filenames = OrderedDict()

    for ff in filters:
        for p in searchpath:

            # Allow with and without .py ending
            if ff.endswith('.py'):
                fn = os.path.join(p, ff)
            else:
                fn = os.path.join(p, ff + '.py')

            if os.path.isfile(fn):
                if verbose:
                    debug("panflute: filter <{}> found in {}".format(ff, fn))
                filenames[ff] = fn
                break
            elif verbose:
                debug("          filter <{}> NOT found in {}".format(ff, fn))
        else:
            raise Exception("filter not found: " + ff)

    for ff, fn in filenames.items():
        _ = dict()
        if verbose:
            debug("panflute: running filter <{}>".format(ff))
        with ContextImport(fn) as module:
            try:
                module.main(doc)
            except:
                debug("Failed to run filter: " + ff)
                if not hasattr(module, 'main'):
                    debug(' - Possible cause: filter lacks a main() function')
                debug('Filter code:')
                debug('-' * 64)
                debug(code)
                debug('-' * 64)
                raise
        if verbose:
            debug("panflute: filter <{}> completed".format(ff))

    return doc
