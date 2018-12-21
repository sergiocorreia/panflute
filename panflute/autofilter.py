"""
Allow Panflute to be run as a command line executable
to be used as a Pandoc filter or used in Pandoctools
shell scripts as Pandoc filter with arguments.

Exports ``main`` and ``panfl``.
"""

import os
import os.path as p
import sys
import click

from .io import load, dump
from .tools import debug
from .utils import ContextImport


reduced_sys_path = [dir_ for dir_ in sys.path if (dir_ not in ('', '.')) and p.isdir(dir_)]


def get_filter_dir(hardcoded=True):
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
        return p.normpath(p.expanduser(p.expandvars(p.join(data_dir, 'filters'))))


def stdio(filters=None, search_dirs=None, data_dir=True, sys_path=True, panfl_=False, input_stream=None, output_stream=None):
    """
    Reads JSON from stdin and second CLI argument:
    ``sys.argv[1]``. Dumps JSON doc to the stdout.

    :param filters: Union[List[str], None]
        if None then read from metadata
    :param search_dirs: Union[List[str], None]
        if None then read from metadata
    :param data_dir: bool
    :param sys_path: bool
    :param panfl_: bool
    :param input_stream: io.StringIO or None
        for debug purpose
    :param output_stream: io.StringIO or None
        for debug purpose
    :return: None
    """
    doc = load(input_stream)
    # meta = doc.metadata  # Local variable 'meta' value is not used
    verbose = doc.get_metadata('panflute-verbose', False)

    if search_dirs is None:
        # metadata 'panflute-path' can be a list, a string, or missing
        # `search_dirs` should be a list of str
        search_dirs = doc.get_metadata('panflute-path', [])
        if type(search_dirs) != list:
            search_dirs = [search_dirs]
        if '--data-dir' in search_dirs:
            data_dir = True
        if '--no-sys-path' in search_dirs:
            sys_path = False
        search_dirs = [dir_ for dir_ in search_dirs
                       if dir_ not in ('--data-dir', '--no-sys-path')]

    if verbose:
        debug('panflute: data_dir={} sys_path={}'.format(data_dir, sys_path))
    search_dirs = [p.normpath(p.expanduser(p.expandvars(dir_))) for dir_ in search_dirs]

    if not panfl_:
        # default panflute behaviour:
        search_dirs.append('.')
        if data_dir:
            search_dirs.append(get_filter_dir())
        if sys_path:
            search_dirs += sys.path
    else:
        # panfl/pandoctools behaviour:
        if data_dir:
            search_dirs.append(get_filter_dir())
        if sys_path:
            search_dirs += reduced_sys_path

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
        doc = autorun_filters(filters, doc, search_dirs, verbose)
    elif verbose:
        debug("panflute: no filters were provided")

    dump(doc, output_stream)


def main():
    """
    Allows Panflute to be run as a command line executable
    to be used as a Pandoc filter.
    """
    stdio()


help_str = """Allows Panflute to be run as a command line executable:

* to be used in Pandoctools shell scripts as Pandoc filter with
multiple arguments (should have -t/--to option in this case):
`pandoc -t json | panfl -t markdown foo.bar | pandoc -f json`

* to be used as a Pandoc filter (in this case only one positional
argument is allowed of all options): `pandoc --filter panfl`

Filters may be set with or without .py extension.
It can be relative or absolutele paths to files or modules specs
like `foo.bar`.

MIND THAT Panflute temporarily prepends folder of the filter
(or relevant dir provided if module spec) TO THE `sys.path` before
importing the filter!

Search preserves directories order (except for --data-dir and
`sys.path`).
"""


@click.command(help=help_str)
@click.argument('filters', nargs=-1)
@click.option('-w', '-t', '--write', '--to', 'to', type=str, default=None,
              help='Derivative of Pandoc writer option that Pandoc passes to filters.')
@click.option('--dir', '-d', 'search_dirs', multiple=True,
              help="Search filters in provided directories: `-d dir1 -d dir2`.")
@click.option('--data-dir', is_flag=True, default=False,
              help="Search filters in default user data directory listed in `pandoc --version` " +
                   "(in it's `filters` subfolder actually). It's appended to the search list.")
@click.option('--no-sys-path', 'sys_path', is_flag=True, default=True,
              help="Disable search filters in python's `sys.path` (without '' and '.') " +
                   "that is appended to the search list.")
def panfl(filters, to, search_dirs, data_dir, sys_path):
    """
    Allows Panflute to be run as a command line executable:

    * to be used in Pandoctools shell scripts as Pandoc filter with
      multiple arguments (should have -t/--to option in this case):
      ``pandoc -t json | panfl -t markdown foo.bar | pandoc -f json``

    * to be used as a Pandoc filter (in this case only one positional
      argument is allowed of all options):
      ``pandoc --filter panfl``

    MIND THAT Panflute temporarily prepends folder of the filter
    (or relevant dir provided if module spec) TO THE `sys.path` before
    importing the filter!
    """
    if to is None:
        if (len(filters) > 1) or search_dirs or not sys_path or data_dir:
            raise ValueError('When no `--to` option then Pandoc filter mode assumed and ' +
                             'only one positional argument is allowed of all options.')
        else:
            filters, search_dirs = None, None
            sys_path, data_dir = True, False
    else:
        filters, search_dirs = list(filters), list(search_dirs)
        # `load()` in `stdio()` needs `to` in the 2nd arg
        sys.argv[1:] = []
        sys.argv.append(to)

    stdio(filters, search_dirs, data_dir, sys_path, panfl_=True)


def autorun_filters(filters, doc, search_dirs, verbose):
    """
    :param filters: list of str
    :param doc: panflute.Doc
    :param search_dirs: list of str
    :param verbose: bool
    :return: panflute.Doc
    """
    def remove_py(s):
            return s[:-3] if s.endswith('.py') else s

    filter_paths = []
    for filter_ in filters:
        filter_exp = p.normpath(p.expanduser(p.expandvars(filter_)))

        if filter_exp == remove_py(p.basename(filter_exp)).lstrip('.'):
            # import .foo  # is not supported
            module = True
            mod_path = filter_exp.replace('.', p.sep)
            path_postfixes = (p.join(mod_path, '__init__.py'), mod_path + '.py')
        else:
            module = False
            # allow with and without .py ending
            path_postfixes = (remove_py(filter_exp) + '.py',)

        for path, path_postf in [(path, path_postf)
                                 for path in search_dirs
                                 for path_postf in path_postfixes]:
            if p.isabs(path_postf):
                filter_path = path_postf
            else:
                filter_path = p.abspath(p.normpath(p.join(path, path_postf)))

            if p.isfile(filter_path):
                if verbose:
                    debug("panflute: filter <{}> found in {}".format(filter_, filter_path))

                if module and not (path in reduced_sys_path):
                    extra_dir = p.abspath(path)
                    # `path` already doesn't contain `.`, `..`, env vars or `~`
                else:
                    extra_dir = None
                module_ = filter_exp if module else filter_path

                filter_paths.append((filter_, filter_path, module_, extra_dir))
                break
            elif p.isabs(path_postf):
                if verbose:
                    debug("          filter <{}> NOT found in {}".format(filter_, filter_path))
                raise Exception("filter not found: " + filter_)
            elif verbose:
                debug("          filter <{}> NOT found in {}".format(filter_, filter_path))
        else:
            raise Exception("filter not found: " + filter_)

    for filter_, filter_path, module_, extra_dir in filter_paths:
        if verbose:
            debug("panflute: running filter <{}>".format(filter_))
        with ContextImport(module_, extra_dir) as module:
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
