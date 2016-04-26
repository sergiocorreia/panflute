from panflute import *

def increase_header_level(elem, doc):
	if type(elem)==Header:
		if elem.level < 6:
			elem.level += 1
		else:
			return []

if __name__ == "__main__":
    toJSONFilter(increase_header_level)