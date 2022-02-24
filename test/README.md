## Introduction

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

To run all the tests:

    pytest -vss test
    (or within the test dir)
    pytest -vss .

The test driver used (pytest) allows one to filter the tests run via short
strings that identify specific or groups of tests. Run `pytest test --list` to
list all available tests and their names/tags. I use the "knownfailure" tag to
mark those tests that I know fail (e.g. the `php-markdown-extra-cases` all fail
because markdown2.py doesn't implement those additions to the Markdown syntax).
To run the test suite **without** the known failures:

    $ pytest test_rendering.py -m "not knownfailure
    test/test_rendering.py::test_render[tm-cases-CVE-2018-5773.text] PASSED
    test/test_rendering.py::test_render[tm-cases-ampersands.text] PASSED
    test/test_rendering.py::test_render[tm-cases-auto_link.text] FAILED
    test/test_rendering.py::test_render[tm-cases-auto_link_email_with_underscore.text] FAILED
    ....
    ....
    5 failed, 146 passed, 15 deselected in 0.33s


## Examples

List all tests (and tags):

    pytest test --list

Run all tests:

    pytest -vss test

Run one single (named test):

    pytest -s test/test_rendering.py::test_render[tm-cases-codespans.text]

Run all tests with a particular flag:

    pytest -vvs  test -m pygments

RUn all test with flags matching an expression:

    pytest -vvs  test -m "pygments and not fenced_code_blocks"


**NOTE**: All the commands are executed from the top most check out directory, PYTHONPATH is set to lib.

**NOTE**: pass the -vv flag to display verbose logging and -s flag to prevent pytest to capture the stdout/stderr (for debug)


**TODO**: Add details about which tests in the various test sets that markdown2.py
fails... and why I'm not concerned about them. 
 
