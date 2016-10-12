#!/usr/bin/env python

"""
Pandoc filter to convert definition lists to bullet
lists with the defined terms in strong emphasis (for
compatibility with standard markdown).
"""

from panflute import toJSONFilter, DefinitionList, BulletList, ListItem, Para, Strong


def deflists(elem, doc):
    if type(elem) == DefinitionList:
        bullets = [tobullet(item) for item in elem.content]
        return BulletList(*bullets)


def tobullet(item):
    ans = [Para(Strong(*item.term))]
    for definition in item.definitions:
        for block in definition.content:
            ans.append(block)
    return ListItem(*ans)


if __name__ == "__main__":
    toJSONFilter(deflists)
