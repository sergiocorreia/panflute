"""
Shared pytest configuration for the panflute test suite (hooks and fixtures).
Plain helper functions and paths live in ``helpers.py``.

- Every path is resolved relative to the tests directory, so the suite can be
  run from any working directory.
- Tests that need a ``pandoc`` executable are marked ``requires_pandoc`` and
  are skipped (not failed) when pandoc is not on the PATH.
- Tests that make pandoc run panflute filters (``pandoc --filter panfl``,
  ``pandoc --filter some_filter.py``) use the ``filter_env`` fixture, which
  puts the running interpreter's scripts directory first on the PATH, so that
  pandoc finds the ``python``/``panfl``/``panflute`` belonging to the
  interpreter under test rather than whatever the caller has on its PATH.
"""

import os
import shutil
import sys

import pytest

from .helpers import PANDOC, SCRIPTS_DIR

# Fixture directories contain Python files (filters, packages) that must not
# be imported by pytest's collection: some are even named test_*.py.
collect_ignore_glob = ['fixtures/*']


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_runtest_setup(item):
    if item.get_closest_marker('requires_pandoc') and PANDOC is None:
        pytest.skip('pandoc executable not found on PATH')


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def no_pandoc_environment(monkeypatch):
    """
    Remove the environment variables that pandoc sets when it runs a filter
    (``Doc()`` reads them), so that no test inherits them from the caller.
    For instance, the ``pandoc/actions/setup`` GitHub action exports
    ``PANDOC_VERSION``. Filters run by pandoc still get them from pandoc.
    """
    monkeypatch.delenv('PANDOC_VERSION', raising=False)
    monkeypatch.delenv('PANDOC_READER_OPTIONS', raising=False)


@pytest.fixture
def filter_env(monkeypatch):
    """
    Make subprocesses (pandoc and the filters it launches) use the running
    interpreter: prepend its scripts directory to PATH and return the
    environment dict, for tests that pass ``env=`` explicitly.
    """
    if shutil.which('panfl', path=str(SCRIPTS_DIR)) is None:
        pytest.skip(f'panflute console scripts not installed in {SCRIPTS_DIR}')
    path = os.pathsep.join([str(SCRIPTS_DIR), os.environ.get('PATH', '')])
    monkeypatch.setenv('PATH', path)
    return dict(os.environ)


@pytest.fixture
def clean_import_state(monkeypatch):
    """
    Undo the side effects of importing filter modules from the fixtures
    directory (sys.modules entries, sys.path changes, sys.argv changes).
    """
    before = set(sys.modules)
    monkeypatch.setattr(sys, 'path', list(sys.path))
    monkeypatch.setattr(sys, 'argv', list(sys.argv))
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    yield
    installed = (sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix)
    for name in set(sys.modules) - before:
        module_file = getattr(sys.modules[name], '__file__', None) or ''
        # Forget filter modules (from fixtures, examples or tmp_path), so that
        # another test importing a module of the same name gets a fresh one
        if module_file and not module_file.startswith(installed):
            del sys.modules[name]
