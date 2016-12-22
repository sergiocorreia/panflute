---
author: someone
cmd: 'pandoc --to markdown example.md -F ./remove-tables.py'
toc-depth: 2
---

# Header 1

Some *emphasized*, **bold** and ~~striken out~~ text.

## Header 2

$include(../ch2/invalid)

$include this
$include is invalid

$include valid_file

!include ../ch2/invalid

$include ../ch2/a random valid file.md

$include "quotes here"

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

### Header 3

| Variable | Mean |
|----------|------|
| Price    | 10   |
| Weight   | 12   |

lorem lorem..

| Variable | Mean |
|----------|------|
| Price    | 10   |
| Price    | 10   |
| Price    | 10   |
| Weight   | 12   |

# Another header 1

## Tables go here

$tables

## Fenced tables...

~~~ csv
title: Some Title
has-header: True
---
Col1, Col2, Col3
1, 2, 3
10, 20, 30
~~~

## Something else here

[Stack Overflow](wiki://)

[pizza](wiki://)

What is Pandoc? [Pandoc](wiki://)

the end..

