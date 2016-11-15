"""
Fenced code block filter; used for testing
"""

import panflute as pf

def fenced_action(options, data, element, doc):
	count = options.get('count', 1)
	div = pf.Div(attributes={'count': str(count)})
	div.content.extend([pf.HorizontalRule] * count)
	return div

def main():
    pf.run_filter(pf.yaml_filter, tag='spam', function=fenced_action)

if __name__ == '__main__':
	main()
