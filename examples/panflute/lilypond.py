#!/usr/bin/env python3

"""
Pandoc filter to process code blocks with class "ly" containing
Lilypond notation.  Assumes that Lilypond and Ghostscript are
installed, plus [lyluatex](https://github.com/jperon/lyluatex) package for
LaTeX, with LuaLaTeX.
"""

import os
from sys import getfilesystemencoding, stderr
from subprocess import Popen, call, PIPE
from hashlib import sha1
from panflute import toJSONFilter, Para, Image, RawInline, RawBlock, Code, CodeBlock

IMAGEDIR = "tmp_ly"
LATEX_DOC = """\\documentclass{article}
\\usepackage{libertine}
\\usepackage{lyluatex}
\\pagestyle{empty}
\\begin{document}
%s
\\end{document}
"""


def sha(x):
    return sha1(x.encode(getfilesystemencoding())).hexdigest()


def latex(code):
    """LaTeX inline"""
    return RawInline(code, format='latex')


def latexblock(code):
    """LaTeX block"""
    return RawBlock(code, format='latex')


def ly2png(lily, outfile, staffsize):
    p = Popen([
        "lilypond",
        "-dno-point-and-click",
        "-dbackend=eps",
        "-djob-count=2",
        "-ddelete-intermediate-files",
        "-o", outfile,
        "-"
    ], stdin=PIPE, stdout=-3)
    p.stdin.write(("\\paper{\n"
        "indent=0\\mm\n"
        "oddFooterMarkup=##f\n"
        "oddHeaderMarkup=##f\n"
        "bookTitleMarkup = ##f\n"
        "scoreTitleMarkup = ##f\n"
        "}\n"
        "#(set-global-staff-size %s)\n" % staffsize +
        lily).encode("utf-8"))
    p.communicate()
    p.stdin.close()
    call([
        "gs",
        "-sDEVICE=pngalpha",
        "-r144",
        "-sOutputFile=" + outfile + '.png',
        outfile + '.pdf',
    ], stdout=-3)


def png(contents, staffsize):
    """Creates a png if needed."""
    outfile = os.path.join(IMAGEDIR, sha(contents + str(staffsize)))
    src = outfile + '.png'
    if not os.path.isfile(src):
        try:
            os.mkdir(IMAGEDIR)
            stderr.write('Created directory ' + IMAGEDIR + '\n')
        except OSError:
            pass
        ly2png(contents, outfile, staffsize)
        stderr.write('Created image ' + src + '\n')
    return src


def lily(elem, doc):
    if type(elem) == Code and 'ly' in elem.classes:
        staffsize = int(elem.attributes.get('staffsize', '20'))
        if doc.format == "latex":
            if elem.identifier == "":
                label = ""
            else:
                label = '\\label{' + elem.identifier + '}'
            return latex(
                '\\includely[staffsize=%s]{%s}' % (staffsize, contents) +
                label
            )
        else:
            infile = contents + (
                '.ly' if '.ly' not in contents else ''
            )
            with open(infile, 'r') as doc:
                code = doc.read()
            return Image(url=png(code, staffsize))

    if type(elem) == CodeBlock and 'ly' in elem.classes:
        staffsize = int(elem.attributes.get('staffsize', '20'))
        if doc.format == "latex":
            if elem.identifier == "":
                label = ""
            else:
                label = '\\label{' + elem.identifier + '}'
            return latexblock(
                '\\lily[staffsize=%s]{%s}' % (staffsize, code) +
                label
            )
        else:
            return Para(Image(url=png(code, staffsize)))

if __name__ == "__main__":
    toJSONFilter(lily)
