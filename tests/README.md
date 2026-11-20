To run the tests:

* install panflute with its development dependencies, from the root of the repo:
  `python -m pip install -e ".[dev]"` (see [CONTRIBUTING.md](../CONTRIBUTING.md#development-setup)),
* make sure `pandoc` is installed and on your `PATH`,
* keep the CWD at the root of the Panflute repo,
* run:
```
pytest --cov --cov-report=html
```
