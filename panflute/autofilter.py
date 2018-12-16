"""
Allow Panflute to be run as a command line script
main():
    to be used as a Pandoc filter
panfl():
    to be used in Pandoctools shell scripts as
    Pandoc filter with arguments
"""

import os
import os.path as p
import sys
from collections import OrderedDict
import click

from .io import load, dump
from .tools import debug
from .utils import ContextImport


def get_filter_dir(hardcoded=False):
    if hardcoded:
        if os.name == 'nt':
            return p.join(os.environ["APPDATA"], "pandoc", "filters")
        else:
            return p.join(os.environ["HOME"], ".pandoc", "filters")
    else:
        from .tools import run_pandoc
        # Extract $DATADIR
        info = run_pandoc(args=['--version']).splitlines()
        prefix = "Default user data directory: "
        info = [row for row in info if row.startswith(prefix)]
        assert len(info) == 1
        data_dir = info[0][len(prefix):]
        return p.join(data_dir, 'filters')


def _main(filters=None, extra_dirs=None, data_dir=False, sys_path=True):
    """
    :param filters: Union[List[str], None]
        if not None then it's panfl
        instead of panflute
    :param extra_dirs: Union[List[str], None]
        if not None then it's panfl
        instead of panflute
    :param data_dir: bool
    :param sys_path: bool
    :return: json doc
    """
    doc = load()
    # meta = doc.metadata  # Local variable 'meta' value is not used
    verbose = doc.get_metadata('panflute-verbose', False)

    if extra_dirs is None:
        # metadata 'panflute-path' can be a list, a string, or missing
        # `extra_dirs` should be a list of str
        extra_dirs = doc.get_metadata('panflute-path', [])
        if type(extra_dirs) != list:
            extra_dirs = [extra_dirs]
        extra_dirs.append('.')
        if data_dir:
            extra_dirs.append(get_filter_dir())
    elif data_dir:
        # panfl case:
        extra_dirs.append(get_filter_dir(hardcoded=True))

    # Display message (tests that everything is working ok)
    msg = doc.get_metadata('panflute-echo', False)
    if msg:
        debug(msg)

    if filters is None:
        # metadata 'panflute-filters' can be a list, a string, or missing
        # `filters` should be a list of str
        filters = doc.get_metadata('panflute-filters', [])
        if type(filters) != list:
            filters = [filters]

    if filters:
        if verbose:
            msg = "panflute: will run the following filters:"
            debug(msg, ' '.join(filters))
        doc = autorun_filters(filters, doc, extra_dirs, verbose, sys_path)
    elif verbose:
        debug("panflute: no filters were provided")

    dump(doc)


def main():
    _main(data_dir=True)


@click.command(help="Filters should have basename only (may be with or without .py extension). " +
               "Search preserves directories order (except for --data-dir and `sys.path`).")
@click.argument('filters', nargs=-1)
@click.option('-w', '-t', '--write', '--to', 'to', type=str, default='html',
              help='Pandoc writer option.')
@click.option('--dir', '-d', 'extra_dirs', multiple=True,
              help="Search filters in provided directories: `-d dir1 -d dir2`.")
@click.option('--data-dir', is_flag=True, default=False,
              help="Search filters in default user data directory listed in `pandoc --version` " +
                   "(in it's `filters` subfolder actually). It's appended to the search list.")
@click.option('--no-sys-path', 'not_sys_path', is_flag=True, default=False,
              help="Disable search filters in python's `sys.path` " +
                   "(I tried to remove current working directory either way) " +
                   "that is appended to the search list.")
def panfl(filters, to, extra_dirs, data_dir, not_sys_path):
    # `load()` in `_main()` needs `to` in the 2nd arg
    if len(sys.argv) > 1:
        sys.argv[1] = to
    elif len(sys.argv) == 1:
        sys.argv.append(to)
    _main(list(filters), list(extra_dirs), data_dir, sys_path=not not_sys_path)


def autorun_filters(filters, doc, extra_dirs, verbose, sys_path=True):
    """
    :param filters: list of str
    :param doc: panflute.Doc
    :param extra_dirs: list of str
    :param verbose: bool
    :param sys_path: bool
    :return: panflute.Doc
    """
    search_path = extra_dirs
    if sys_path:
        search_path += [dir_ for dir_ in sys.path if (dir_ != '') and (dir_ != '.') and p.isdir(dir_)]

    file_names = OrderedDict()

    for filter_ in filters:
        if not filter_.endswith('.py') and not (p.sep in filter_):
            file_names[filter_] = filter_
            continue

        for path in search_path:
            # Allow with and without .py ending
            filter_path = p.abspath(p.normpath(
                p.join(path, filter_ + ('' if filter_.endswith('.py') else '.py'))
            ))
            if p.isfile(filter_path):
                if verbose:
                    debug("panflute: filter <{}> found in {}".format(filter_, filter_path))
                file_names[filter_] = filter_path
                break
            elif verbose:
                debug("          filter <{}> NOT found in {}".format(filter_, filter_path))
        else:
            raise Exception("filter not found: " + filter_)

    for filter_, filter_path in file_names.items():
        if verbose:
            debug("panflute: running filter <{}>".format(filter_))
        with ContextImport(filter_path, extra_dirs) as module:
            try:
                module.main(doc)
            except Exception as e:
                debug("Failed to run filter: " + filter_)
                if not hasattr(module, 'main'):
                    debug(' - Possible cause: filter lacks a main() function')
                debug('Filter code:')
                debug('-' * 64)
                with open(filter_path) as fp:
                    debug(fp.read())
                debug('-' * 64)
                raise Exception(e)
        if verbose:
            debug("panflute: filter <{}> completed".format(filter_))

    return doc
