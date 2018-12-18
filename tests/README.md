* install packages from [`setup.py`](../setup.py) -> `extras_require` -> `'test'`,
  (if you use pip instead of conda you can do it right from pip),
* change CWD in terminal to the root of the Panflute repo,
* run:
```
py.test --cov=panflute tests && coverage html && cd htmlcov && index.html && cd ..
```
