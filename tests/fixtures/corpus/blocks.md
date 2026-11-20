# Header level one {#custom-id .unnumbered lang=en}

## Header *with* inline markup

###### Header level six

Setext header
-------------

A paragraph with
two lines.

> A block quote
>
> > with a nested quote
>
> - and a list

- tight item one
- tight item two
    - nested item

* loose item one

* loose item two

  with a second paragraph

3. ordered starting at three
4. next

(a) lower alpha with two parens
(b) second

i.  lower roman, period
ii. second

#. default style
#. second

(@) example list item
(@good) labelled example

A reference to example (@good).

Term one
:   Definition one

Term *two*
:   Definition two, first

:   Definition two, second

    with a code block inside:

        code inside definition

Compact term
~   compact definition

| The limerick packs laughs anatomical
|     Into space that is quite economical.
|
| But the good ones I've seen

```python {#code-block-id .numberLines startFrom="10"}
def f(x):
    return x + 1
```

    indented code block
    second line

~~~
fenced without class
~~~

```{=html}
<div class="raw-html">raw html block</div>
```

```{=latex}
\begin{center}raw latex\end{center}
```

<div class="html-div">
Markdown *inside* an HTML div.
</div>

::: {#div-id .warning data-level="2"}
Fenced div content.

::: nested
Nested div.
:::
:::

* * * * *

![A figure caption with *emphasis*](figure.png "fig title"){#fig-id width=80%}

<!-- an html comment -->

Final paragraph.
