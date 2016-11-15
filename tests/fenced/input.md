---
title: Some title
author: Some author
note: this is standard markdown metadata
---

This file contains fenced code blocks that can be used
to test the panflute code that deals with YAML code blocks, 
as discussed [here](http://scorreia.com/software/panflute/guide.html#yaml-code-blocks)

# Standard examples

## Just raw data

~~~ spam
---
raw text
~~~

~~~ spam
...
raw text
~~~

## Just YAML

~~~ spam
foo: bar
bacon: True
~~~

## Both

~~~ spam
foo: bar
bacon: True
---
raw text
~~~

~~~ spam
foo: bar
bacon: True
...
raw text
~~~

## Longer delimiters

~~~ spam
foo: bar
bacon: True
.......
raw text
~~~

# Strict-YAML examples

## Just raw data

~~~ eggs
raw text
~~~

~~~ eggs
---
...
raw text
~~~

~~~ eggs
raw text
---
---
~~~

~~~ eggs
---
...
raw text
---
...
~~~

## Just YAML

~~~ eggs
---
foo: bar
bacon: True
~~~

~~~ eggs
---
foo: bar
bacon: True
...
~~~

## Both

~~~ eggs
---
foo: bar
bacon: True
---
raw text
~~~

~~~ eggs
---
foo: bar
bacon: True
...
raw text
~~~

## Longer delimiters

~~~ eggs
---
foo: bar
bacon: True
-----
raw text
~~~

## Both; metadata interlinked

~~~ eggs
raw1
---
foo: bar
...
raw2
---
spam: eggs
---
this
...
is
...
all raw
~~~
