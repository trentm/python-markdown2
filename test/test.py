#!/usr/bin/env python
# Copyright (c) 2007 ActiveState Software Inc.

"""The markdown2 test suite entry point."""

import os
from os.path import exists, join, abspath, dirname, normpath
import sys
import logging

import testlib


testdir_from_ns = {
    None: os.curdir,
}

def setup():
    externals_dir = join(dirname(dirname(abspath(__file__))), "externals")
    pygments_dir = join(externals_dir, "pygments")
    if exists(pygments_dir):
        sys.path.insert(0, pygments_dir)

if __name__ == "__main__":
    retval = testlib.harness(testdir_from_ns=testdir_from_ns,
                             setup_func=setup)
    sys.exit(retval)

