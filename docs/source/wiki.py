"""
Panflute filter that embeds wikipedia text

Replaces markdown such as [Stack Overflow](wiki://) with the resulting text.
"""

import requests
import panflute as pf


def action(elem, doc):
    if isinstance(elem, pf.Link) and elem.url.startswith('wiki://'):
        title = pf.stringify(elem).strip()
        baseurl = 'https://en.wikipedia.org/w/api.php'
        query = {'format': 'json', 'action': 'query', 'prop': 'extracts',
            'explaintext': '', 'titles': title}
        r = requests.get(baseurl, params=query)
        data = r.json()
        extract = list(data['query']['pages'].values())[0]['extract']
        extract = extract.split('.', maxsplit=1)[0]
        return pf.RawInline(extract)


if __name__ == '__main__':
    pf.toJSONFilter(action)
