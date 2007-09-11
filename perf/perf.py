#!/usr/bin/env python

"""
Run some performance numbers.

Usage: 
    python perf.py [all|markdown.py|markdown2.py|Markdown.pl] [cases-dir]

where <cases-dir> is a directory with a number of "*.text" files to process.

Example:
    python gen_perf_cases.py    # generate a couple cases dirs
    python perf.py all tmp-test-cases
"""

import os
import sys
import timeit
import time
from os.path import *
from glob import glob

from util import hotshotit


DEFAULT_REPEAT = 1

clock = sys.platform == "win32" and time.clock or time.time


def time_markdown_py(cases_dir, repeat=DEFAULT_REPEAT):
    sys.path.insert(0, join("..", "test"))
    import markdown
    del sys.path[0]
    markdowner = markdown.Markdown()
    times = []
    for i in range(repeat):
        start = clock()
        for path in glob(join(cases_dir, "*.text")):
            f = open(path, 'r')
            content = f.read()
            f.close()
            try:
                markdowner.convert(content)
                markdowner.reset()
            except UnicodeError:
                pass
        end = clock()
        times.append(end - start)
    print "  markdown.py: best of %d: %.3fs" % (repeat, min(times))

@hotshotit
def time_markdown2_py(cases_dir, repeat=DEFAULT_REPEAT):
    sys.path.insert(0, "..")
    import markdown2
    del sys.path[0]
    markdowner = markdown2.Markdown()
    times = []
    for i in range(repeat):
        start = clock()
        for path in glob(join(cases_dir, "*.text")):
            f = open(path, 'r')
            content = f.read()
            f.close()
            markdowner.convert(content)
        end = clock()
        times.append(end - start)
    print "  markdown2.py: best of %d: %.3fs" % (repeat, min(times))

def time_markdown_pl(cases_dir, repeat=DEFAULT_REPEAT):
    times = []
    for i in range(repeat):
        start = clock()
        os.system('perl time_markdown_pl.pl "%s"' % cases_dir)
        end = clock()
        times.append(end - start)
    print "  Markdown.pl: best of %d: %.3fs" % (repeat, min(times))

def time_all(cases_dir, repeat=DEFAULT_REPEAT):
    time_markdown_pl(cases_dir, repeat=repeat)
    time_markdown_py(cases_dir, repeat=repeat)
    time_markdown2_py(cases_dir, repeat=repeat)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("error: incorrect number of args\n")
        sys.stderr.write(__doc__)
        sys.exit(1)

    script, selector, cases_dir = sys.argv
    timer_name = "time_%s" % selector.lower().replace('.', '_')
    d = sys.modules[__name__].__dict__
    if timer_name not in d:
        raise ValueError("no '%s' timer function" % timer_name)
    timer = d[timer_name]
    if not exists(cases_dir):
        raise OSError("cases dir `%s' does not exist: use "
                      "gen_perf_cases.py to generate some cases dirs" 
                      % cases_dir)
    print "Time conversion of %s%s*.text:" % (cases_dir, os.path.sep)
    timer(cases_dir)

