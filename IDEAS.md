# Ideas for later

This file records changes that were considered for panflute 3.0 and left
out, so that nobody has to rediscover them. Nothing here is planned or
promised.

## Faster loading and walking

Each idea below would make panflute faster, and each was left out because
it changes something a user can observe. The gains were measured once, in
November 2026, on one machine, against the 3.0 development branch, with
pandoc 3.1.3. Treat them as rough. To measure an idea, use
`tests/benchmark.py` with `--compare` (see [tests/README.md](tests/README.md#benchmarks));
differences of a few percent are noise.

### Turn off the garbage collector during `load()`

- **Gain:** `load()` takes 30% less time on CPython 3.12 (68 ms instead of
  96 ms) and 19% less on 3.14: that is the share of its time the garbage
  collector spends running while `load()` creates elements.
- **What would change:** `gc.disable()` is a switch for the whole process.
  While `load()` runs, the callbacks in `gc.callbacks` do not fire, and
  if another thread disables the collector in the meantime, `load()` would
  turn it back on when it ends.
- **To adopt it:** decide that these effects are acceptable, turn the
  collector back on only if it was on before, document it, and test that a
  `load()` that fails also turns it back on.

### Reuse the container objects in `walk()`

- **Gain:** an estimated 20 to 25% off `walk()` and `stringify()`.
  Rebuilding the containers takes about 27% of the time of `walk()`.
- **What would change:** today, after a walk, each parent holds a new
  container object with the same elements, so `para.content` before and
  after a walk are different objects. With this change they would be the
  same object, which a filter that keeps a reference to a container across
  a walk would notice.
  `test_walk_leaves_new_containers_with_the_same_elements` in
  `tests/test_walk.py` pins the current behavior.
- **To adopt it:** decide that keeping the same container is the intended
  behavior, change that test, and check that an action that replaces or
  deletes elements, or that changes its siblings or parent during the
  walk, still gives the same document.

### Skip re-checking pandoc's own JSON in `load()`

- **Gain:** up to 15% off `load()`.
- **What would change:** `load()` builds each element through its
  constructor, which checks the type of every argument. JSON written by
  pandoc always passes those checks. Without them, malformed JSON (written
  by another program, or edited by hand) would raise an error later or a
  different one.
- **To adopt it:** keep the checks for elements that users build, and add
  tests that malformed input still raises a clear error.

### Cache pandoc's API version in `convert_text()`

- **Gain:** `convert_text(x, input_format='panflute')`, when `x` is an
  element or a list of elements, takes 11.5 ms per call instead of 23 ms.
  Today each such call runs pandoc twice: once on an empty document to
  learn its API version, and once to convert.
- **What would change:** pandoc would run once per call instead of twice.
  If the pandoc executable were replaced while the Python process runs,
  the cached version would be wrong.
- **To adopt it:** key the cache on the pandoc path (`pandoc_path` or
  `PANDOC_PATH`), and accept or document the stale-cache case.

### Tried and rejected

Measured or examined, and not worth doing:

- Inlining `encode_dict` and `to_json_wrapper` in `dump()`: about 4%.
- A fast path in `from_json`, and skipping `check_type` in `_set_ica` for
  strings: about 2% off `load()`.
- Inlining `attach` into `ListContainer.__init__`: no gain.
- Calling `json.loads` on bytes instead of decoding them first: under 1 ms,
  and it would accept a UTF-8 byte-order mark that is rejected today.
- Speeding up the environment lookups in `Doc.__init__` and the climb
  through parents in `Element.doc`: they cost microseconds per document.
- Not importing click for users of `from panflute import *`: not possible
  without changing what `panfl` is.

## Other ideas

Limitations that 3.0 already documents are listed under
[Known limitations](CHANGELOG.md#known-limitations-unchanged-in-300) in the
changelog. These are not:

- **Pandoc errors say nothing.** When pandoc exits with an error,
  `run_pandoc()` in `panflute/tools.py` raises `IOError('')` (an `OSError`)
  with an empty message; pandoc's own error message goes only to stderr,
  through `debug()`. The exception could carry pandoc's exit code and
  message.
- **`convert_text()` does not fix the API version of a `Doc`.** With
  `input_format='panflute'`, `convert_text()` gives an element or a list of
  elements the API version of the installed pandoc, but sends a `Doc` as
  it is. Pandoc rejects a document whose API version differs from its own
  in the first two numbers, so a `Doc()` created with the default
  `api_version`, (1, 23), fails with pandoc 2.x (API 1.22) and would fail
  with a future pandoc that moves to API 1.24. The failure is the empty
  `IOError` above; pandoc's message ("Incompatible API versions") goes only
  to stderr.
