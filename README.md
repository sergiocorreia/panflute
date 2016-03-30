# Extensions to [pandocfilters](https://github.com/jgm/pandocfilters)

*(Note: This is an experimental build and is likely to evolve)*

This Python package contains the basic functionality of `pandocfilters`
plus helper functions useful for complex filters.
They contain common boilerplate plus asserts and sanity checks to minimize bugs.

For a guide to pandocfilters, see the [repository](https://github.com/jgm/pandocfilters)
and the [tutorial](http://pandoc.org/scripting.html).
The repo includes [sample filters](https://github.com/jgm/pandocfilters/tree/master/examples),
and the wiki lists useful [third party filters](https://github.com/jgm/pandoc/wiki/Pandoc-Filters).

The extensions introduced here include:

## 1. YAML block filters

Many filters introduce new elements (tables, figures, etc.) via fenced code blocks
(with either three tildes or backticks as fences).
They allow for titles, filenames, etc. via [attributes](http://pandoc.org/README.html#fenced-code-blocks).
However, these quickly get hard to read (and write, and use source control on):

<pre><code>
```{.table file="foo.csv" header=yes aligns=LRCRR inlinemarkdown=yes
 caption="my **caption**" delimiter="," quotechar="\"" }
```
</code></pre>


asdasdasd


*(example taken from the [pandoc-placetable](https://github.com/mb21/pandoc-placetable) filter)*

More complex filters---that use attributes such as long blocks of text or lists---quickly get even moreunwieldy, so as a solution YAML block filters just move the attributes
to a YAML miniblock inside the filter. The above would then be:

    ```table
    file: foo.csv
    header: true
    aligns: LRCRR
    inlinemarkdown: true
    caption: my **caption**
    delimiter:','
    quotechar:'\"'
    ```

If we also had data, we can add it after a YAML end delimiter (either `---` or `...`):

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





# License

A lot of the code started as copy--paste of `pandocfilter` by @jgm, so we just extend his BSD license.

# Helper Functions for Code Block Pandoc Filters

This module contains helper functions for YAML block filters.
A YAML block is a code block (delimited with three tildes or
backticks) with an identifier on the first line and YAML as
the code content. The identifier describes which filter to 
apply, and the YAML describes attributes and content. Examples:

~~~ figure
title: Some Title ($e=mc^2$ and *bold*)
notes: 'If the notes contain colons: wrap them in single quotes'
source: picture.png
label: optional-label
~~~

~~~ table
title: Summary Stats
notes: 'Some notes'
label: summary-stats
source: '../Tables/summary-stats.tex'
~~~

~~~ table
title: Summary Stats
notes: 'Some notes'
label: summary-stats
input: csv # Some comment
---
Variable, Mean, Median
Price, 10, 11
Weight, 12, 13
~~~

~~~ algorithm
title: K-Means
input: $\vx, \vy$
output: $\vz \in \SR$
steps:
  1. Something
  2. Something else
~~~

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

To process each module, you just do

>>> import utils
>>> filters = {'figure': figure_filter, 'algorithm': algo_filter}
>>> doc = utils.get_doc()
>>> metadata = utils.get_metadata(doc)
>>> doc = utils.filter(metadata, filters)
>>> utils.dump(doc) # When you are done

Advanced Cases
--------------

If you want to read all the filter instances, run an external script
once, and then apply the results, you can do:

1. Curry the function so you append the attributes of each instance
2. Call utils.filter() for the filter stata_read
3. Run Stata
4. Call utils.filter() for the filter stata_write
5. Then call other utils.filter() again for the normal filters

Similarly, if you want e.g. figures at the end, you can set up a
backmatter list:

>>> from functools import partial
>>> backmatter = []
>>> fig_filter = partial(figure_filter, backmatter=backmatter)

And after running the filters, use the included replace filter:

>>> bm = build_backmatter(backmatter) # Join it somehow
>>> doc = utils.replace_filter(doc, bm, location="REPLACE_HERE")

(If location is not set, it will be appended at the end of the document)
