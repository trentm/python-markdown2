#!/usr/bin/env python

import os
import sys
import timeit
import time
from os.path import *
from glob import glob

from util import hotshotit


DEFAULT_REPEAT = 3
DEFAULT_CASES_DIR = "test-cases"

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
    print "time_markdown_py: best of %d: %.3fs" % (repeat, min(times))

#@hotshotit
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
    print "time_markdown2_py: best of %d: %.3fs" % (repeat, min(times))

def time_markdown_pl(cases_dir, repeat=DEFAULT_REPEAT):
    times = []
    for i in range(repeat):
        start = clock()
        os.system('perl time_markdown_pl.pl "%s"' % cases_dir)
        end = clock()
        times.append(end - start)
    print "time_markdown_pl: best of %d: %.3fs" % (repeat, min(times))

def time_all(cases_dir, repeat=DEFAULT_REPEAT):
    time_markdown_pl(cases_dir, repeat=repeat)
    time_markdown_py(cases_dir, repeat=repeat)
    time_markdown2_py(cases_dir, repeat=repeat)

if __name__ == "__main__":
    # Usage: $0 [all|markdown.py|markdown2.py|Markdown.pl]
    selector = len(sys.argv) > 1 and sys.argv[1] or "all"
    timer_name = "time_%s" % selector.lower().replace('.', '_')
    d = sys.modules[__name__].__dict__
    if timer_name not in d:
        raise ValueError("no '%s' timer function" % timer_name)
    timer = d[timer_name]
    timer(DEFAULT_CASES_DIR)

