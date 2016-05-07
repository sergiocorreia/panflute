"""
Remove all tables
"""

from panflute import *

def action(elem, doc):
    if isinstance(elem, Table):
    	return []

if __name__ == '__main__':
    toJSONFilter(action)
