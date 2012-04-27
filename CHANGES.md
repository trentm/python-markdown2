# python-markdown2 Changelog

## python-markdown2 1.4.3 (not yet released)

(nothing yet)


## python-markdown2 1.4.2

- [issue #84, issue #87] Fix problems with fenced-code-blocks getting
  double-processed.


## python-markdown2 1.4.1

- [issue #67] Fix an sub-`ul` inside a `ol` not working with an indent less
  than 4 spaces.

- Fix code blocks and fenced-code-blocks to work with a single leading newline
  at the start of the input.

- [issue #86, 'fenced-code-blocks' extra] Fix fenced code blocks not being
  parsed out before other syntax elements, like headers.

- [issue #83, 'fenced-code-blocks' and 'code-color' extras] Allow 'cssclass'
  code coloring option (passed to pygments) to be overridden (by
  https://github.com/kaishaku). E.g.:

        import markdown2
        html = markdown2.markdown(text,
            extras={'fenced-code-blocks': {'cssclass': 'mycode'}})


## python-markdown2 1.4.0

- [issue #64] Python 3 support! markdown2.py supports Python 2 and 3 in the
  same file without requiring install-time 2to3 transformation.


## python-markdown2 1.3.1

- [issue #80] Jython 2.2.1 support fix (by github.com/clach04)


## python-markdown2 1.3.0

- Deprecate `code-color` extra. Use the `fenced-code-block` extra and
  its cleaner mechanism for specifying the language, instead. This extra
  will be removed in v2.0 or so.

- New `fenced-code-blocks` extra. It allows a code block to not have to be
  indented by fencing it with '```' on a line before and after. Based on
  [GFM](<http://github.github.com/github-flavored-markdown/).

        Some code:

        ```
        print "hi"
        ```

  It includes support for code syntax highlighting as per GFM. This requires
  the `pygments` Python module to be on the pythonpath.

        ```python
        if True:
            print "hi"
        ```


## python-markdown2 1.2.0

- [issue #78, issue #77] Add "metadata" extra (github.com/slomo).


## python-markdown2 1.1.1

- Drop "Makefile.py" (a `mk` thing) and simplify to "Makefile".


## python-markdown2 1.1.0

- [issue #76] Ensure "smarty-pants" extra doesn't destroy image links
  and links with title text.

- [issue #72] Support reading from stdin for command line tool like any
  well-behaved unix tool, e.g.:

      $ echo '*hi*' | markdown2
      <p><em>hi</em></p>

  Thanks Ryan!

- Drop this "1.0.1.*" version silliness. The idea *was* that the first three
  numbers tracked the Markdown.pl on which markdown2.py was originally based.
  I don't believe Markdown.pl really gets releases anymore tho, so pointless.


## python-markdown2 1.0.1.19

- [Issue 66] Add "wiki-tables" extra for Google Code Wiki-style tables.
  See <http://code.google.com/p/support/wiki/WikiSyntax#Tables>.


## python-markdown2 1.0.1.18

- [Issue 57] Add html5 block tags (article, section, aside, et al; see
  "_html5tags" variable) to Markdown literal HTML block tag handling. Thanks
  Tim Gray!

- [Issue 56] Fix `setup.py install`.

- [Issue 54] Fix escaping of link title attributes. Thanks FND!

- Tweak list matching to NOT make a ul for something like this:

        - - - - - hi there

  Before this change this would be a silly 5-deep nested li. See
  "not_quite_a_list" test case.

- [Issue 52] Fix potential pathologically slow matching for `<hr>` markdown
  ("slow_hr" test case).

- Add a `Markdown.postprocess(text) -> text` hook that is called near the end
  of markdown conversion. By default this does no transformation. It is called
  just before unescaping of special characters and unhashing of literal HTML
  blocks.

- ["header-ids" and "toc" extras] Add "n" argument to
  `Markdown.header_id_from_text` hook. This allows a subclass using this hook
  to differentiate the header id based on the hN number (e.g. h1 diff that
  h2). Also allow a `None` return value to not add an id to that header (and
  exclude that header from the TOC).

  Note: If you used this hook, this is an incompatible change to the call
  signature.

- Add a "markdown-in-html" extra similar to (but limited)
  <http://michelf.com/projects/php-markdown/extra/#markdown-attr>. I.e. this:

        <div markdown="1">
        Yo **yo**!
        </div>

  becomes:

        <div>

        Yo <strong>yo</strong>!

        </div>

- [Issue 39] Test case fix for pygments 1.3.1 from thomas.moschny.

- [Issue 42] Add "smarty-pants" extra for transforming plain ASCII
  punctuation characters into smart typographic punctuation HTML entities.
  Inspiration: <http://daringfireball.net/projects/smartypants/>
  Implementation by Nikhil Chelliah. Also add `\'` and `\"` escape sequences
  for forcing dumb quotes when this extra is in use.

- Guard against using `True` instead of `None` as follows
  `markdown(..., extras={'header-ids': True})`. `None` is wanted, but `True`
  is commonly (at least I did it twice) used.


## python-markdown2 1.0.1.17

- [Issue 36] Fix "cuddled-lists" extra handling for an
  looks-like-a-cuddled-list-but-is-indented block. See the
  "test/tm-cases/cuddled_list_indented.text" test case.

- Experimental new "toc" extra. The returned string from conversion will have
  a `toc_html` attribute.

- New "header-ids" extra that will add an `id` attribute to headers:

        # My First Section

  will become:

        <h1 id="my-first-section">My First Section</h1>

  An argument can be give for the extra, which will be used as a prefix for
  the ids:

        $ cat foo.txt
        # hi there
        $ python markdown2.py foo.txt
        <h1>hi there</h1>
        $ python markdown2.py foo.txt -x header-ids
        <h1 id="hi-there">hi there</h1>
        $ python markdown2.py foo.txt -x header-ids=prefix
        <h1 id="prefix-hi-there">hi there</h1>

- Preliminary support for "html-classes" extra: takes a dict mapping HTML tag
  to the string value to use for a "class" attribute for that emitted tag.
  Currently just supports "pre" and "code" for code *blocks*.


## python-markdown2 1.0.1.16

- [Issue 33] Implement a "cuddled-lists" extra that allows:

        I did these things:
        * bullet1
        * bullet2
        * bullet3

  to be converted to:

        <p>I did these things:</p>

        <ul>
        <li>bullet1</li>
        <li>bullet2</li>
        <li>bullet3</li>
        </ul>


## python-markdown2 1.0.1.15

- [Issue 30] Fix a possible XSS via JavaScript injection in a carefully
  crafted image reference (usage of double-quotes in the URL).

## python-markdown2 1.0.1.14

- [Issue 29] Fix security hole in the md5-hashing scheme for handling HTML
  chunks during processing.
- [Issue 27] Fix problem with underscores in footnotes content (with
  "footnotes" extra).

## python-markdown2 1.0.1.13

- [Issue 24] Set really long sentinel for max-length of link text to avoid
  problems with reasonably long ones.
- [Issue 26] Complete the fix for this issue. Before this change the
  randomized obscuring of 'mailto:' link letters would sometimes result
  in emails with underscores getting misinterpreted as for italics.

## python-markdown2 1.0.1.12

- [Issue 26] Fix bug where email auto linking wouldn't work for emails with
  underscores. E.g. `Mail me: <foo_bar@example.com>` wouldn't work.
- Update MANIFEST.in to ensure bin/markdown2 gets included in sdist.
- [Issue 23] Add support for passing options to pygments for the "code-color"
  extra. For example:

        >>> markdown("...", extras={'code-color': {"noclasses": True}})

  This `formatter_opts` dict is passed to the pygments HtmlCodeFormatter.
  Patch from 'svetlyak.40wt'.
- [Issue 21] Escape naked '>' characters, as is already done for '&' and '<'
  characters. Note that other markdown implementations (both Perl and PHP) do
  *not* do this. This results in differing output with two 3rd-party tests:
  "php-markdown-cases/Backslash escapes.text" and "markdowntest-cases/Amps
  and angle encoding.tags".
- "link-patterns" extra: Add support for the href replacement being a
  callable, e.g.:

        >>> link_patterns = [
        ...     (re.compile("PEP\s+(\d+)", re.I),
        ...      lambda m: "http://www.python.org/dev/peps/pep-%04d/" % int(m.group(1))),
        ... ]
        >>> markdown2.markdown("Here is PEP 42.", extras=["link-patterns"],
        ...     link_patterns=link_patterns)
        u'<p>Here is <a href="http://www.python.org/dev/peps/pep-0042/">PEP 42</a>.</p>\n'

## python-markdown2 1.0.1.11

- Fix syntax_color test for the latest Pygments.
- [Issue 20] Can't assume that `sys.argv` is defined at top-level code --
  e.g. when used at a PostreSQL stored procedure. Fix that.

## python-markdown2 1.0.1.10

- Fix sys.path manipulation in setup.py so `easy_install markdown2-*.tar.gz`
  works. (Henry Precheur pointed out the problem.)
- "bin/markdown2" is now a stub runner script rather than a symlink to
  "lib/markdown2.py". The symlink was a problem for sdist: tar makes it a
  copy.
- Added 'xml' extra: passes *one-liner* XML processing instructions and
  namespaced XML tags without wrapping in a `<p>` -- i.e. treats them as a HTML
  block tag.

## python-markdown2 1.0.1.9

- Fix bug in processing text with two HTML comments, where the first comment
  is cuddled to other content. See "test/tm-cases/two_comments.text". Noted
  by Wolfgang Machert.
- Revert change in v1.0.1.6 passing XML processing instructions and one-liner
  tags. This changed caused some bugs. Similar XML processing support will
  make it back via an "xml" extra.

## python-markdown2 1.0.1.8

- License note updates to facilitate Thomas Moschny building a package for
  Fedora Core Linux. No functional change.

## python-markdown2 1.0.1.7

- Add a proper setup.py and release to pypi:
  http://pypi.python.org/pypi/markdown2/
- Move markdown2.py module to a lib subdir. This allows one to put the "lib"
  dir of a source checkout (e.g. via an svn:externals) on ones Python Path
  without have the .py files at the top-level getting in the way.

## python-markdown2 1.0.1.6

- Fix Python 2.6 deprecation warning about the `md5` module.
- Pass XML processing instructions and one-liner tags. For example:

        <?blah ...?>
        <xi:include xmlns:xi="..." />

  Limitations: they must be on one line. Test: pi_and_xinclude.
  Suggested by Wolfgang Machert.

## python-markdown2 1.0.1.5

- Add ability for 'extras' to have arguments. Internally the 'extras'
  attribute of the Markdown class is a dict (it was a set).
- Add "demote-headers" extra that will demote the markdown for, e.g., an h1
  to h2-6 by the number of the demote-headers argument.

        >>> markdown('# this would be an h1', extras={'demote-headers': 2})
        u'<h3>this would be an h1</h3>\n'

  This can be useful for user-supplied Markdown content for a sub-section of
  a page.

## python-markdown2 1.0.1.4

- [Issue 18] Allow spaces in the URL for link definitions.
- [Issue 15] Fix some edge cases with backslash-escapes.
- Fix this error that broken command-line usage:

        NameError: global name 'use_file_vars' is not defined

- Add "pyshell" extra for auto-codeblock'ing Python interactive shell
  sessions even if they weren't properly indented by the tab width.

## python-markdown2 1.0.1.3

- Make the use of the `-*- markdown-extras: ... -*-` emacs-style files
  variable to set "extras" **off** be default. It can be turned on via
  `--use-file-vars` on the command line and `use_file_vars=True` via the
  module interface.
- [Issue 3] Drop the code-color extra hack added *for* issue3 that was
  causing the a unicode error with unicode in a code-colored block,
  <http://code.google.com/p/python-markdown2/issues/detail?id=3#c8>

## python-markdown2 1.0.1.2

- [Issue 8] Alleviate some of the incompat of the last change by allowing (at
  the Python module level) the usage of `safe_mode=True` to mean what it used
  to -- i.e. "replace" safe mode.
- [Issue 8, **incompatible change**] The "-s|--safe" command line option and
  the equivalent "safe_mode" option has changed semantics to be a string
  instead of a boolean. Legal values of the string are "replace" (the old
  behaviour: literal HTML is replaced with "[HTML_REMOVED]") and "escape"
  (meta chars in literal HTML is escaped).
- [Issue 11] Process markup in footnote definition bodies.
- Add support for `-*- markdown-extras: ... -*-` emacs-style files variables
  (typically in an XML comment) to set "extras" for the markdown conversion.
- [Issue 6] Fix problem with footnotes if the reference string had uppercase
  letters.

## python-markdown2 1.0.1.1

- [Issue 3] Fix conversion of unicode strings.
- Make the "safe_mode" replacement test overridable via subclassing: change
  `Markdown.html_removed_text`.
- [Issue 2] Fix problems with "safe_mode" removing generated HTML, instead of
  just raw HTML in the text.
- Add "-s|--safe" command-line option to set "safe_mode" conversion
  boolean. This option is mainly for compat with markdown.py.
- Add "link-patterns" extra: allows one to specify a list of regexes that
  should be automatically made into links. For example, one can define a
  mapping for things like "Mozilla Bug 1234":

        regex:  mozilla\s+bug\s+(\d+)
        href:   http://bugzilla.mozilla.org/show_bug.cgi?id=\1

  See <https://github.com/trentm/python-markdown2/wiki/Extras> for details.
- Add a "MarkdownWithExtras" class that enables all extras (except
  "code-friendly"):

        >>> import markdown2
        >>> converter = markdown2.MarkdownWithExtras()
        >>> converter.convert('...TEXT...')
        ...HTML...

- [Issue 1] Added "code-color" extra: pygments-based (TODO: link) syntax
  coloring of code blocks. Requires the pygments Python library on sys.path.
  See <https://github.com/trentm/python-markdown2/wiki/Extras> for details.
- [Issue 1] Added "footnotes" extra: adds support for footnotes syntax. See
  <https://github.com/trentm/python-markdown2/wiki/Extras> for details.

## python-markdown2 1.0.1.0

- Added "code-friendly" extra: disables the use of leading and trailing `_`
  and `__` for emphasis and strong. These can easily get in the way when
  writing docs about source code with variable_list_this and when one is not
  careful about quoting.
- Full basic Markdown syntax.


(Started maintaining this log 15 Oct 2007. At that point there had been no
releases of python-markdown2.)
