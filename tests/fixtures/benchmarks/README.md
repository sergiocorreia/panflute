# Benchmark documents

Three large real-world Markdown documents, kept as round-trip test inputs
(`tests/test_golden.py`) and as benchmark inputs for performance work.

| File | Source | Size of JSON |
|------|--------|--------------|
| `awesome-c.md` | <https://github.com/uhub/awesome-c/blob/6c2ecc1d5b0dc6d700eb7da592a11eabecfd2003/README.md> | ~1.5 MB |
| `barcode.md` | <https://github.com/mskyttner/actg-barcode/blob/gh-pages/index.md> | ~0.3 MB |
| `portugal.md` | <https://github.com/JJ/github-country-data/blob/9260760e7a7208de5cab6fdf263843ecb2bb1db9/formatted/top-Portugal.md> | ~1.5 MB |

The Markdown files were modified slightly when they were added: horizontal
rules `---` were replaced with `----` to avoid confusion with YAML blocks.

The `.json` files are pandoc's JSON output for them (`pandoc --from=markdown
--to=json`), regenerated with `python tests/fixtures/regenerate.py`.

To load one:

```python
import panflute as pf

with open('tests/fixtures/benchmarks/awesome-c.json', encoding='utf-8') as f:
    doc = pf.load(f)
```
