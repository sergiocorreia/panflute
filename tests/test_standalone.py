'''
Test panflute independently of Pandoc,
by creating elements (instead of loading them from Pandoc)
and then modifying them.
'''

from panflute import *


def test_standalone():

	# Create document
	x = Para(Str('Hello'), Space, Str('world!'))
	m = {'a': True, 'b': 123.4, 'c': MetaBlocks(Para(Str('!')))}
	doc = Doc(x, metadata=m)

	# Interact with content
	print(repr(stringify(doc)))
	#assert stringify(doc) == 'Hello world!', stringify(doc)  # Do we want metadata in stringify?
	assert 'Hello world!' in stringify(doc)

	doc.content.append(Para(Str('More')))
	print(repr(stringify(doc)))
	assert 'Hello world!\n\nMore' in stringify(doc)
	
	# Interact with metadata
	doc.metadata['d'] = False
	doc.metadata['e'] = MetaBool(True)
	doc.metadata['f'] = {'A': 1233435353, 'B': 456}
	doc.metadata['f']['g'] = [1,2,3,4,5]
	doc.metadata['g'] = 123

	assert isinstance(doc.get_metadata('d'), bool)
	assert isinstance(doc.get_metadata('e'), bool)
	assert isinstance(doc.get_metadata('f.B'), str)

	assert doc.get_metadata('e') == True, repr(doc.get_metadata('e'))
	assert doc.get_metadata('f.A') == '1233435353', repr(doc.get_metadata('f.A'))
	assert doc.get_metadata('f.e') == None
	assert doc.get_metadata('f.g') == ['1','2','3','4','5'], repr(doc.get_metadata('f.g'))

	p = doc.content[0]
	p.content.append(Str('3434'))
	print(p)
	#print(stringify(p))
	s = p.content[0]

	assert s.offset(0) is s

	print(s.next)
	print(s.next.next)
	print(s.offset(2))
	print(s.offset(-1))
	print(s.parent.next)
	print(s.ancestor(2))
	print(s.ancestor(3))
	print(s.parent.parent)
	#print(s.parent.parent.parent.parent) # Fail

	s.parent.content.append(Space())
	s.parent.content.append(Space)

	x = Space()
	x.parent

	print(s.parent)
	print(doc.content)


	a = Str('a')
	a.parent

	title = [Str('Monty'), Space, Str('Python')]
	header = Header(*title, level=2, identifier='toc')
	header.level += 1
	header.to_json()

	div = Div(p, p, classes=['a','b'])
	span = Span(Emph(Str('hello')))

	div.content.append(Plain(span))


	c = Citation('foo', prefix=[Str('A')])
	c.hash = 100
	c.suffix= p.content

	cite = Cite(Str('asdasd'), citations=[c])
	print(cite)


	li1 = ListItem(Para(Str('a')))
	li2 = ListItem(Null())
	lx1 = [li1, li2]
	lx2 = [[Para(Str('b')), Null()], [Header(Str('foo'))]]

	asd = [ListItem(*x) for x in lx2]
	lx2 = BulletList(*asd)

	ul = BulletList(*lx1)
	ul.content.extend(lx2.content)

	print(header)

	di1 = DefinitionItem([Str('a'), Space], [Definition(p)])
	di2 = DefinitionItem([Str('b'), Space], [Definition(p)])

	dl = DefinitionList(di1, di2)


	term = [Str('Spam')]
	def1 = Definition(Para(Str('...emails')))
	def2 = Definition(Para(Str('...meat')))
	spam = DefinitionItem(term, [def1, def2])

	term = [Str('Spanish'), Space, Str('Inquisition')]
	def1 = Definition(Para(Str('church'), Space, Str('court')))
	inquisition = DefinitionItem(term=term, definitions=[def1])
	dl = DefinitionList(spam, inquisition)

	print(dl)

	print('------')
	print(dl.content[0])

	x = dl.content[0].definitions[0]
	print(x.parent)
	print('--')
	print(x.offset(0))
	print(x.next)
	print(x.parent.next.term)
	print(type(x.parent.next.term))


	x = [Para(Str('Something')), Para(Space, Str('else'))]
	c1 = TableCell(*x)
	c2 = TableCell(Header(Str('Title')))

	rows = [TableRow(c1, c2)]
	table_head = TableHead(TableRow(c2,c1))
	body = TableBody(*rows)
	table = Table(body, head=table_head, caption=Caption())

	print(table)


	# REPLACE KEYWORD FUNCTION
	p1 = Para(Str('Spam'), Space, Emph(Str('and'), Space, Str('eggs')))
	p2 = Para(Str('eggs'))
	p3 = Plain(Emph(Str('eggs')))
	doc = Doc(p1, p2, p3)

	print(doc.content.list)
	print(stringify(doc))

	print('-'*20)

	doc.replace_keyword(keyword='eggs', replacement=Str('salad'))
	print('<', stringify(doc), '>')

	print('-'*20)

	doc.replace_keyword(keyword='salad', replacement=Para(Str('PIZZA')))
	print(doc.content.list)
	print('<', stringify(doc), '>')





	# CONVERT TEXT (MD, ETC)
	md = 'Some *markdown* **text** ~xyz~'
	tex = r'Some $x^y$ or $x_n = \sqrt{a + b}$ \textit{a}'
	print(convert_text(md))
	print(convert_text(tex))



if __name__ == "__main__":
    test_standalone()
