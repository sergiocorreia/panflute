# Misc

- Can use isinstance(element, Block)
- Can use globals through doc

# Panflute -- Pythonic Pandoc Filters

This Python package is intended as a Pythonic alternative to 
[pandocfilters](https://github.com/jgm/pandocfilters). Its features include:

- Elements can be created "Pythonically", directly by specifying arguments. Thus, instead of
`Div(attributes({id: "foo"}, [Str("bar"), Str("Spam")])` you can write
`Div(Str(bar), Str(spam), identifier=foo)`
- Elements are documented, so autocompletion works and `help(div)` is useful.
- Complex cases, such as tracking global variables, are easier to handle.
- There are useful helper functions for some common--but--complex filters.

## Motivation

The lack of documentation about the precise JSON format that Pandoc expects
makes filters in Python both harder to create and maintain.

For instance, it is really hard to read code like this
six months down the line:
`Para([Image(['a caption', [], []], [], [src, ""])])`

Alternatively, we will do:
`Para(Image(text='a caption', source=src))`

Thus, we hope that filters written with `panflute` are more readable and concise. Some examples of ported filters are [included](/tree/master/examples/panflute).

### Pandoc Filters

For a guide to pandocfilters, see the [repository](https://github.com/jgm/pandocfilters)
and the [tutorial](http://pandoc.org/scripting.html).
The repo includes [sample filters](https://github.com/jgm/pandocfilters/tree/master/examples),
and the wiki lists useful [third party filters](https://github.com/jgm/pandoc/wiki/Pandoc-Filters).


## Extensions

The extensions introduced here include:

### 1. YAML block filters

Many filters introduce new elements (tables, figures, etc.) via fenced code blocks
(with either three tildes or backticks as fences).
They allow for titles, filenames, etc. via [attributes](http://pandoc.org/README.html#fenced-code-blocks).
However, these quickly get hard to read (and write, and use source control on):

<pre><code>
```{.table file="foo.csv" header=yes aligns=LRCRR inlinemarkdown=yes
 caption="my **caption**" delimiter="," quotechar="\"" }
```
</code></pre>

*(example taken from the [pandoc-placetable](https://github.com/mb21/pandoc-placetable) filter)*

More complex filters---that use attributes such as long blocks of text or lists---quickly get even more unwieldy,
so as a solution YAML block filters just move the attributes
to a YAML miniblock inside the filter. The above would then be:

<pre><code>
```table
file: foo.csv
header: true
aligns: LRCRR
inlinemarkdown: true
caption: my **caption**
delimiter:','
quotechar:'\"'
```
</code></pre>

If we also had data, we can add it after a YAML end delimiter (either `---` or `...`):

<pre><code>
```table
file: foo.csv
header: true
aligns: LRCRR
inlinemarkdown: true
caption: my **caption**
delimiter:','
quotechar:'\"'
...
Fruit, Quantity, Price  
apples, 15, 3.24  
oranges, 12, 2.22
```
</code></pre>


### More Examples

Figures and tables:

<pre><code>
~~~ figure
title: Some Title (some latex $e=mc^2$ and *some markdown*)
notes: 'If the notes contain colons: wrap them in single quotes'
source: picture.png
label: optional-label
~~~
</code></pre>

<pre><code>
~~~ table
title: Summary Stats
notes: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
label: summary-stats
source: '../Tables/summary-stats.tex'
~~~
</code></pre>

<pre><code>
~~~ algorithm
title: K-Means
input: $\vx, \vy$
output: $\vz \in \SR$
steps:
  1. Something
  2. Something else
~~~
</code></pre>

<pre><code>
~~~ stata
title: A Stata Table
refresh: false
source: '../tmp/stuff.csv'
---
sysuse auto
collapse (mean) price, by(foreign)
outsheet using '../tmp/stuff.csv', replace
exit, STATA // implicit?
~~~
</code></pre>

#### Usage

```python
import pandocfilters_extended as pf
from string import Template

def figures(opt, content, format, meta):
    base = r"\begin{figure}\caption{$title}\includegraphics{$fn}\end{figure}"
    tex = Template(base).safe_substitute(title=opt.title, fn=opt.fn)
    return tex

if __name__ == "__main__":
    myfilter = pf.block_filter('table', figures)
    pf.toJSONFilter(myfilter)
```

### 2. Support for external scripts

If you want to read all the instances of a filter and then run an external script
*once* (to compile the results, you can do):

```python
import pandocfilters_extended as pf
from string import Template

def read_stata(opt, content, format, meta, commands):
    commands.extend(content)

def write_stata(opt, content, format, meta, commands):
    # do something with the text based on -opt- or -content-
    pass

def get_cmd(format, meta, commands):
    # write commands to a temp file
    return 'stata.exe do ' + temp_file

if __name__ == "__main__":
    commands = []
    myfilter = pf.block_filter('table', reader=read_stata, write=write_stata, cmd=get_cmd, commands=commands)
    pf.toJSONFilter(myfilter)
```

This will do a first pass that creates the list of script lines that need to be run, then call an external command,
then do a second pass that uses the output of the command to write into the AST.

### 3. Support for global variables and backmatter

We may want to append all figures and tables to the end, so we need an alternative AST for that,
and some placeholder text

TODO: the filters should take a backmatter option, where we write the output, and then we should have a replace option that 
either appends the text at the end of the document, or at a specific place (walking through the doc and replacing a specific word).

Internally, we could rely on partial to curry the functions:

```
>>> from functools import partial
>>> backmatter = []
>>> fig_filter = partial(figure_filter, backmatter=backmatter)
```


And after running the filters, use the included replace filter:

```
>>> bm = build_backmatter(backmatter) # Join it somehow
>>> doc = utils.replace_filter(doc, bm, location="REPLACE_HERE")
```



# Advanced Template

```python
import pandocfilters_extended as pf
filters = {'figure': figure_filter, 'algorithm': algo_filter}
doc = pf.get_doc()
metadata = pf.get_metadata(doc)
doc = pf.walk(doc, metadata, filters)
pf.dump(doc)
```

# Install

Run:

```
pip install git+git://github.com/sergiocorreia/pandocfilters_extended.git
```

(Windows note: open `cmd` as administrator)

# Dev Install

`python setup.py install`
: installs the package locally

`python setup.py develop`
: installs locally with a symlink so changes are automatically updated

# License

A lot of the code started as copy--paste of `pandocfilter` by @jgm, so we just extend his BSD license.
