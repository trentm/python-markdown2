#!/usr/bin/env python
#
# Run the test suite against all the Python versions we can find.
#
import os
import re
import subprocess
import sys
from os.path import abspath, dirname, join

TOP = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(TOP, "tools"))
import which


def _python_ver_from_python(python):
    assert ' ' not in python
    o = os.popen('''%s -c "import sys; print(sys.version)"''' % python)
    ver_str = o.read().strip()
    ver_bits = re.split(r"\.|[^\d]", ver_str, 2)[:2]
    ver = tuple(map(int, ver_bits))
    return ver

def _gen_python_names():
    yield "python"
    if sys.platform == "win32":
        return

    # generate version numbers from python 3.8 to 3.20
    for ver in [(3, i) for i in range(8, 20)]:
        yield "python%d.%d" % ver
        if sys.platform == "win32":
            yield "python%d%d" % ver

def _gen_pythons():
    python_from_ver = {}
    for name in _gen_python_names():
        for python in which.whichall(name):
            if sys.platform == "win32" and re.search(r"\\WindowsApps\\[^\\]+$", python, flags=re.IGNORECASE):
                # skip Python stubs from the Windows Store.
                continue

            ver = _python_ver_from_python(python)
            if ver not in python_from_ver:
                python_from_ver[ver] = python
    for ver, python in sorted(python_from_ver.items()):
        yield ver, python

def testall():
    all_warnings = []
    for ver, python in _gen_pythons():
        if ver < (3, 8):
            # Don't support Python < 3.5
            continue
        ver_str = "%s.%s" % ver
        print("-- test with Python %s (%s)" % (ver_str, python))
        assert ' ' not in python

        env_args = 'MACOSX_DEPLOYMENT_TARGET= ' if sys.platform == 'darwin' else ''

        proc = subprocess.Popen(
            # pass "-u" option to force unbuffered output
            "%s%s -u test.py -- -knownfailure" % (env_args, python),
            shell=True, stderr=subprocess.PIPE
        )

        while proc.poll() is None:
            # capture and re-print stderr while process is running
            line = proc.stderr.readline().decode().strip()
            print(line, file=sys.stderr)
            if 'WARNING:' in line:
                # if stderr contains a warning, save this for later
                all_warnings.append((python, ver_str, line))

        if proc.returncode:
            sys.exit(proc.returncode)

    for python, ver_str, warning in all_warnings:
        # now re-print all warnings to make sure they are seen
        print('-- warning raised by Python %s (%s) -- %s' % (ver_str, python, warning))

testall()
