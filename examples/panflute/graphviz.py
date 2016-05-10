#!/usr/bin/env python

"""
Pandoc filter to process code blocks with class "graphviz" into
graphviz-generated images.
"""

import pygraphviz
import hashlib
import os
import sys
from panflute import toJSONFilter, Str, Para, Image, CodeBlock


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()

imagedir = "graphviz-images"


def graphviz(elem, doc):
    if type(elem) == CodeBlock and 'graphviz' in elem.classes:
        code = elem.text
        caption = "caption"
        G = pygraphviz.AGraph(string=code)
        G.layout()
        filename = sha1(code)
        filetype = {'html': 'png', 'latex': 'pdf'}.get(doc.format, 'png')
        alt = Str(caption)
        src = imagedir + '/' + filename + '.' + filetype
        if not os.path.isfile(src):
            try:
                os.mkdir(imagedir)
                sys.stderr.write('Created directory ' + imagedir + '\n')
            except OSError:
                pass
            G.draw(src)
            sys.stderr.write('Created image ' + src + '\n')
        return Para(Image(alt, url=source, title=''))


if __name__ == "__main__":
    toJSONFilter(graphviz)
