# To Do List

- Finish io and tools, and then test
- Split elements into a CSV with name, args, docstring, 
  to_json format, and a creator fn.
  This is akin to having a templating engine.
- Better docstring for partial functions:
  compare `help(panflute.Div)` with `help(panflute.Table)`.
  To fix, just set the `foobar.__doc__` attribute.

# Maybe

- Add elements for rows, cells, table head, table body, individual definitions (pairs), and everything else that is currently a nested list
- Add a `.getparent()` attribute as in lxml (but for that we need a way to distinguish whether the child element was in the `.items` property or in the header property).
- More radically, replace all the elements with lxml.etree.Element instances, and move the `.get_content` methods to its own function. This would give us css selectors, xpath, etc. (so we can select based on whether its the first row, if it has siblings, etc.). OTOH, it might create other problems (besides a dependency on lxml).