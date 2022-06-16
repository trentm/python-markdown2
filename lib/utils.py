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


def calculate_toc_html(toc):
    """Return the HTML for the current TOC.

    This expects the `_toc` attribute to have been set on this instance.
    """
    if toc is None:
        return None

    def indent():
        return "  " * (len(h_stack) - 1)

    lines = []
    h_stack = [0]  # stack of header-level numbers
    for level, id, name in toc:
        if level > h_stack[-1]:
            lines.append("%s<ul>" % indent())
            h_stack.append(level)
        elif level == h_stack[-1]:
            lines[-1] += "</li>"
        else:
            while level < h_stack[-1]:
                h_stack.pop()
                if not lines[-1].endswith("</li>"):
                    lines[-1] += "</li>"
                lines.append("%s</ul></li>" % indent())
        lines.append('%s<li><a href="#%s">%s</a>' % (indent(), id, name))
    while len(h_stack) > 1:
        h_stack.pop()
        if not lines[-1].endswith("</li>"):
            lines[-1] += "</li>"
        lines.append("%s</ul>" % indent())
    return "\n".join(lines) + "\n"
