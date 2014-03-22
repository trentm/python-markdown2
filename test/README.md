This directory holds test suite. There are a number of test sets, each in its own directory:

- **tm-cases**: Cases I wrote while writing markdown2.py. Many of these are
  very small bits of text testing a specific part of the Markdown syntax.
- **markdowntest-cases**: The test cases from the
  [MarkdownTest_1.0.zip package announce on the markdown-discuss list](http://six.pairlist.net/pipermail/markdown-discuss/2004-December/000909.html).
- **php-markdown-cases**: Test cases included in the MDTest package
  [announce on markdow-discuss in July 2007](http://six.pairlist.net/pipermail/markdown-discuss/2007-July/000674.html).
- **php-markdown-extra-cases**: Test cases included in the MDTest package
  (same as above) testing extra Markdown syntax that only PHP Markdown implements.


# markdown2.py test results

To run the test suite:

    python test.py [TAGS...]

The test driver used (testlib.py) allows one to filter the tests run via short
strings that identify specific or groups of tests. Run `python test.py -l` to
list all available tests and their names/tags. I use the "knownfailure" tag to
mark those tests that I know fail (e.g. the `php-markdown-extra-cases` all fail
because markdown2.py doesn't implement those additions to the Markdown syntax).
To run the test suite **without** the known failures:

    $ python test.py -- -knownfailure
    markdown2/tm/auto_link ... ok
    markdown2/tm/blockquote ... ok
    markdown2/tm/blockquote_with_pre ... ok
    markdown2/tm/code_block_with_tabs [fromphpmarkdown] ... ok
    markdown2/tm/code_safe_emphasis [code_safe] ... ok
    markdown2/tm/codeblock ... ok
    markdown2/tm/codespans ... ok
    markdown2/tm/emphasis ... ok
    markdown2/tm/escapes ... ok
    markdown2/tm/header ... ok
    markdown2/tm/hr ... ok
    markdown2/tm/inline_links ... ok
    markdown2/tm/lists ... ok
    markdown2/tm/nested_list ... ok
    markdown2/tm/parens_in_url_4 [fromphpmarkdown] ... ok
    markdown2/tm/raw_html ... ok
    markdown2/tm/ref_links ... ok
    markdown2/tm/safe_mode ... ok
    markdown2/tm/sublist-para [questionable] ... ok
    markdown2/tm/tricky_anchors ... ok
    markdown2/tm/underline_in_autolink ... ok
    markdown2/markdowntest/amps_and_angle_encoding ... ok
    markdown2/markdowntest/auto_links ... ok
    markdown2/markdowntest/backslash_escapes ... ok
    markdown2/markdowntest/blockquotes_with_code_blocks ... ok
    markdown2/markdowntest/hard-wrapped_paragraphs_with_list-like_lines ... ok
    markdown2/markdowntest/horizontal_rules ... ok
    markdown2/markdowntest/inline_html_simple ... ok
    markdown2/markdowntest/inline_html_comments ... ok
    markdown2/markdowntest/links_inline_style ... ok
    markdown2/markdowntest/links_reference_style ... ok
    markdown2/markdowntest/literal_quotes_in_titles ... ok
    markdown2/markdowntest/markdown_documentation_basics ... ok
    markdown2/markdowntest/markdown_documentation_syntax ... ok
    markdown2/markdowntest/nested_blockquotes ... ok
    markdown2/markdowntest/ordered_and_unordered_lists ... ok
    markdown2/markdowntest/strong_and_em_together ... ok
    markdown2/markdowntest/tabs ... ok
    markdown2/phpmarkdown/backslash_escapes ... ok
    markdown2/phpmarkdown/code_spans ... ok
    markdown2/phpmarkdown/email_auto_links ... ok
    markdown2/phpmarkdown/headers ... ok
    markdown2/phpmarkdown/images_untitled ... ok
    markdown2/phpmarkdown/inline_html_comments ... ok
    markdown2/phpmarkdown/ins_&_del ... ok
    markdown2/phpmarkdown/links_inline_style ... ok
    markdown2/phpmarkdown/md5_hashes ... ok
    markdown2/phpmarkdown/php-specific_bugs ... ok
    markdown2/phpmarkdown/tight_blocks ... ok
    markdown2/direct/code_in_strong [code, strong] ... ok
    markdown2/direct/pre ... ok
    markdown2/direct/starter_pre [pre, recipes] ... ok
    
    ----------------------------------------------------------------------
    Ran 52 tests in 0.799s
    
    OK


TODO: Add details about which tests in the various test sets that markdown2.py
fails... and why I'm not concerned about them. 
 
