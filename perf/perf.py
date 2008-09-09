#!/usr/bin/env python

"""Run some performance numbers.  <cases-dir> is a directory with a
number of "*.text" files to process.

Example:
    python gen_perf_cases.py    # generate a couple cases dirs
    python perf.py tmp-test-cases
"""

import os
import sys
import timeit
import time
from os.path import *
from glob import glob
import optparse

from util import hotshotit


clock = sys.platform == "win32" and time.clock or time.time


@hotshotit
def hotshot_markdown_py(cases_dir, repeat):
    time_markdown_py(cases_dir, repeat)

def time_markdown_py(cases_dir, repeat):
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
def hotshot_markdown2_py(cases_dir, repeat):
    time_markdown2_py(cases_dir, repeat)

def time_markdown2_py(cases_dir, repeat):
    sys.path.insert(0, "../lib")
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

def time_markdown_pl(cases_dir, repeat):
    times = []
    for i in range(repeat):
        start = clock()
        os.system('perl time_markdown_pl.pl "%s"' % cases_dir)
        end = clock()
        times.append(end - start)
    print "  Markdown.pl: best of %d: %.3fs" % (repeat, min(times))

def time_all(cases_dir, repeat):
    time_markdown_pl(cases_dir, repeat=repeat)
    time_markdown_py(cases_dir, repeat=repeat)
    time_markdown2_py(cases_dir, repeat=repeat)

def time_not_markdown_py(cases_dir, repeat):
    time_markdown_pl(cases_dir, repeat=repeat)
    time_markdown2_py(cases_dir, repeat=repeat)


#---- mainline

class _NoReflowFormatter(optparse.IndentedHelpFormatter):
    """An optparse formatter that does NOT reflow the description."""
    def format_description(self, description):
        return description or ""

def main(args=sys.argv):
    usage = "python perf.py [-i all|markdown.py|markdown2.py|Markdown.pl] [cases-dir]"
    parser = optparse.OptionParser(prog="perf", usage=usage,
        description=__doc__, formatter=_NoReflowFormatter())
    parser.add_option("-r", "--repeat", type="int",
        help="number of times to repeat timing cycle (default 3 if timing, "
             "1 if profiling)")
    parser.add_option("-i", "--implementation",
        help="Markdown implementation(s) to run: all (default), "
             "markdown.py, markdown2.py, Markdown.pl, not-markdown.py")
    parser.add_option("--hotshot", "--profile", dest="hotshot",
        action="store_true",
        help="profile and dump stats about a single run (not supported "
             "for Markdown.pl)")
    parser.set_defaults(implementation="all", hotshot=False, repeat=None)
    opts, args = parser.parse_args()
 
    if len(args) != 1:
        sys.stderr.write("error: incorrect number of args\n")
        sys.stderr.write(__doc__)
        return 1
    cases_dir = args[0]
    if not exists(cases_dir):
        raise OSError("cases dir `%s' does not exist: use "
                      "gen_perf_cases.py to generate some cases dirs" 
                      % cases_dir)
    if opts.repeat is None:
        opts.repeat = opts.hotshot and 1 or 3

    if opts.hotshot:
        assert opts.implementation in ("markdown.py", "markdown2.py")
        timer_name = "hotshot_%s" \
            % opts.implementation.lower().replace('.', '_').replace('-', '_')
        d = sys.modules[__name__].__dict__
        if timer_name not in d:
            raise ValueError("no '%s' timer function" % timer_name)
        timer = d[timer_name]
        print "Profile conversion of %s (plat=%s):" \
              % (os.path.join(cases_dir, "*.text"), sys.platform)
        timer(cases_dir, repeat=opts.repeat)
        print
        os.system("python show_stats.py %s.prof" % timer_name)

    else:
        timer_name = "time_%s" \
            % opts.implementation.lower().replace('.', '_').replace('-', '_')

        d = sys.modules[__name__].__dict__
        if timer_name not in d:
            raise ValueError("no '%s' timer function" % timer_name)
        timer = d[timer_name]
        print "Time conversion of %s (plat=%s):" \
              % (os.path.join(cases_dir, "*.text"), sys.platform)
        timer(cases_dir, repeat=opts.repeat)
    
if __name__ == "__main__":
    sys.exit( main(sys.argv) )


