#!/usr/bin/env python

# ---------------------------
# Imports
# ---------------------------

import os
from string import Template

import panflute as pf


# ---------------------------
# Constants
# ---------------------------

LATEX_TEMPLATE = Template(r"""
%%%% BEGIN FIGURE %%%%
$pagebreak
{\setstretch{1.0} % Force single spacing for media
  \begin{figure}[htbp]
    \centering
    \begin{minipage}[c]{$width\textwidth}
      \vspace{10pt}
      \centering\includegraphics[width=$innerwidth\linewidth]{"$fn"} \\
      \caption{$title}\label{fig:$label}
      \medskip
      \justify
      \$notesize
      $notes
    \end{minipage}
  \end{figure}
\par
} % End single spacing
%%%% END FIGURE %%%%
""")

    
# ---------------------------
# Functions
# ---------------------------

def prepare(doc):
    doc.backmatter = []


def finalize(doc):
    if doc.backmatter:
        doc.replacement_ok = False
        backmatter = pf.Div(*doc.backmatter, identifier='backmatter')
        pf.replace_keyword(doc, '$backmatter', backmatter)
        assert doc.replacement_ok, "Couldn't replace '$backmatter'"
    else:
        pf.replace_keyword(doc, '$backmatter', pf.Null())

def figure(options, data, element, doc):

    # Get options
    fn = os.path.abspath(options['source']).replace('\\', '/')
    title = options.get('title', 'Untitled')
    notes = data
    label = options.get('label', os.path.splitext(os.path.basename(fn))[0])

    if doc.format == 'latex':
        subs = {'fn': fn, 'label': label}
        subs['title'] = pf.convert_markdown(title, format='latex')
        subs['notes'] = pf.convert_markdown(notes, format='latex')
        backmatter = doc.get_metadata('format.backmatter', False)
        pagebreak = doc.get_metadata('format.media-pagebreak', False)

        w = options.get('width', 1.0)
        subs['width'] = w
        subs['innerwidth'] = options.get('innerwidth', w) / w
        subs['notesize'] = options.get('notesize', 'small')
        subs['pagebreak'] = '\\clearpage\n' if pagebreak else ''

        text = LATEX_TEMPLATE.safe_substitute(subs)
        ans = pf.RawBlock(text=text, format='latex')

        if backmatter:
            doc.backmatter.append(ans)
            msg = '\hyperref[fig:{}]{{[\Cref{{fig:{}}} Goes Here]}}'
            msg = msg.format(label, label)
            return pf.Plain(pf.Str(msg))
        else:
            return ans
    else:
        title = pf.convert_markdown(title)
        assert len(title)==1, title
        title = (title[0]).items

        notes = pf.Div(*pf.convert_markdown(notes), classes=['note'])
        title_text = pf.stringify(title)
        img = pf.Image(*title, url=fn, title=title_text, identifier=label)
        ans = pf.Div(pf.Plain(img), pf.Plain(pf.LineBreak), notes, classes=['figure'])
        return ans


# ---------------------------
# Main
# ---------------------------

if __name__ == "__main__":
    pf.toJSONFilter(pf.yaml_filter, prepare=prepare, finalize=finalize,
                    tag='figure', function=figure)
