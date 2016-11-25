# PyPI Distribution Instructions

## Guides

- https://packaging.python.org/distributing/#upload-your-distributions
- http://peterdowns.com/posts/first-time-with-pypi.html


## Instructions

First you may want to test a local install:

```
python setup.py install
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
py.test --cov=panflute tests && coverage html && cd htmlcov && index.html && cd ..
```

This requires `pip install coverage` and `pip install pytest-cov`.
