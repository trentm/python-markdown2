Markdown is a light text markup format and a processor to convert that to HTML.
The originator describes it as follows:

> Markdown is a text-to-HTML conversion tool for web writers.
> Markdown allows you to write using an easy-to-read, 
> easy-to-write plain text format, then convert it to 
> structurally valid XHTML (or HTML).
>
> -- <http://daringfireball.net/projects/markdown/>

This is a fast and complete Python implementation of Markdown. It was written to
closely match the behaviour of the original Perl-implemented Markdown.pl. There
is another [Python
markdown.py](http://www.freewisdom.org/projects/python-markdown/). However, at
least at the time this project was started, markdown2.py was faster (see the
[Performance
Notes](https://github.com/trentm/python-markdown2/wiki/Performance-Notes)) and,
to my knowledge, more correct (see [Testing
Notes](https://github.com/trentm/python-markdown2/wiki/Testing-Notes)).
That was a while ago though, so you should still consider Python-markdown for
your usage.


# Install

To install it in your Python installation run *one* of the following:

    pypm install markdown2      # if you use ActivePython (activestate.com/activepython)
    pip install markdown2
    python setup.py install

However, everything you need to run this is in "lib/markdown2.py". If it is
easier for you, you can just copy that file to somewhere on your PythonPath
(to use as a module) or executable path (to use as a script).


# Quick Usage

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

See the [project wiki](https://github.com/trentm/python-markdown2/wiki),
[lib/markdown2.py](https://github.com/trentm/python-markdown2/blob/master/lib/markdown2.py)
docstrings and/or `python markdown2.py --help` for more details.


# Project

The python-markdown2 project lives at <https://github.com/trentm/python-markdown2/>.
Note: On Mar 6, 2011 this project was moved from [Google Code](http://code.google.com/p/python-markdown2)
to here on Github.

The change log: <https://github.com/trentm/python-markdown2/blob/master/CHANGES.txt>

To report a bug: <https://github.com/trentm/python-markdown2/issues>


# Test Suite

This markdown implementation passes a fairly extensive test suite. To run it:

    cd test && python test.py

If you have the [mk](https://github.com/ActiveState/mk) tool installed you can
run the test suite with all available Python versions by running:

    mk test

The crux of the test suite is a number of "cases" directories -- each with a
set of matching .text (input) and .html (expected output) files. These are:

    tm-cases/                   Tests authored for python-markdown2 (tm=="Trent Mick")
    markdowntest-cases/         Tests from the 3rd-party MarkdownTest package
    php-markdown-cases/         Tests from the 3rd-party MDTest package
    php-markdown-extra-cases/   Tests also from MDTest package

See the [Testing Notes wiki
page](https://github.com/trentm/python-markdown2/wiki/Testing-Notes) for full
details.
