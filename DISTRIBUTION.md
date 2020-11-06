# PyPI Distribution Instructions

## Guides

- https://packaging.python.org/distributing/#upload-your-distributions
- http://peterdowns.com/posts/first-time-with-pypi.html


## Instructions

First you may want to test a local install and test it:

```
python setup.py install
py.test
```

Then,

1. Copy .pypirc file from backup (if required, as it's not synced to git)
2. Test it: `python setup.py sdist upload -r pypitest`
3. Run it live:

```
pandoc README.md --output=README.rst && python setup.py sdist upload -r pypi
```

## Documentation

To run *and* update docs and website, run:

```
cd docs && make.bat html && cd .. && cd ../website && jekyll build && s3_website push && cd ../panflute
```

## PDF Documentation

To build the pdf version (slow), install miktex or similar and run:

```
cd docs && make.bat latex && cd build && cd latex && Makefile && cd
```

(On Windows, replace `Makefile` with a few runs of `pdflatex Panflute.tex`)

Then copy the resulting PDF into the Panflute folder of the website.


## Unit Tests and Code Coverage

To run unit tests locally and check code coverage, run:

```
pytest --cov=panflute tests && coverage html && cd htmlcov && index.html && cd ..
```

This requires a development environment,
which can be installed from the repository's root directory using:

```shell
pip install --editable ".[dev]"
```


## Pushing to PyPI through Twine

First, ensure that you have `twine` installed and the checks pass:

```bash
cls && python setup.py sdist && twine check dist/*
```

Then try the test PyPI repository:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose
```

Finally update to the official repo:

```bash
twine upload  dist/*
```

### Possible errors

#### `warning: `long_description_content_type` missing. defaulting to `text/x-rst`.`

Solution: ensure that files have Unix line endings (not Windows)
