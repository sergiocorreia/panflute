from panflute import run_filter, Header


def increase_header_level(elem, doc):
    if type(elem) == Header:
        if elem.level < 6:
            elem.level += 1
        else:
            return []


def main(doc=None):
    return run_filter(increase_header_level, doc=doc)


if __name__ == "__main__":
    main()
