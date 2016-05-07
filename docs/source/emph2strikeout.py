"""
Replace Emph elements with Strikeout elements
"""

from panflute import *

def action(elem, doc):
    if isinstance(elem, Emph):
    	return Strikeout(*elem.content)

if __name__ == '__main__':
    toJSONFilter(action)
