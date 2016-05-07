from panflute import *
x = Para(Str('Hello'), Str('world!'))

m = {'a': True, 'b': 123.4, 'c': Para(Str('!'))}

doc = Doc(x, metadata=m)
doc.content.append(Para(Str('More')))
doc.metadata['d'] = False
doc.metadata['e'] = MetaBool(True)
doc.metadata['f'] = {'A': 1233435353, 'B': 456}
doc.metadata['f']['g'] = [1,2,3,4,5]

print(type(doc.get_metadata('d')))
print(type(doc.get_metadata('e')))
print(type(doc.get_metadata('f.B')))

print(doc.get_metadata('f.A'))

print('<<<<<')
print(type(doc.get_metadata('f.g')))
print(doc.get_metadata('f.g'))
print('>>>>>')


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
table = Table(*rows, header=TableRow(c2,c1))

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
tex = 'Some $x^y$ or $x_n = \sqrt{a + b}$ \textit{a}'
print(convert_text(md))
print(convert_text(tex))
