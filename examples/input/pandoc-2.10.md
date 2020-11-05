Test api changes for python 2.10

To run (on a windows install), go to the `examples\panflute` folder and type:

```
cls & pandoc --filter=pandoc-2.10.py ../input/pandoc-2.10.md
```

- See: https://github.com/jgm/pandoc/releases/tag/2.10

# Support underline tag

[this text will be underlined]{.ul}

*This text will not be underlined* but **this text will be**.
