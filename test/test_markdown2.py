#!/usr/bin/env python
# Copyright (c) 2007-2008 ActiveState Software Inc.
# License: MIT (http://www.opensource.org/licenses/mit-license.php)

"""Test the Python markdown2.py."""

import os
import sys
from os.path import join, dirname, abspath, exists, splitext, basename
import re
from glob import glob
from pprint import pprint
import unittest
import codecs
import difflib
import doctest
from json import loads as json_loads

from testlib import TestError, TestSkipped, tag

sys.path.insert(0, join(dirname(dirname(abspath(__file__)))))
try:
    import markdown2
finally:
    del sys.path[0]



#---- Python version compat

# Use `bytes` for byte strings and `unicode` for unicode strings (str in Py3).
if sys.version_info[0] <= 2:
    py3 = False
    try:
        bytes
    except NameError:
        bytes = str
    base_string_type = basestring
elif sys.version_info[0] >= 3:
    py3 = True
    unicode = str
    base_string_type = str
    unichr = chr



#---- Test cases

class _MarkdownTestCase(unittest.TestCase):
    """Helper class for Markdown tests."""

    maxDiff = None

    def _assertMarkdownParity(self, text):
        """Assert that markdown2.py produces same output as Markdown.pl."""
        #TODO add normalization
        python_html = markdown2.markdown(text)
        perl_html = _markdown_with_perl(text)

        close_though = ""
        if python_html != perl_html \
           and (python_html.replace('\n', '')
                == perl_html.replace('\n', '')):
            close_though = " (close though -- all but EOLs match)"

        self.assertEqual(python_html, perl_html, _dedent("""\
            markdown2.py didn't produce the same output as Markdown.pl%s:
              ---- text ----
            %s  ---- Python markdown2.py HTML ----
            %s  ---- Perl Markdown.pl HTML ----
            %s""") % (close_though, _display(text),
                      _display(python_html), _display(perl_html)))

    def _assertMarkdownPath(self, text_path, encoding="utf-8", opts=None,
            toc_html_path=None, metadata_path=None):
        text = codecs.open(text_path, 'r', encoding=encoding).read()
        html_path = splitext(text_path)[0] + ".html"
        html = codecs.open(html_path, 'r', encoding=encoding).read()
        extra = {}
        if toc_html_path:
            extra["toc_html"] = codecs.open(toc_html_path, 'r', encoding=encoding).read()
            extra["toc_html_path"] = toc_html_path
        if metadata_path:
            extra["metadata"] = json_loads(
                codecs.open(metadata_path, 'r', encoding=encoding).read())
            extra["metadata_path"] = metadata_path
        self._assertMarkdown(text, html, text_path, html_path, opts=opts, **extra)

    def _assertMarkdown(self, text, html, text_path=None, html_path=None,
            opts=None, toc_html=None, toc_html_path=None, metadata=None,
            metadata_path=None):
        """Assert that markdown2.py produces the expected HTML."""
        if text_path is None: text_path = "<text content>"
        if html_path is None: html_path = "<html content>"
        if opts is None:
            opts = {}

        norm_html = norm_html_from_html(html)
        python_html = markdown2.markdown(text, **opts)
        python_norm_html = norm_html_from_html(python_html)

        close_though = ""
        if python_norm_html != norm_html \
           and (python_norm_html.replace('\n', '')
                == norm_html.replace('\n', '')):
            close_though = " (close though -- all but EOLs match)"

        diff = ''
        if python_norm_html != norm_html:
            diff = difflib.unified_diff(
                    norm_html.splitlines(1),
                    python_norm_html.splitlines(1),
                    html_path,
                    "markdown2 "+text_path)
            diff = ''.join(diff)
        errmsg = _dedent("""\
            markdown2.py didn't produce the expected HTML%s:
              ---- text (escaping: .=space, \\n=newline) ----
            %s  ---- Python markdown2.py HTML (escaping: .=space, \\n=newline) ----
            %s  ---- expected HTML (escaping: .=space, \\n=newline) ----
            %s  ---- diff ----
            %s""") % (close_though, _display(text),
                      _display(python_html), _display(html),
                      _indent(diff))

        def charreprreplace(exc):
            if not isinstance(exc, UnicodeEncodeError):
                raise TypeError("don't know how to handle %r" % exc)
            if py3:
                obj_repr = repr(exc.object[exc.start:exc.end])[1:-1]
            else:
                # repr -> remote "u'" and "'"
                obj_repr = repr(exc.object[exc.start:exc.end])[2:-1]
            return (unicode(obj_repr), exc.end)
        codecs.register_error("charreprreplace", charreprreplace)

        self.assertEqual(python_norm_html, norm_html, errmsg)

        if toc_html:
            python_toc_html = python_html.toc_html
            python_norm_toc_html = norm_html_from_html(python_toc_html)
            norm_toc_html = norm_html_from_html(toc_html)

            diff = ''
            if python_norm_toc_html != norm_toc_html:
                diff = difflib.unified_diff(
                        norm_toc_html.splitlines(1),
                        python_norm_toc_html.splitlines(1),
                        toc_html_path,
                        "`markdown2 %s`.toc_html" % text_path)
                diff = ''.join(diff)
            errmsg = _dedent("""\
                markdown2.py didn't produce the expected TOC HTML%s:
                  ---- text (escaping: .=space, \\n=newline) ----
                %s  ---- Python markdown2.py TOC HTML (escaping: .=space, \\n=newline) ----
                %s  ---- expected TOC HTML (escaping: .=space, \\n=newline) ----
                %s  ---- diff ----
                %s""") % (close_though, _display(text),
                          _display(python_toc_html), _display(toc_html),
                          _indent(diff))
            self.assertEqual(python_norm_toc_html, norm_toc_html,
                errmsg.encode('utf-8', 'charreprreplace'))

        if metadata:
            self.assertEqual(python_html.metadata, metadata)

    def generate_tests(cls):
        """Add test methods to this class for each test file in
        `cls.cases_dir'.
        """
        cases_pat = join(dirname(__file__), cls.cases_dir, "*.text")
        for text_path in glob(cases_pat):
            # Load an options (`*.opts` file, if any).
            # It must be a Python dictionary. It will be passed as
            # kwargs to the markdown function.
            opts = {}
            opts_path = splitext(text_path)[0] + ".opts"
            if exists(opts_path):
                try:
                    opts = eval(open(opts_path, 'r').read())
                except Exception:
                    _, ex, _ = sys.exc_info()
                    print("WARNING: couldn't load `%s' opts file: %s" \
                          % (opts_path, ex))

            toc_html_path = splitext(text_path)[0] + ".toc_html"
            if not exists(toc_html_path):
                toc_html_path = None
            metadata_path = splitext(text_path)[0] + ".metadata"
            if not exists(metadata_path):
                metadata_path = None

            test_func = lambda self, t=text_path, o=opts, c=toc_html_path, \
                    m=metadata_path: \
                    self._assertMarkdownPath(t, opts=o, toc_html_path=c,
                          metadata_path=m)

            tags_path = splitext(text_path)[0] + ".tags"
            if exists(tags_path):
                tags = []
                for line in open(tags_path):
                    if '#' in line: # allow comments in .tags files
                        line = line[:line.index('#')]
                    tags += line.split()
                test_func.tags = tags

            name = splitext(basename(text_path))[0]
            name = name.replace(' - ', '_')
            name = name.replace(' ', '_')
            name = re.sub("[(),]", "", name)
            test_name = "test_%s" % name
            setattr(cls, test_name, test_func)
    generate_tests = classmethod(generate_tests)

class TMTestCase(_MarkdownTestCase):
    cases_dir = "tm-cases"

class MarkdownTestTestCase(_MarkdownTestCase):
    """Test cases from MarkdownTest-1.0."""
    cases_dir = "markdowntest-cases"

class PHPMarkdownTestCase(_MarkdownTestCase):
    """Test cases from MDTest."""
    cases_dir = "php-markdown-cases"

class PHPMarkdownExtraTestCase(_MarkdownTestCase):
    """Test cases from MDTest.

    These are all knownfailures because these test non-standard Markdown
    syntax no implemented in markdown2.py.  See
    <http://www.michelf.com/projects/php-markdown/extra/> for details.
    """
    __tags__ = ["knownfailure"]
    cases_dir = "php-markdown-extra-cases"


class DirectTestCase(_MarkdownTestCase):
    """These are specific test that I found were broken in
    Python-markdown (markdown.py).
    """

    def test_slow_hr(self):
        import time
        text = """\
* * *

This on *almost* looks like an hr, except for the trailing '+'. In older
versions of markdown2.py this was pathologically slow:

- - - - - - - - - - - - - - - - - - - - - - - - - +
"""
        html = """\
<hr />

<p>This on <em>almost</em> looks like an hr, except for the trailing '+'. In older
versions of markdown2.py this was pathologically slow:</p>

<p>- - - - - - - - - - - - - - - - - - - - - - - - - +</p>
"""
        start = time.time()
        self._assertMarkdown(text, html)
        end = time.time()
        delta = end - start
        self.assertTrue(delta < 1.0, "It took more than 1s to process "
            "'slow-hr'. It took %.2fs. Too slow!" % delta)
    test_slow_hr.tags = ["perf"]

    def test_code_in_strong(self):
        self._assertMarkdown(
            '**look at `this code` call**',
            '<p><strong>look at <code>this code</code> call</strong></p>\n')
    test_code_in_strong.tags = ["code", "strong"]

    def test_starter_pre(self):
        self._assertMarkdown(
            _indent('#!/usr/bin/python\nprint "hi"'),
            '<pre><code>#!/usr/bin/python\nprint "hi"\n</code></pre>\n')
    test_starter_pre.tags = ["pre", "recipes"]

    def test_pre(self):
        self._assertMarkdown(_dedent('''\
            some starter text

                #!/usr/bin/python
                print "hi"'''),
            '<p>some starter text</p>\n\n<pre><code>#!/usr/bin/python\nprint "hi"\n</code></pre>\n')

    def test_russian(self):
        ko = '\u043b\u0449' # 'ko' on russian keyboard
        self._assertMarkdown("## %s" % ko,
            '<h2>%s</h2>\n' % ko)
    test_russian.tags = ["unicode", "issue3"]


class DocTestsTestCase(unittest.TestCase):
    def test_api(self):
        test = doctest.DocFileTest("api.doctests")
        test.runTest()

    # Don't bother on Python 3 because (a) there aren't many inline doctests,
    # and (b) they are more to be didactic than comprehensive test suites.
    if not py3:
        def test_internal(self):
            doctest.testmod(markdown2)



#---- internal support stuff

_xml_escape_re = re.compile(r'&#(x[0-9A-Fa-f]{2,3}|[0-9]{2,3});')
def _xml_escape_sub(match):
    escape = match.group(1)
    if escape[0] == 'x':
        return unichr(int('0'+escape, base=16))
    else:
        return unichr(int(escape))

_markdown_email_link_re = re.compile(r'<a href="(.*?&#.*?)">(.*?)</a>', re.U)
def _markdown_email_link_sub(match):
    href, text = match.groups()
    href = _xml_escape_re.sub(_xml_escape_sub, href)
    text = _xml_escape_re.sub(_xml_escape_sub, text)
    return '<a href="%s">%s</a>' % (href, text)

def norm_html_from_html(html):
    """Normalize (somewhat) Markdown'd HTML.

    Part of Markdown'ing involves obfuscating email links with
    randomize encoding. Undo that obfuscation.

    Also normalize EOLs.
    """
    if not isinstance(html, unicode):
        html = html.decode('utf-8')
    html = _markdown_email_link_re.sub(
        _markdown_email_link_sub, html)
    if sys.platform == "win32":
        html = html.replace('\r\n', '\n')
    return html


def _display(s):
    """Markup the given string for useful display."""
    if not isinstance(s, unicode):
        s = s.decode("utf-8")
    s = _indent(_escaped_text_from_text(s, "whitespace"), 4)
    if not s.endswith('\n'):
        s += '\n'
    return s

def _markdown_with_perl(text):
    markdown_pl = join(dirname(__file__), "Markdown.pl")
    if not exists(markdown_pl):
        raise OSError("`%s' does not exist: get it from "
                      "http://daringfireball.net/projects/markdown/"
                      % markdown_pl)

    i, o = os.popen2("perl %s" % markdown_pl)
    i.write(text)
    i.close()
    html = o.read()
    o.close()
    return html


# Recipe: dedent (0.1.2)
def _dedentlines(lines, tabsize=8, skip_first_line=False):
    """_dedentlines(lines, tabsize=8, skip_first_line=False) -> dedented lines

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
        print("dedent: dedent(..., tabsize=%d, skip_first_line=%r)"\
              % (tabsize, skip_first_line))
    indents = []
    margin = None
    for i, line in enumerate(lines):
        if i == 0 and skip_first_line: continue
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += tabsize - (indent % tabsize)
            elif ch in '\r\n':
                continue # skip all-whitespace lines
            else:
                break
        else:
            continue # skip all-whitespace lines
        if DEBUG: print("dedent: indent=%d: %r" % (indent, line))
        if margin is None:
            margin = indent
        else:
            margin = min(margin, indent)
    if DEBUG: print("dedent: margin=%r" % margin)

    if margin is not None and margin > 0:
        for i, line in enumerate(lines):
            if i == 0 and skip_first_line: continue
            removed = 0
            for j, ch in enumerate(line):
                if ch == ' ':
                    removed += 1
                elif ch == '\t':
                    removed += tabsize - (removed % tabsize)
                elif ch in '\r\n':
                    if DEBUG: print("dedent: %r: EOL -> strip up to EOL" % line)
                    lines[i] = lines[i][j:]
                    break
                else:
                    raise ValueError("unexpected non-whitespace char %r in "
                                     "line %r while removing %d-space margin"
                                     % (ch, line, margin))
                if DEBUG:
                    print("dedent: %r: %r -> removed %d/%d"\
                          % (line, ch, removed, margin))
                if removed == margin:
                    lines[i] = lines[i][j+1:]
                    break
                elif removed > margin:
                    lines[i] = ' '*(removed-margin) + lines[i][j+1:]
                    break
            else:
                if removed:
                    lines[i] = lines[i][removed:]
    return lines

def _dedent(text, tabsize=8, skip_first_line=False):
    """_dedent(text, tabsize=8, skip_first_line=False) -> dedented text

        "text" is the text to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    textwrap.dedent(s), but don't expand tabs to spaces
    """
    lines = text.splitlines(1)
    _dedentlines(lines, tabsize=tabsize, skip_first_line=skip_first_line)
    return ''.join(lines)

# Recipe: indent (0.2.1)
def _indent(s, width=4, skip_first_line=False):
    """_indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)


# Recipe: text_escape (0.1)
def _escaped_text_from_text(text, escapes="eol"):
    r"""Return escaped version of text.

        "escapes" is either a mapping of chars in the source text to
            replacement text for each such char or one of a set of
            strings identifying a particular escape style:
                eol
                    replace EOL chars with '\r' and '\n', maintain the actual
                    EOLs though too
                whitespace
                    replace EOL chars as above, tabs with '\t' and spaces
                    with periods ('.')
                eol-one-line
                    replace EOL chars with '\r' and '\n'
                whitespace-one-line
                    replace EOL chars as above, tabs with '\t' and spaces
                    with periods ('.')
    """
    #TODO:
    # - Add 'c-string' style.
    # - Add _escaped_html_from_text() with a similar call sig.
    import re

    if isinstance(escapes, base_string_type):
        if escapes == "eol":
            escapes = {'\r\n': "\\r\\n\r\n", '\n': "\\n\n", '\r': "\\r\r"}
        elif escapes == "whitespace":
            escapes = {'\r\n': "\\r\\n\r\n", '\n': "\\n\n", '\r': "\\r\r",
                       '\t': "\\t", ' ': "."}
        elif escapes == "eol-one-line":
            escapes = {'\n': "\\n", '\r': "\\r"}
        elif escapes == "whitespace-one-line":
            escapes = {'\n': "\\n", '\r': "\\r", '\t': "\\t", ' ': '.'}
        else:
            raise ValueError("unknown text escape style: %r" % escapes)

    # Sort longer replacements first to allow, e.g. '\r\n' to beat '\r' and
    # '\n'.
    escapes_keys = list(escapes.keys())
    escapes_keys.sort(key=lambda a: len(a), reverse=True)
    def repl(match):
        val = escapes[match.group(0)]
        return val
    escaped = re.sub("(%s)" % '|'.join([re.escape(k) for k in escapes_keys]),
                     repl,
                     text)

    return escaped

def _one_line_summary_from_text(text, length=78,
        escapes={'\n':"\\n", '\r':"\\r", '\t':"\\t"}):
    r"""Summarize the given text with one line of the given length.

        "text" is the text to summarize
        "length" (default 78) is the max length for the summary
        "escapes" is a mapping of chars in the source text to
            replacement text for each such char. By default '\r', '\n'
            and '\t' are escaped with their '\'-escaped repr.
    """
    if len(text) > length:
        head = text[:length-3]
    else:
        head = text
    escaped = _escaped_text_from_text(head, escapes)
    if len(text) > length:
        summary = escaped[:length-3] + "..."
    else:
        summary = escaped
    return summary


#---- hook for testlib

def test_cases():
    """This is called by test.py to build up the test cases."""
    TMTestCase.generate_tests()
    yield TMTestCase
    MarkdownTestTestCase.generate_tests()
    yield MarkdownTestTestCase
    PHPMarkdownTestCase.generate_tests()
    yield PHPMarkdownTestCase
    PHPMarkdownExtraTestCase.generate_tests()
    yield PHPMarkdownExtraTestCase
    yield DirectTestCase
    yield DocTestsTestCase
