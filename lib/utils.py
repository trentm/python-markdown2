from random import random
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


# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549
def curry(*args, **kwargs):
    function, args = args[0], args[1:]

    def result(*rest, **kwrest):
        combined = kwargs.copy()
        combined.update(kwrest)
        return function(*args + rest, **combined)

    return result


# Recipe: regex_from_encoded_pattern (1.0)
def regex_from_encoded_pattern(s):
    """'foo'    -> re.compile(re.escape('foo'))
    '/foo/'  -> re.compile('foo')
    '/foo/i' -> re.compile('foo', re.I)
    """
    if s.startswith("/") and s.rfind("/") != 0:
        # Parse it: /PATTERN/FLAGS
        idx = s.rfind("/")
        _, flags_str = s[1:idx], s[idx + 1 :]
        flag_from_char = {
            "i": re.IGNORECASE,
            "l": re.LOCALE,
            "s": re.DOTALL,
            "m": re.MULTILINE,
            "u": re.UNICODE,
        }
        flags = 0
        for char in flags_str:
            try:
                flags |= flag_from_char[char]
            except KeyError:
                raise ValueError(
                    "unsupported regex flag: '%s' in '%s' "
                    "(must be one of '%s')"
                    % (char, s, "".join(list(flag_from_char.keys())))
                )
        return re.compile(s[1:idx], flags)
    else:  # not an encoded regex
        return re.compile(re.escape(s))


# Recipe: dedent (0.1.2)
def dedentlines(lines, tabsize=8, skip_first_line=False):
    """dedentlines(lines, tabsize=8, skip_first_line=False) -> dedented lines

        "lines" is a list of lines to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    Same as dedent() except operates on a sequence of lines. Note: the
    lines list is modified **in-place**.
    """
    DEBUG = False
    if DEBUG:
        print(
            "dedent: dedent(..., tabsize=%d, skip_first_line=%r)"
            % (tabsize, skip_first_line)
        )
    margin = None
    for i, line in enumerate(lines):
        if i == 0 and skip_first_line:
            continue
        indent = 0
        for ch in line:
            if ch == " ":
                indent += 1
            elif ch == "\t":
                indent += tabsize - (indent % tabsize)
            elif ch in "\r\n":
                continue  # skip all-whitespace lines
            else:
                break
        else:
            continue  # skip all-whitespace lines
        if DEBUG:
            print("dedent: indent=%d: %r" % (indent, line))
        if margin is None:
            margin = indent
        else:
            margin = min(margin, indent)
    if DEBUG:
        print("dedent: margin=%r" % margin)

    if margin is not None and margin > 0:
        for i, line in enumerate(lines):
            if i == 0 and skip_first_line:
                continue
            removed = 0
            for j, ch in enumerate(line):
                if ch == " ":
                    removed += 1
                elif ch == "\t":
                    removed += tabsize - (removed % tabsize)
                elif ch in "\r\n":
                    if DEBUG:
                        print("dedent: %r: EOL -> strip up to EOL" % line)
                    lines[i] = lines[i][j:]
                    break
                else:
                    raise ValueError(
                        "unexpected non-whitespace char %r in "
                        "line %r while removing %d-space margin" % (ch, line, margin)
                    )
                if DEBUG:
                    print(
                        "dedent: %r: %r -> removed %d/%d" % (line, ch, removed, margin)
                    )
                if removed == margin:
                    lines[i] = lines[i][j + 1 :]
                    break
                elif removed > margin:
                    lines[i] = " " * (removed - margin) + lines[i][j + 1 :]
                    break
            else:
                if removed:
                    lines[i] = lines[i][removed:]
    return lines


def dedent(text, tabsize=8, skip_first_line=False):
    """dedent(text, tabsize=8, skip_first_line=False) -> dedented text

        "text" is the text to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    textwrap.dedent(s), but don't expand tabs to spaces
    """
    lines = text.splitlines(1)
    dedentlines(lines, tabsize=tabsize, skip_first_line=skip_first_line)
    return "".join(lines)


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    http://wiki.python.org/moin/PythonDecoratorLibrary
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__


def xml_oneliner_re_from_tab_width(tab_width):
    """Standalone XML processing instruction regex."""
    return re.compile(
        r"""
        (?:
            (?<=\n\n)       # Starting after a blank line
            |               # or
            \A\n?           # the beginning of the doc
        )
        (                           # save in $1
            [ ]{0,%d}
            (?:
                <\?\w+\b\s+.*?\?>   # XML processing instruction
                |
                <\w+:\w+\b\s+.*?/>  # namespaced single tag
            )
            [ \t]*
            (?=\n{2,}|\Z)       # followed by a blank line or end of document
        )
        """
        % (tab_width - 1),
        re.X,
    )


xml_oneliner_re_from_tab_width = memoized(xml_oneliner_re_from_tab_width)


def hr_tag_re_from_tab_width(tab_width):
    return re.compile(
        r"""
        (?:
            (?<=\n\n)       # Starting after a blank line
            |               # or
            \A\n?           # the beginning of the doc
        )
        (                       # save in \1
            [ ]{0,%d}
            <(hr)               # start tag = \2
            \b                  # word break
            ([^<>])*?           #
            /?>                 # the matching end tag
            [ \t]*
            (?=\n{2,}|\Z)       # followed by a blank line or end of document
        )
        """
        % (tab_width - 1),
        re.X,
    )


hr_tag_re_from_tab_width = memoized(hr_tag_re_from_tab_width)


def xml_escape_attr(ampersand_re, attr, skip_single_quote=True):
    """Escape the given string for use in an HTML/XML tag attribute.

    By default this doesn't bother with escaping `'` to `&#39;`, presuming that
    the tag attribute is surrounded by double quotes.
    """
    escaped = ampersand_re.sub("&amp;", attr)

    escaped = attr.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
    if not skip_single_quote:
        escaped = escaped.replace("'", "&#39;")
    return escaped


def xml_encode_email_char_at_random(ch):
    r = random()
    # Roughly 10% raw, 45% hex, 45% dec.
    # '@' *must* be encoded. I [John Gruber] insist.
    # Issue 26: '_' must be encoded.
    if r > 0.9 and ch not in "@_":
        return ch
    elif r < 0.45:
        # The [1:] is to drop leading '0': 0x63 -> x63
        return "&#%s;" % hex(ord(ch))[1:]
    else:
        return "&#%s;" % ord(ch)


def html_escape_url(attr, safe_mode=False):
    """Replace special characters that are potentially malicious in url string."""
    escaped = (attr
        .replace('"', '&quot;')
        .replace('<', '&lt;')
        .replace('>', '&gt;'))
    if safe_mode:
        escaped = escaped.replace('+', ' ')
        escaped = escaped.replace("'", "&#39;")
    return escaped