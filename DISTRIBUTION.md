# PyPI Distribution Instructions

Also see:

- https://packaging.python.org/distributing/#upload-your-distributions
- http://peterdowns.com/posts/first-time-with-pypi.html

1. Copy .pypirc file from backup (if required, as it's not synced to git)
2. Test it: python setup.py sdist upload -r pypitest
3. Run it live: python setup.py sdist upload -r pypi
