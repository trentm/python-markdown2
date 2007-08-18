"""
show_stats.py

Display results from profiling with hotshot.

Usage:
In module M.py, replace a call to function f with this code:

    import hotshot
    profiler = hotshot.Profile("%s.prof" % (__file__))
    profiler.runcall(f, *args)

and run from the command-line as
% python .../whatever.py args

To get the results, run this file:

% python .../show_stats.py .../whatever.py.prof
"""

import sys

import hotshot, hotshot.stats
stats = hotshot.stats.load(sys.argv[1])
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)
