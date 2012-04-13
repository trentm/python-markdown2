#!/usr/bin/env python
#
# Run the test suite against all the Python versions we can find.
#

import sys
import os
from os.path import dirname, abspath, join
import re


TOP = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(TOP, "tools"))
import which


def _python_ver_from_python(python):
    assert ' ' not in python
    o = os.popen('''%s -c "import sys; print(sys.version)"''' % python)
    ver_str = o.read().strip()
    ver_bits = re.split("\.|[^\d]", ver_str, 2)[:2]
    ver = tuple(map(int, ver_bits))
    return ver

def _gen_python_names():
    yield "python"
    for ver in [(2,4), (2,5), (2,6), (2,7), (3,0), (3,1), (3,2)]:
        yield "python%d.%d" % ver
        if sys.platform == "win32":
            yield "python%d%d" % ver

def _gen_pythons():
    python_from_ver = {}
    for name in _gen_python_names():
        for python in which.whichall(name):
            ver = _python_ver_from_python(python)
            if ver not in python_from_ver:
                python_from_ver[ver] = python
    for ver, python in sorted(python_from_ver.items()):
        yield ver, python

def testall():
    for ver, python in _gen_pythons():
        if ver < (2,3):
            # Don't support Python < 2.3.
            continue
        elif ver >= (3, 0):
            # Don't yet support Python 3.
            continue
        ver_str = "%s.%s" % ver
        print "-- test with Python %s (%s)" % (ver_str, python)
        assert ' ' not in python
        rv = os.system("%s test.py -- -knownfailure" % python)
        if rv:
            sys.exit(os.WEXITSTATUS(rv))

testall()
