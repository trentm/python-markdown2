#!/usr/bin/env python
# Copyright (c) 2007-2008 ActiveState Software Inc.
# License: MIT (http://www.opensource.org/licenses/mit-license.php)

"""The markdown2 test suite entry point."""

import importlib
import os
from os.path import join, abspath, dirname
import sys
import logging
import testlib

log = logging.getLogger("test")
testdir_from_ns = {
    None: os.curdir,
}

def setup():
    top_dir = dirname(dirname(abspath(__file__)))
    lib_dir = join(top_dir, "lib")
    sys.path.insert(0, lib_dir)

    # Attempt to get 'pygments' on the import path.
    try:
        # If already have it, use that one.
        import pygments  # noqa
    except ImportError:
        pygments_dir = join(top_dir, "deps", "pygments")
        if sys.version_info[0] <= 2:
            sys.path.insert(0, pygments_dir)
        else:
            sys.path.insert(0, pygments_dir + "3")

if __name__ == "__main__":
    logging.basicConfig()

    setup()
    default_tags = []
    warnings = []
    for extra_lib in ('pygments', 'wavedrom', 'latex2mathml'):
        try:
            mod = importlib.import_module(extra_lib)
        except ImportError:
            warnings.append("skipping %s tests ('%s' module not found)" % (extra_lib, extra_lib))
            default_tags.append("-%s" % extra_lib)
        else:
            if extra_lib == 'pygments':
                version = tuple(int(i) for i in mod.__version__.split('.')[:3])
                if version >= (2, 14, 0):
                    tag = "pygments<2.14"
                else:
                    tag = "pygments>=2.14"
                warnings.append("skipping %s tests (pygments %s found)" % (tag, mod.__version__))
                default_tags.append("-%s" % tag)

    retval = testlib.harness(testdir_from_ns=testdir_from_ns,
                             default_tags=default_tags)

    for warning in warnings:
        log.warning(warning)

    sys.exit(retval)
