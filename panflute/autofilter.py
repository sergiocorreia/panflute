"""
Allow Panflute to be run as a command line script
(so it can be used as a Pandoc filter)
"""

import os
import sys
from collections import OrderedDict

from .io import load, dump
from .tools import debug, stringify, run_pandoc


def main():
	doc = load()
	meta = doc.metadata

	verbose = doc.get_metadata('panflute-verbose', False)

	extra_path = doc.get_metadata('panflute-path', '')
	extra_path = [stringify(extra_path)] if extra_path else []

	
	# Display message (tests that everything is working ok)
	msg = doc.get_metadata('panflute-echo')
	if msg:
		debug(stringify(msg))

	# Run filters sequentially
	filters = doc.get_metadata('panflute-filters')
	if filters:
		filters = [stringify(chunk) for chunk in filters]
		if verbose:
			debug("panflute: will run the following filters:", ' '.join(filters))
		doc = autorun_filters(filters, doc, extra_path, verbose)
	elif verbose:
		debug("panflute: no filters found in metadata")

	dump(doc)


def autorun_filters(filters, doc, searchpath, verbose):
	# Extract $DATADIR
	info = run_pandoc(args=['--version']).splitlines()
	prefix = "Default user data directory: "
	info = [row for row in info if row.startswith(prefix)]
	assert len(info) == 1
	datadir = info[0][len(prefix):]

	searchpath = searchpath + ['.', datadir] + sys.path
	filenames = OrderedDict()

	for ff in filters:
		for p in searchpath:
			fn = os.path.join(p, ff + '.py')
			if os.path.isfile(fn):
				if verbose:
					debug("panflute: filter <{}> found in {}".format(ff, fn))
				filenames[ff] = fn
				break
			elif verbose:
				debug("          filter <{}> NOT found in {}".format(ff, fn))
		else:
			raise Exception("filter not found: " + ff) 

	for ff, fn in filenames.items():
		_ = dict()
		if verbose:
			debug("panflute: running filter <{}>".format(ff))
		if verbose:
			debug("panflute: filter <{}> completed".format(ff))
		with open(fn) as fp:
		    exec(fp.read(), _)
		    doc = _['main'](doc)
	
	return doc