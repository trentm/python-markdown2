markdown2 README
================

This is a fast and complete Python implementation of Markdown, a text-to-html
markup system as defined here:

    http://daringfireball.net/projects/markdown/syntax


Install
-------

To install it in your Python installation run:

    python setup.py install

However, everything you need to run this is in "lib/markdown2.py". If it is
easier for you, you can just copy that file to somewhere on your PythonPath
(to use as a module) or executable path (to use as a script).


Quick Usage
-----------

As a module:

    >>> import markdown2
    >>> markdown2.markdown("*boo!*")  # or use `html = markdown_path(PATH)`
    u'<p><em>boo!</em></p>\n'

    >>> markdowner = Markdown()
    >>> markdowner.convert("*boo!*")
    u'<p><em>boo!</em></p>\n'
    >>> markdowner.convert("**boom!**")
    u'<p><strong>boom!</strong></p>\n'

As a script:

    $ python markdown2.py foo.txt > foo.html

See the project pages, "lib/markdown2.py" docstrings and/or 
`python markdown2.py --help` for more details.


Project
-------

The python-markdown2 project lives here (subversion repo, issue tracker,
wiki):

    http://code.google.com/p/python-markdown2/

To checkout the full sources:

    svn checkout http://python-markdown2.googlecode.com/svn/trunk/ python-markdown2

To report a bug:

    http://code.google.com/p/python-markdown2/issues/list


License
-------

This project is licensed under the MIT License. 

Note that in the subversion repository there are a few files (for the test
suite and performance metrics) that are under different licenses. These files
are *not* included in source packages. See LICENSE.txt for details.


Test Suite
----------

This markdown implementation passes a fairly extensive test suite. To run it:

    cd test && python test.py

If you have the [mk](http://svn.openkomodo.com/openkomodo/browse/mk/trunk)
tool installed you can run the test suite with all available Python versions
by running:

    mk test

The crux of the test suite is a number of "cases" directories -- each with a
set of matching .text (input) and .html (expected output) files. These are:

    tm-cases/                   Tests authored for python-markdown2
    markdowntest-cases/         Tests from the 3rd-party MarkdownTest package
    php-markdown-cases/         Tests from the 3rd-party MDTest package
    php-markdown-extra-cases/   Tests also from MDTest package

See the wiki page for full details:
http://code.google.com/p/python-markdown2/wiki/TestingNotes

