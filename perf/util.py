#!python
# Copyright (c) 2004-2006 ActiveState Software Inc.

"""Perf utility functions"""

import os
from os.path import basename
import sys
import md5
import re
import stat
import textwrap
import types
from pprint import pprint, pformat


# Global dict for holding specific hotshot profilers
hotshotProfilers = {}


# Decorators useful for timing and profiling specific functions.
#
# timeit usage:
#   Decorate the desired function and you'll get a print for how long
#   each call to the function took.
#
# hotspotit usage:
#   1. decorate the desired function
#   2. run your code
#   3. run:
#       python show_stats.py <funcname>.prof
#
def timeit(func):
    clock = (sys.platform == "win32" and time.clock or time.time)
    def wrapper(*args, **kw):
        start_time = clock()
        try:
            return func(*args, **kw)
        finally:
            total_time = clock() - start_time
            print "%s took %.3fs" % (func.func_name, total_time)
    return wrapper

def hotshotit(func):
    def wrapper(*args, **kw):
        import hotshot
        global hotshotProfilers
        prof_name = func.func_name+".prof"
        profiler = hotshotProfilers.get(prof_name)
        if profiler is None:
            profiler = hotshot.Profile(prof_name)
            hotshotProfilers[prof_name] = profiler
        return profiler.runcall(func, *args, **kw)
    return wrapper


