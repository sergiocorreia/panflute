# PyPI Distribution Instructions

Also see:

- https://packaging.python.org/distributing/#upload-your-distributions
- http://peterdowns.com/posts/first-time-with-pypi.html

1. Copy .pypirc file from backup (if required, as it's not synced to git)
2. Test it: `python setup.py sdist upload -r pypitest`
3. Run it live:

```
pandoc README.md --output=README.rst && python setup.py sdist upload -r pypi
```

Note: to run *and* update docs and website, also run:

```
cd docs && make.bat html && cd .. && cd ../website && jekyll build && s3_website push && cd ../panflute
```


## Unit Tests and Code Coverage

To run unint tests locally and check code coverage, run:

```
py.test --cov=panflute tests && coverage html && cd htmlcov && index.html && cd ..
```

This requires `pip install coverage` and `pip install pytest-cov`.
