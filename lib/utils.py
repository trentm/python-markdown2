import re


## {{{ http://code.activestate.com/recipes/577257/ (r1)

_slugify_strip_re = re.compile(r"[^\w\s-]")
_slugify_hyphenate_re = re.compile(r"[-\s]+")


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata

    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = _slugify_strip_re.sub("", value).strip().lower()
    return _slugify_hyphenate_re.sub("-", value)

## end of http://code.activestate.com/recipes/577257/ }}}
