#!/usr/bin/env python

"""
Pandoc filter to process code blocks with class "plantuml" into
plant-generated images.
"""

import hashlib
import os
import sys
from panflute import toJSONFilter, Str, Para, Image, CodeBlock
from subprocess import call


imagedir = "plantuml-images"


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()


def filter_keyvalues(kv):
    res = []
    caption = []
    for k, v in kv:
        if k == u"caption":
            caption = [Str(v)]
        else:
            res.append([k, v])

    return caption, "fig:" if caption else "", res


def plantuml(elem, doc):
    if type(elem) == CodeBlock and 'plantuml' in elem.classes:
        if 'caption' in elem.attributes:
            caption = [Str(elem.attributes['caption'])]
            typef = 'fig:'
        else:
            caption = []
            typef = ''

        filetype = {'html': 'svg', 'latex': 'eps'}.get(doc.format, 'png')
        src = os.path.join(imagedir, filename + '.uml')
        dest = os.path.join(imagedir, filename + '.' + filetype)

        if not os.path.isfile(dest):
            try:
                os.mkdir(imagedir)
                sys.stderr.write('Created directory ' + imagedir + '\n')
            except OSError:
                pass

            txt = code.encode("utf-8")
            if not txt.startswith("@start"):
                txt = "@startuml\n" + txt + "\n@enduml\n"
            with open(src, "w") as f:
                f.write(txt)

            call(["java", "-jar", "plantuml.jar", "-t" + filetype, src])

            sys.stderr.write('Created image ' + dest + '\n')

        return Para(Image(*caption, identifier=elem.identifier,
                          attributes=elem.attributes, url=dest, title=typef))

if __name__ == "__main__":
    toJSONFilter(plantuml)
