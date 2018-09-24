# Panflute: Pythonic Pandoc Filters

This is my own fork of Panflute, from which when ever needed I'll make a pull request from the original project [Panflute](https://github.com/sergiocorreia/panflute).

- Contribution is changing the `autorun` function from `autofilter.py` so it uses a context manager from `utils` makes filter run by importing them from their original directory, and executing their main function. This respects the filter template for autorunning with `pandoc ... -F panflute`

## Note
This is a copy from the original readme just, kept what I considered necesary
 
## License

BSD3 license (following  `pandocfilters` by @jgm).

