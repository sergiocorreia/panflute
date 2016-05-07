"""
Set all headers to level 1
"""

from panflute import *

def action(elem, doc):
    if isinstance(elem, Header):
    	elem.level = 1

if __name__ == '__main__':
    toJSONFilter(action)
