#!/usr/bin/env python
# Copyright (c) 2007-2008 ActiveState Software Inc.
# License: MIT (http://www.opensource.org/licenses/mit-license.php)

"""The markdown2 test suite entry point."""

import os
from os.path import exists, join, abspath, dirname, normpath
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
        import pygments
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
    try:
        import pygments
    except ImportError:
        log.warning("skipping pygments tests ('pygments' module not found)")
        default_tags.append("-pygments")

    retval = testlib.harness(testdir_from_ns=testdir_from_ns,
                             default_tags=default_tags)
    sys.exit(retval)
