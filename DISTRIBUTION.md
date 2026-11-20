# Releasing panflute

Releases are built and uploaded to PyPI by GitHub Actions
([`.github/workflows/publish.yml`](.github/workflows/publish.yml)) using
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/).
No PyPI passwords or API tokens are stored in the repository or its secrets.

- Publishing a **GitHub release** uploads to [PyPI](https://pypi.org/project/panflute/).
- Publishing a GitHub **prerelease**, or running the workflow manually
  (*Actions → Publish on PyPI → Run workflow*), uploads to
  [TestPyPI](https://test.pypi.org/project/panflute/) only.

The version number lives in one place: [`panflute/version.py`](panflute/version.py).


## Release checklist

1. Make sure CI is green on `master`.

2. Bump `__version__` in `panflute/version.py`; in
   [`CHANGELOG.md`](CHANGELOG.md), check that the release's section is
   complete and replace `(unreleased)` in its heading with the release date
   (e.g. `## 3.0.0 (2026-12-01)`); update the supported pandoc versions table
   in `README.md` if needed; and commit.

3. Optionally, check the build locally:

   ```bash
   python -m pip install build twine
   python -m build
   twine check --strict dist/*
   ```

4. Optionally, do a dry run on TestPyPI: run the *Publish on PyPI* workflow
   manually from the Actions tab (or publish a GitHub prerelease) and then
   `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ panflute==X.Y.Z`.
   TestPyPI never accepts the same version twice, so a re-run of an
   already uploaded version is skipped rather than failing.

5. Create a GitHub release whose tag is the version, e.g. `2.4.0` or `v2.4.0`
   (*Releases → Draft a new release*), and publish it. The workflow refuses to
   publish if the tag (minus a leading `v`) differs from `panflute.__version__`.

6. If the `pypi` environment requires approval, approve the deployment in the
   workflow run. Then check <https://pypi.org/project/panflute/>.

The [conda-forge feedstock](https://github.com/conda-forge/panflute-feedstock)
usually picks up new PyPI releases automatically through its bot.


## One-time setup (already done once; repeat only if it is lost)

### PyPI and TestPyPI trusted publishers

On <https://pypi.org/manage/project/panflute/settings/publishing/>, add a
*GitHub* trusted publisher with:

| Field             | Value              |
| ----------------- | ------------------ |
| Owner             | `sergiocorreia`    |
| Repository name   | `panflute`         |
| Workflow name     | `publish.yml`      |
| Environment name  | `pypi`             |

Do the same on <https://test.pypi.org/manage/project/panflute/settings/publishing/>
with environment name `testpypi` (the project must exist on TestPyPI and
you must be an owner there; otherwise add it as a "pending publisher").

### GitHub environments

In the repository's *Settings → Environments*, create two environments named
`pypi` and `testpypi`. Recommended for `pypi`: add yourself as a required
reviewer and restrict deployments to protected branches/tags.

### Old secrets

The old workflows authenticated with the repository secrets `pypi_password`
and `test_pypi_password`. They are no longer used and should be deleted
(*Settings → Secrets and variables → Actions*), and the corresponding PyPI
API tokens revoked.


## Documentation

The documentation at <https://scorreia.com/software/panflute/> is built with
Sphinx from [`docs/source`](docs/source):

```bash
python -m pip install sphinx
sphinx-build -b html docs/source docs/build/html
```

Then upload `docs/build/html` to the website.

To build the PDF version, install a LaTeX distribution and run
`sphinx-build -M latexpdf docs/source docs/build`.
