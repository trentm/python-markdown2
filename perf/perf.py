#!/usr/bin/env python

"""Run some performance numbers.  <cases-dir> is a directory with a
number of "*.text" files to process.

Example:
    python gen_perf_cases.py    # generate a couple cases dirs
    python perf.py tmp-test-cases
"""

import os
import sys
import time
from os.path import *
from glob import glob
from StringIO import StringIO
import optparse

from util import hotshotit


clock = sys.platform == "win32" and time.clock or time.time


def init_markdown():
    sys.path.insert(0, join("..", "test"))
    import markdown
    del sys.path[0]
    return markdown.Markdown()

def init_markdown2():
    sys.path.insert(0, "../lib")
    import markdown2
    del sys.path[0]
    return markdown2.Markdown()

def run_py_markdown(mkd, markdowner, cases_dir):
    global show_progress
    for path in glob(join(cases_dir, "*.text")):
        f = open(path, 'r')
        content = f.read()
        f.close()
        try:
            # Mute markdowner
            sys.stdout = StringIO()
            markdowner.convert(content)
            if show_progress:
                sys.__stdout__.write('.')
        except Exception:
            # Don't print out traceback, this is profiling, not unit testing.
            sys.__stdout__.write('E')
        finally:
            # Release normally
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            if mkd == 'markdown.py':
                markdowner.reset()
        sys.stdout.flush()

def run_pl_markdown(mkd, markdowner, cases_dir):
    global show_progress
    cmd = 'perl time_markdown_pl.pl "%s"'
    if not show_progress:
        cmd += ' mute'
    os.system(cmd % cases_dir)


MKD = {
    'markdown.py': {
        'init': init_markdown,
        'run': run_py_markdown,
        },
    'markdown2.py': {
        'init': init_markdown2,
        'run': run_py_markdown,
        },
    'Markdown.pl': {
        'init': lambda: None,
        'run': run_pl_markdown,
        },
    }
MKDS = MKD.keys()


@hotshotit
def hotshot_py_markdown(mkd, cases_dir, repeat):
    time_markdown(mkd, cases_dir, repeat)

def time_markdown(mkd, cases_dir, repeat):
    markdowner = MKD[mkd]['init']()
    times = []
    for i in range(repeat):
        print '#%2d: ' % (i + 1),
        sys.stdout.flush()
        start = clock()
        MKD[mkd]['run'](mkd, markdowner, cases_dir)
        end = clock()
        print
        times.append(end - start)
    print "%s: best of %d: %.3fs" % (mkd, repeat, min(times))
    print

def time_all(cases_dir, repeat):
    for mkd in MKDS:
        time_markdown(mkd, cases_dir, repeat=repeat)


#---- mainline

class _NoReflowFormatter(optparse.IndentedHelpFormatter):
    """An optparse formatter that does NOT reflow the description."""
    def format_description(self, description):
        return description or ""

def main(args=sys.argv):
    global show_progress
    usage = "python perf.py [-i all|markdown.py|markdown2.py|Markdown.pl] [cases-dir]"
    parser = optparse.OptionParser(prog="perf", usage=usage,
        description=__doc__, formatter=_NoReflowFormatter())
    parser.add_option("-r", "--repeat", type="int",
        help="number of times to repeat timing cycle (default 3 if timing, "
             "1 if profiling)")
    parser.add_option("-i", "--implementation",
        help="Markdown implementation(s) to run: all (default), "
             "markdown.py, markdown2.py, Markdown.pl, not-markdown.py")
    parser.add_option("-H", "--hotshot", dest="hotshot",
        action="store_true",
        help="profile and dump stats about a single run (not supported "
             "for Markdown.pl)")
    parser.add_option("-p", "--progress", dest="progress",
        action="store_true", default=False,
        help="Show the progress")
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

    show_progress = opts.progress
    if opts.hotshot:
        assert opts.implementation in ("markdown.py", "markdown2.py")
        print "Profile conversion of %s (plat=%s):" \
              % (os.path.join(cases_dir, "*.text"), sys.platform)
        mkd = opts.implementation
        hotshot_py_markdown(mkd, cases_dir, repeat=opts.repeat)
        print
        os.system("python show_stats.py hotshot_%s.prof" % mkd)

    else:
        mkd = opts.implementation
        if mkd not in MKDS and mkd != 'all':
            raise ValueError("no such '%s' Markdown implementation" % mkd)
        print "Time conversion of %s (plat=%s):" \
              % (os.path.join(cases_dir, "*.text"), sys.platform)
        if mkd == 'all':
            time_all(cases_dir, repeat=opts.repeat)
        else:
            time_markdown(mkd, cases_dir, repeat=opts.repeat)
    
if __name__ == "__main__":
    sys.exit( main(sys.argv) )


