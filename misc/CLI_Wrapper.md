# Some notes on CLI wrappers for Pandoc

There are three active and one inactive CLI wrappers for pandoc:

1. [`pandocomatic`](https://heerdebeer.org/Software/markdown/pandocomatic/) (Ruby)
2. [`panrun`](https://github.com/mb21/panrun) (Ruby; powers [panwriter](https://panwriter.com/))
3. [`rmarkdown`](https://rmarkdown.rstudio.com/) (R; powers [bookdown](https://bookdown.org/) and RStudio)
4. [`panzer`](https://github.com/msprev/panzer) (Python; inactive)

They mostly have two goals:

1. Avoid having to type *long* Pandoc command line calls that need to be remembered every time, and instead replace them with the equivalent of `make`. This means that all the options need to be either stored within the YAML metadata of the document, or in a separate YAML file, so it can be used through multiple documents.
2. Extending Pandoc by adding preprocessing, custom filters, postprocessing, etc.

Is it worth it to add a new one? To avoid the [standard proliferation problem](https://xkcd.com/927/), we need to know if there is something we need that can't be done with the three active tools, or by maintaining other ones such as `panzer`. Also, even if we add a new CLI wrapper, it would be good to avoid reinventing the wheel altogether.

Also, pandoc constantly adds [features](https://github.com/jgm/pandoc/issues/5870) that reduce the need of CLI wrappers.


# Current tools

*(disclaimer: this is a relatively shallow evaluation of the current tools for my personal purposes, so take it with ~~one~~ two grains of salt)*

## `pandocomatic`

- Supports pre/post processors
- Supports common yaml files. **(ISSUE?)** Why are the files so nested? (`templates` contains `templatename`, which contains `pandoc`, which  contains the actual key-value metadata)
- Supports adding settings to yaml header. **(ISSUE?)** again, settings need to be nested within `pandocmatic_`-`pandoc`, and seem verbose (why `use-template` instead of `template`? also templates can be confused with the Pandoc templates)
- Supports running Pandoc on many files (e.g. in a website), including running all files in a folder, only modified files, etc. However, I have no need for that.
- Pandocomatic itself can be configured through a YAML file to avoid typing its command line arguments. Seems useful, but perhaps a bit too meta.

## `panrun`

- Minimalistic; aims to be "a simple script", so it's not too complex to understand but doesn't support pre/post processors.
- Seems to use the `output` key (instead of `pandocmatic_`) and within it there are subkeys for each output type (html, latex, etc.)
- The first metadata key (e.g. html) will be used as default output format, but this can be changed through the `--to` option.
- Pandoc options are passed-through, but others are silently ignored. **(ISSUE?)** What about typos?

## `panzer`

- Worked through the `style` metadata field; multiple styles allowed.
- Allowed much more than just pandoc command line arguments: pre/post processing, latex/beamer pre/post flight, cleanup, inheritance through `parent` field


## `rmarkdown`

- See: https://bookdown.org/yihui/rmarkdown/pdf-document.html
- Essentially the key feature is interleaving of R code and prose.
- Not very useful in my case, where code can be long (100s of lines) and take long to run (hours)


# Best of both worlds approach


## YAML blocks

- Inheritance? not through YAML anchors (too complicated, no one knows how to use them) but through a `extends` field (better than `parent` or `inherits`)
- Sample YAML blocks:

```yaml
author: John Smith
title: Some Title
panflute:
  filters: ['fix-tables', 'include-files']
style: arxiv
```

```yaml
author: John Smith
title: Some Title
panflute:
  filters: ['fix-tables', 'include-files']
pandoc:
 - include-in-header: xyz.tex
 - preserve-tabs: true
```


## CLI Options

- `view`: show in PDF viewer
- `watch`: watch the file and re-run as needed
- `verbose`: display debugging information
- `tex`: save tex file in addition of the PDF output

## Defaults:

- By default, `standalone` will be true, output will be PDF



## Misc:

- Should we have an output: format for the default output type? like rmarkdown
- The rmarkdown extensions are also quite useful: https://bookdown.org/yihui/rmarkdown/bookdown-markdown.html#bookdown-markdown
	- Theorem YAML codeblocks
	- Cross-referencing

