# python-markdown2 Changelog

## python-markdown2 2.4.5

- [pull #466] Add optional dependencies to `setup.py`


## python-markdown2 2.4.4

- [pull #439] Fix TypeError if html-classes extra is None
- [pull #441] Remove Python2 support
- [pull #445] Replace `<strike>` with `<s>` in strike extra
- [pull #446] Fix link patterns extra applying within links
- [pull #443] create proper entry point
- [pull #449] Codespans inside link text issue344
- [pull #451] Underline and HTML comments
- [pull #453] Links with brackets
- [pull #454] Fix emacs local variable one-liners
- [pull #457] Example of the current mixed-paragraph mode behavior in lists
- [pull #455] Fix code block indentation in lists
- [pull #434] Fix filter bypass leading to XSS (#362)
- [pull #464] Fix html-classes extra not applying to code spans
- [pull #462] Fix pygments block matching
- [pull #462] Fix pyshell blocks in blockquotes
- [pull #463] Fix multilevel lists
- [pull #468] Remove `_uniform_outdent_limit` function
- [pull #470] Add support for ordered lists that don't start at 1. (#469)
- [pull #472] Fix `AssertionError` with lazy numbered lists (issue #471)
- [pull #475] Add `<ul>` and `<ol>` tags to html-classes extra (#352)
- [pull #473] XSS test and fix


## python-markdown2 2.4.3

- [pull #413] Fix meta indentation
- [pull #414] Fix code surrounded by blank lines inside blockquote fenced code blocks
- [pull #417] Fix inline code pipe symbol within tables (issue #399)
- [pull #418] Fix code block parsing error (issue #327)
- [pull #419] Fix hr block created when not supposed to (issue #400)
- [pull #421] Fix backslashes removed by adjacent code blocks (issues #369 and #412)
- [pull #420] Fix md5-* in resulting HTML when several code blocks follow one by one (issue #355)
- [pull #422] Fix excessive `<br>` tags in lists using break-on-newline extra (issue #394)
- [pull #424] Standardize key and value definitions for metadata extra (issue #423)
- [pull #427] Fix fenced code blocks breaking lists (issue #426)
- [pull #429] Fix catastrophic backtracking (Regex DoS) in pyshell blocks.
- [pull #431] Fix incorrect indentation of fenced code blocks within lists
- [pull #436] RST admonitions
- [pull #430] Improve error message if link_patterns forgotten
- [pull #437] fix compatibility with pygments 2.12


## python-markdown2 2.4.2

- [pull #408] Fix for fenced code blocks issue #396
- [pull #410] Be more strict on auto linking urls, RE DOS fix


## python-markdown2 2.4.1

- [pull #389] Tables extra: allow whitespace at the end of the underline row
- [pull #392] Pyshell extra: enable syntax highlighting if `fenced-code-blocks` is loaded.
- [pull #402] Regex DOS bandaid fix


## python-markdown2 2.4.0

- [pull #377] Fixed bug breaking strings elements in metadata lists
- [pull #380] When rendering fenced code blocks, also add the `language-LANG` class
- [pull #387] Regex DoS fixes


## python-markdown2 2.3.10

- [pull #356] Don't merge sequential quotes into a single blockquote
- [pull #357] use style=text-align for table alignment
- [pull #360] introduce underline extra
- [pull #368] Support for structured and nested values in metadata
- [pull #371] add noopener to external links


## python-markdown2 2.3.9

- [pull #335] Added header support for wiki tables
- [pull #336] Reset _toc when convert is run
- [pull #353] XSS fix
- [pull #350] XSS fix


## python-markdown2 2.3.8

- [pull #317] Temporary fix to issue #150
- [pull #319] Stop XML escaping the body of a link
- [pull #322] Don't auto link patterns surrounded by triple quotes
- [pull #324] Add class configurability to the enclosing tag
- [pull #328] Accept [X] as marked task


## python-markdown2 2.3.7

- [pull #306] Drop support for legacy Python versions
- [pull #307] Fix syntax highlighting test cases that depend on Pygments output
- [pull #308] Add support for Python 3.7
- [pull #304] Add Wheel package support
- [pull #312] Fix toc_depth initialization regression
- [pull #315] XSS fix


## python-markdown2 2.3.6

- [pull #282] Add TOC depth option
- [pull #283] Fix to add TOC html to output via CLI
- [pull #284] Do not remove anchors in safe_mode
- [pull #288] fixing cuddled-lists with a single list item
- [pull #292] Fix Wrong rendering of last list element
- [pull #295] link-patterns fix
- [pull #300] Replace a deprecated method
- [pull #301] DeprecationWarning: invalid escape sequence
- [pull #302] Fix "make test" in Python 3
- [pull #303] Fix CVE-2018-5773


## python-markdown2 2.3.5

- [pull #238] Fenced code blocks lang with leading space
- [pull #260] Search for items only within metadata header
- [pull #264] highlightjs language class support
- [pull #265] FIPS compliance
- [pull #274] Fix for double amp replacement inside link title


## python-markdown2 2.3.4

- [pull #243] task list extra visual changes
- [pull #245] Don't let "target-blank-lines" break footnotes
- [pull #247] Translatable footnote titles
- [pull #252] Add pipe escaping in table extension


## python-markdown2 2.3.3

- [pull #236] Fix for safe_mode links regression
- [pull #235] Fix for overgreedy regex in metadata
- [pull #237] Fix for header-ids extra non-alpha character issue


## python-markdown2 2.3.2

- [pull #204] toc extra Python 3 error
- [pull #207] Performance improvements
- [pull #210] Leading paragraph with fenced code blocks
- [pull #212] Target blank links extra
- [pull #215] Optional metadata fences
- [pull #218] Github style task list
- [pull #220] Numbering extra
- [pull #224] Metadata in blocks
- [pull #230] safe_mode changes


## python-markdown2 2.3.1

- [pull #131] Markdown "spoiler" extra
- [pull #170] html-classes support for table tags
- [pull #190] "strike" extra
- [pull #201] Allow empty table cells


## python-markdown2 2.3.0

- New "tables" extra for table syntax that matches GFM
  <https://help.github.com/articles/github-flavored-markdown#tables> and
  PHP-Markdown Extra <https://michelf.ca/projects/php-markdown/extra/#table>.
  For example:

        | Header 1 | *Header* 2 |
        | -------- | -------- |
        | `Cell 1` | [Cell 2](http://example.com) link |
        | Cell 3   | **Cell 4** |

  See <https://github.com/trentm/python-markdown2/blob/master/test/tm-cases/tables.text>
  for examples and edge cases.

  If you have documents using the 'wiki-tables' syntax and want to convert to the
  'tables' syntax, there is a script to help with that here:
  <https://github.com/trentm/python-markdown2/blob/master/tools/wiki-tables-to-tables.py>


## python-markdown2 2.2.3

- [issue #165] Fix an edge case in list parsing.


## python-markdown2 2.2.2

- [pull #156] Footnotes XML compatibility.
- [pull #157] Horizontal rule minimum length.
- [pull #162] Fix escaping fenced code block with safe mode
- [pull #163] Fix code highlight with safe mode


## python-markdown2 2.2.1

- [issue #142 pull #141] Fix parentheses and spaces in urls.
- [issue #88 issue #95 pull #145] Fix code blocks in code blocks with syntax highlighting.
- [issue #113 issue #127 via pull #144] Fix fenced-code-blocks html and code output.
- [pull #133] Unify the -/= and ## style headers and fix TOC order
- [pull #146] tag-friendly extra to require that atx headers have a space after #


## python-markdown2 2.2.0

- [issue #135] Fix fenced code blocks odd rendering.
- [pull #138] specify shell in Makefile
- [pull #130] break-on-newline extra
- [pull #140] Allow html-classes for img
- [pull #122] Allow parentheses in urls


## python-markdown2 2.1.0

- ["nofollow" extra, issue #74, pull #104] Add `rel="nofollow"` support
  (mostly by https://github.com/cdman):

        $ echo '[link](http://example)' | markdown2 -x nofollow
        <p><a rel="nofollow" href="http://example">link</a></p>

   Limitation: This *can* add a duplicate 'rel' attribute to raw HTML links
   in the input.

## python-markdown2 2.0.1

- ["toc" extra] Unescape Markdown special chars in TOC entries. See
  <https://github.com/trentm/restdown/issues/15>.

- Now 'tox' testing support (by github.com/msabramo):

        [sudo] pip install tox
        tox

  confirming that markdown2 works with jython (not sure which version) and
  pypy!  Also added pypy to travis-ci testing
  (http://travis-ci.org/#!/trentm/python-markdown2).


## python-markdown2 2.0.0

- [issue #90] Add a `Markdown.preprocess(text) -> text` hook for subclasses.
  This is a match for the `Markdown.postprocess(text) -> text` hook added in
  an earlier version. (by @joestump).

- [issue #90, backward incompatible change] Require a space between the '#'
  and a text for a title. I.e.:

        # This still works

        #This doesn't work

        ##Nor this

  This keeps comments, hash tags, and ticket numbers at the beginning of the
  line from turning into an h1. (by @joestump)

  This is a backward incompatible change, however small, hence the version
  change to 2.0.0.


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
