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

Note that in the source repository there are a few files (for the test suite
and performance metrics) that are under different licenses. None of these
files are included in the source packages. These exceptions are as follows:

- perf/recipes.pprint: Python License

  This file includes a number of real-world examples of Markdown from the
  ActiveState Python Cookbook, used for doing some performance testing of
  markdown2.py

- test/php-markdown-cases/* & test/php-markdown-extra-cases/*

  These are copies of the MarkdownTest-1.0 and MDTest packages announced on
  the markdown-discuss list.

- test/markdown.py: GPL 2 or BSD

  A copy (currently old) of Python-Markdown -- the other Python Markdown
  implementation.

- test/markdown.php: BSD-style

  This is PHP Markdown (http://michelf.com/projects/php-markdown/).

- test/Markdown.pl: BSD-style

  A copy of Perl Markdown (http://daringfireball.net/projects/markdown/).

