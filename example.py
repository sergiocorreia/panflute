import panflute as pf


doc = pf.load(filename=None) # If no fn, from stdin
# fmt = pf.format() ???
# doc.content doc.metadata doc.raw_metadata doc.format

doc = pf.walk(doc, some_filter)
doc_json = doc.to_json()

pf.dump(filename=None) # if no fn, to stdout

