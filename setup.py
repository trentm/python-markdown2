#!/usr/bin/env python

import os
import sys

from setuptools import setup

_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "lib"))
try:
    import markdown2
finally:
    del sys.path[0]

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Operating System :: OS Independent
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Documentation
Topic :: Text Processing :: Filters
Topic :: Text Processing :: Markup :: HTML
"""

extras_require = {
    "code_syntax_highlighting": ["pygments>=2.7.3"],
    "wavedrom": ["wavedrom"],
    "latex": ['latex2mathml; python_version>="3.8.1"'],
}
# nested listcomp to combine all optional extras into convenient "all" option
extras_require["all"] = [i for v in tuple(extras_require.values()) for i in v]

setup(
    name="markdown2",
    version=markdown2.__version__,
    maintainer="Trent Mick",
    maintainer_email="trentm@gmail.com",
    author="Trent Mick",
    author_email="trentm@gmail.com",
    url="https://github.com/trentm/python-markdown2",
    license="MIT",
    platforms=["any"],
    py_modules=["markdown2"],
    package_dir={"": "lib"},
    entry_points={
        "console_scripts": [
            "markdown2 = markdown2:main"
        ]
    },
    description="A fast and complete Python implementation of Markdown",
    python_requires=">=3.9, <4",
    extras_require=extras_require,
    classifiers=classifiers.strip().split("\n"),
    long_description="""markdown2: A fast and complete Python implementation of Markdown.

Markdown is a text-to-HTML filter; it translates an easy-to-read /
easy-to-write structured text format into HTML.  Markdown's text
format is most similar to that of plain text email, and supports
features such as headers, *emphasis*, code blocks, blockquotes, and
links.  -- http://daringfireball.net/projects/markdown/

This is a fast and complete Python implementation of the Markdown
spec. See http://github.com/trentm/python-markdown2 for more info.
""",
)
