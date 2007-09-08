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

if __name__ == "__main__":
    retval = testlib.harness(testdir_from_ns=testdir_from_ns)
    sys.exit(retval)

