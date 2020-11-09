---
jel: [C01, C13, C23, C55, C81]
abstract: |
    Lorem ipsum
    Ipsum lorem
title: "CEO and Firm *Fixed* Effects in a Matched Panel"
subtitle: Identification and Estimation
#author: Sergio Correia
date: March 2016
institute: Duke University

theme: metropolis
fontsize: 11pt # 14pt
foobar: true
spam: false
q1: 'asd'
q2: "ASD"

foo:
  sapo: b
  rana: d

header-includes:
  - \metroset{progressbar=frametitle}
  - \usefonttheme[onlymath]{serif}
  # - \setsansfont[BoldFont={Fira Sans SemiBold}]{Fira Sans Book} # Bolder

build: cls & pandoc slides.md --to=beamer --latex-engine=xelatex --template=templates\default.beamer --output=..\out\slides.pdf && SumatraPDF ..\out\slides.pdf
---

asd