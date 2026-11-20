Plain words, *emphasis*, **strong**, ***both***, ~~strikeout~~,
super^script^ and sub~script~, [small caps]{.smallcaps} and
[underlined]{.underline}.
A soft break follows this line
and a hard break follows this one\
then `inline code`{#code-id .python key="value"} and `` code with `ticks` ``.

"Double quoted" and 'single quoted' text, with an apostrophe's and
an ellipsis... plus an em---dash and an en--dash.

Inline math $e^{i\pi} + 1 = 0$ and display math $$\int_0^1 x\,dx$$ in a paragraph.

Raw inline: `<b>bold</b>`{=html}, `\textbf{bold}`{=latex} and `#strong[bold]`{=typst}.
Inline HTML <span class="raw">is parsed</span> too.

A [link](https://example.com "Link title"), an [attributed link](/path){#lid .cls target="_blank"},
an autolink <https://pandoc.org>, an email <user@example.com>, and a
[reference link][ref].

An inline image ![alt *text*](image.png "Image title"){width=50%} inside text.

A [span with attributes]{#span-id .class-a .class-b data-x="1" data-y="two"}
and an empty span []{#anchor}.

A footnote reference[^1] and an inline note^[Inline *note* text.].

[ref]: https://example.org/ref "Reference title"

[^1]: The footnote has two paragraphs.

    Second paragraph of the footnote, with `code`.
