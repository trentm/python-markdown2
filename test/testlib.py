#!python
# Copyright (c) 2000-2008 ActiveState Software Inc.
# License: MIT License (http://www.opensource.org/licenses/mit-license.php)

"""
    test suite harness

    Usage:

        test --list [<tags>...]  # list available tests modules
        test [<tags>...]         # run test modules

    Options:
        -v, --verbose   more verbose output
        -q, --quiet     don't print anything except if a test fails
        -d, --debug     log debug information        
        -h, --help      print this text and exit
        -l, --list      Just list the available test modules. You can also
                        specify tags to play with module filtering.
        -n, --no-default-tags   Ignore default tags
        -L <directive>  Specify a logging level via
                            <logname>:<levelname>
                        For example:
                            codeintel.db:DEBUG
                        This option can be used multiple times.

    By default this will run all tests in all available "test_*" modules.
    Tags can be specified to control which tests are run. For example:
    
        test python         # run tests with the 'python' tag
        test python cpln    # run tests with both 'python' and 'cpln' tags
        test -- -python     # exclude tests with the 'python' tag
                            # (the '--' is necessary to end the option list)
    
    The full name and base name of a test module are implicit tags for that
    module, e.g. module "test_xdebug.py" has tags "test_xdebug" and "xdebug".
    A TestCase's class name (with and without "TestCase") is an implicit
    tag for an test_* methods. A "test_foo" method also has "test_foo"
    and "foo" implicit tags.

    Tags can be added explicitly added:
    - to modules via a __tags__ global list; and
    - to individual test_* methods via a "tags" attribute list (you can
      use the testlib.tag() decorator for this).
"""
#TODO:
# - Document how tests are found (note the special "test_cases()" and
#   "test_suite_class" hooks).
# - See the optparse "TODO" below.
# - Make the quiet option actually quiet.

__version_info__ = (0, 6, 6)
__version__ = '.'.join(map(str, __version_info__))


import os
from os.path import join, basename, dirname, abspath, splitext, \
                    isfile, isdir, normpath, exists
import sys
import getopt
import glob
import time
import types
import tempfile
import unittest
from pprint import pprint
import imp
import optparse
import logging
import textwrap
import traceback



#---- globals and exceptions

log = logging.getLogger("test")



#---- exports generally useful to test cases

class TestError(Exception):
    pass

class TestSkipped(Exception):
    """Raise this to indicate that a test is being skipped.

    ConsoleTestRunner knows to interpret these at NOT failures.
    """
    pass

class TestFailed(Exception):
    pass

def tag(*tags):
    """Decorator to add tags to test_* functions.
    
    Example:
        class MyTestCase(unittest.TestCase):
            @testlib.tag("knownfailure")
            def test_foo(self):
                #...
    """
    def decorate(f):
        if not hasattr(f, "tags"):
            f.tags = []
        f.tags += tags
        return f
    return decorate


#---- timedtest decorator
# Use this to assert that a test completes in a given amount of time.
# This is from http://www.artima.com/forums/flat.jsp?forum=122&thread=129497
# Including here, becase it might be useful.
# NOTE: Untested and I suspect some breakage.

TOLERANCE = 0.05

class DurationError(AssertionError): pass

def timedtest(max_time, tolerance=TOLERANCE):
    """ timedtest decorator
    decorates the test method with a timer
    when the time spent by the test exceeds
    max_time in seconds, an Assertion error is thrown.
    """
    def _timedtest(function):
        def wrapper(*args, **kw):
            start_time = time.time()
            try:
                function(*args, **kw)
            finally:
                total_time = time.time() - start_time
                if total_time > max_time + tolerance:
                    raise DurationError(('Test was too long (%.2f s)'
                                           % total_time))
        return wrapper

    return _timedtest



#---- module api

class Test(object):
    def __init__(self, ns, testmod, testcase, testfn_name,
                 testsuite_class=None):
        self.ns = ns
        self.testmod = testmod
        self.testcase = testcase
        self.testfn_name = testfn_name
        self.testsuite_class = testsuite_class
        # Give each testcase some extra testlib attributes for useful
        # introspection on TestCase instances later on.
        self.testcase._testlib_shortname_ = self.shortname()
        self.testcase._testlib_explicit_tags_ = self.explicit_tags()
        self.testcase._testlib_implicit_tags_ = self.implicit_tags()
    def __str__(self):
        return self.shortname()
    def __repr__(self):
        return "<Test %s>" % self.shortname()
    def shortname(self):
        bits = [self._normname(self.testmod.__name__),
                self._normname(self.testcase.__class__.__name__),
                self._normname(self.testfn_name)]
        if self.ns:
            bits.insert(0, self.ns)
        return '/'.join(bits)
    def _flatten_tags(self, tags):
        """Split tags with '/' in them into multiple tags.
        
        '/' is the reserved tag separator and allowing tags with
        embedded '/' results in one being unable to select those via
        filtering. As long as tag order is stable then presentation of
        these subsplit tags should be fine.
        """
        flattened = []
        for t in tags:
            flattened += t.split('/')
        return flattened
    def explicit_tags(self):
        tags = []
        if hasattr(self.testmod, "__tags__"):
            tags += self.testmod.__tags__
        if hasattr(self.testcase, "__tags__"):
            tags += self.testcase.__tags__
        testfn = getattr(self.testcase, self.testfn_name)
        if hasattr(testfn, "tags"):
            tags += testfn.tags
        return self._flatten_tags(tags)
    def implicit_tags(self):
        tags = [
            self.testmod.__name__.lower(),
            self._normname(self.testmod.__name__),
            self.testcase.__class__.__name__.lower(),
            self._normname(self.testcase.__class__.__name__),
            self.testfn_name,
            self._normname(self.testfn_name),
        ]
        if self.ns:
            tags.insert(0, self.ns)
        return self._flatten_tags(tags)
    def tags(self):
        return self.explicit_tags() + self.implicit_tags()
    def doc(self):
        testfn = getattr(self.testcase, self.testfn_name)
        return testfn.__doc__ or ""
    def _normname(self, name):
        if name.startswith("test_"):
            return name[5:].lower()
        elif name.startswith("test"):
            return name[4:].lower()
        elif name.endswith("TestCase"):
            return name[:-8].lower()
        else:
            return name


def testmod_paths_from_testdir(testdir):
    """Generate test module paths in the given dir."""
    for path in glob.glob(join(testdir, "test_*.py")):
        yield path

    for path in glob.glob(join(testdir, "test_*")):
        if not isdir(path): continue
        if not isfile(join(path, "__init__.py")): continue
        yield path

def testmods_from_testdir(testdir):
    """Generate test modules in the given test dir.
    
    Modules are imported with 'testdir' first on sys.path.
    """
    testdir = normpath(testdir)
    for testmod_path in testmod_paths_from_testdir(testdir):
        testmod_name = splitext(basename(testmod_path))[0]
        log.debug("import test module '%s'", testmod_path)
        try:
            iinfo = imp.find_module(testmod_name, [dirname(testmod_path)])
            testabsdir = abspath(testdir)
            sys.path.insert(0, testabsdir)
            old_dir = os.getcwd()
            os.chdir(testdir)
            try:
                testmod = imp.load_module(testmod_name, *iinfo)
            finally:
                os.chdir(old_dir)
                sys.path.remove(testabsdir)
        except TestSkipped:
            _, ex, _ = sys.exc_info()
            log.warning("'%s' module skipped: %s", testmod_name, ex)
        except Exception:
            _, ex, _ = sys.exc_info()
            log.warning("could not import test module '%s': %s (skipping, "
                        "run with '-d' for full traceback)",
                        testmod_path, ex)
            if log.isEnabledFor(logging.DEBUG):
                traceback.print_exc()
        else:
            yield testmod

def testcases_from_testmod(testmod):
    """Gather tests from a 'test_*' module.
    
    Returns a list of TestCase-subclass instances. One instance for each
    found test function.
    
    In general the normal unittest TestLoader.loadTests*() semantics are
    used for loading tests with some differences:
    - TestCase subclasses beginning with '_' are skipped (presumed to be
      internal).
    - If the module has a top-level "test_cases", it is called for a list of
      TestCase subclasses from which to load tests (can be a generator). This
      allows for run-time setup of test cases.
    - If the module has a top-level "test_suite_class", it is used to group
      all test cases from that module into an instance of that TestSuite
      subclass. This allows for overriding of test running behaviour.
    """
    class TestListLoader(unittest.TestLoader):
        suiteClass = list

    loader = TestListLoader()
    if hasattr(testmod, "test_cases"):
        try:
            for testcase_class in testmod.test_cases():
                if testcase_class.__name__.startswith("_"):
                    log.debug("skip private TestCase class '%s'",
                              testcase_class.__name__)
                    continue
                for testcase in loader.loadTestsFromTestCase(testcase_class):
                    yield testcase
        except Exception:
            _, ex, _ = sys.exc_info()
            testmod_path = testmod.__file__
            if testmod_path.endswith(".pyc"):
                testmod_path = testmod_path[:-1]
            log.warning("error running test_cases() in '%s': %s (skipping, "
                        "run with '-d' for full traceback)",
                        testmod_path, ex)
            if log.isEnabledFor(logging.DEBUG):
                traceback.print_exc()
    else:
        class_names_skipped = []
        for testcases in loader.loadTestsFromModule(testmod):
            for testcase in testcases:
                class_name = testcase.__class__.__name__
                if class_name in class_names_skipped:
                    pass
                elif class_name.startswith("_"):
                    log.debug("skip private TestCase class '%s'", class_name)
                    class_names_skipped.append(class_name)
                else:
                    yield testcase


def tests_from_manifest(testdir_from_ns):
    """Return a list of `testlib.Test` instances for each test found in
    the manifest.
    
    There will be a test for
    (a) each "test*" function of
    (b) each TestCase-subclass in
    (c) each "test_*" Python module in
    (d) each test dir in the manifest.
    
    If a "test_*" module has a top-level "test_suite_class", it will later
    be used to group all test cases from that module into an instance of that
    TestSuite subclass. This allows for overriding of test running behaviour.
    """
    for ns, testdir in testdir_from_ns.items():
        for testmod in testmods_from_testdir(testdir):
            if hasattr(testmod, "test_suite_class"):
                testsuite_class = testmod.test_suite_class
                if not issubclass(testsuite_class, unittest.TestSuite):
                    testmod_path = testmod.__file__
                    if testmod_path.endswith(".pyc"):
                        testmod_path = testmod_path[:-1]
                    log.warning("'test_suite_class' of '%s' module is not a "
                                "subclass of 'unittest.TestSuite': ignoring",
                                testmod_path)
            else:
                testsuite_class = None
            for testcase in testcases_from_testmod(testmod):
                yield Test(ns, testmod, testcase,
                            testcase._testMethodName,
                            testsuite_class)

def tests_from_manifest_and_tags(testdir_from_ns, tags):
    include_tags = [tag.lower() for tag in tags if not tag.startswith('-')]
    exclude_tags = [tag[1:].lower() for tag in tags if tag.startswith('-')]

    for test in tests_from_manifest(testdir_from_ns):
        test_tags = [t.lower() for t in test.tags()]

        matching_exclude_tags = [t for t in exclude_tags if t in test_tags]
        if matching_exclude_tags:
            #log.debug("test '%s' matches exclude tag(s) '%s': skipping",
            #          test.shortname(), "', '".join(matching_exclude_tags))
            continue

        if not include_tags:
            yield test
        else:
            for tag in include_tags:
                if tag not in test_tags:
                    #log.debug("test '%s' does not match tag '%s': skipping",
                    #          test.shortname(), tag)
                    break
            else:
                #log.debug("test '%s' matches tags: %s", test.shortname(),
                #          ' '.join(tags))
                yield test
                
def test(testdir_from_ns, tags=[], setup_func=None):
    log.debug("test(testdir_from_ns=%r, tags=%r, ...)",
              testdir_from_ns, tags)
    if setup_func is not None:
        setup_func()
    tests = list(tests_from_manifest_and_tags(testdir_from_ns, tags))
    if not tests:
        return None
    
    # Groups test cases into a test suite class given by their test module's
    # "test_suite_class" hook, if any.
    suite = unittest.TestSuite()
    suite_for_testmod = None
    testmod = None
    for test in tests:
        if test.testmod != testmod:
            if suite_for_testmod is not None:
                suite.addTest(suite_for_testmod)
            suite_for_testmod = (test.testsuite_class or unittest.TestSuite)()
            testmod = test.testmod
        suite_for_testmod.addTest(test.testcase)
    if suite_for_testmod is not None:
        suite.addTest(suite_for_testmod)
    
    runner = ConsoleTestRunner(sys.stdout)
    result = runner.run(suite)
    return result

def list_tests(testdir_from_ns, tags):
    # Say I have two test_* modules:
    #   test_python.py:
    #       __tags__ = ["guido"]
    #       class BasicTestCase(unittest.TestCase):
    #           def test_def(self):
    #           def test_class(self):
    #       class ComplexTestCase(unittest.TestCase):
    #           def test_foo(self):
    #           def test_bar(self):
    #   test_perl/__init__.py:
    #       __tags__ = ["larry", "wall"]
    #       class BasicTestCase(unittest.TestCase):
    #           def test_sub(self):
    #           def test_package(self):
    #       class EclecticTestCase(unittest.TestCase):
    #           def test_foo(self):
    #           def test_bar(self):
    # The short-form list output for this should look like:
    #   python/basic/def [guido]
    #   python/basic/class [guido]
    #   python/complex/foo [guido]
    #   python/complex/bar [guido]
    #   perl/basic/sub [larry, wall]
    #   perl/basic/package [larry, wall]
    #   perl/eclectic/foo [larry, wall]
    #   perl/eclectic/bar [larry, wall]
    log.debug("list_tests(testdir_from_ns=%r, tags=%r)",
              testdir_from_ns, tags)

    tests = list(tests_from_manifest_and_tags(testdir_from_ns, tags))
    if not tests:
        return

    WIDTH = 78
    if log.isEnabledFor(logging.INFO): # long-form
        for i, t in enumerate(tests):
            if i:
                print()
            testfile = t.testmod.__file__
            if testfile.endswith(".pyc"):
                testfile = testfile[:-1]
            print("%s:" % t.shortname())
            print("  from: %s#%s.%s" % (testfile,
                t.testcase.__class__.__name__, t.testfn_name))
            wrapped = textwrap.fill(' '.join(t.tags()), WIDTH-10)
            print("  tags: %s" % _indent(wrapped, 8, True))
            if t.doc():
                print(_indent(t.doc(), width=2))
    else:
        for t in tests:
            line = t.shortname() + ' '
            if t.explicit_tags():
                line += '[%s]' % ' '.join(t.explicit_tags())
            print(line)


#---- text test runner that can handle TestSkipped reasonably

class ConsoleTestResult(unittest.TestResult):
    """A test result class that can print formatted text results to a stream.

    Used by ConsoleTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream):
        unittest.TestResult.__init__(self)
        self.skips = []
        self.stream = stream

    def getDescription(self, test):
        if test._testlib_explicit_tags_:
            return "%s [%s]" % (test._testlib_shortname_,
                                ', '.join(test._testlib_explicit_tags_))
        else:
            return test._testlib_shortname_

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.stream.write("ok\n")

    def addSkip(self, test, err):
        why = str(err[1])
        self.skips.append((test, why))
        self.stream.write("skipped (%s)\n" % why)

    def addError(self, test, err):
        if isinstance(err[1], TestSkipped):
            self.addSkip(test, err)
        else:
            unittest.TestResult.addError(self, test, err)
            self.stream.write("ERROR\n")

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.stream.write("FAIL\n")

    def printSummary(self):
        self.stream.write('\n')
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.write(self.separator1 + '\n')
            self.stream.write("%s: %s\n"
                              % (flavour, self.getDescription(test)))
            self.stream.write(self.separator2 + '\n')
            self.stream.write("%s\n" % err)


class ConsoleTestRunner(object):
    """A test runner class that displays results on the console.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    
    Differences with unittest.TextTestRunner:
    - adds support for *skipped* tests (those that raise TestSkipped)
    - no verbosity option (only have equiv of verbosity=2)
    - test "short desc" is it 3-level tag name (e.g. 'foo/bar/baz' where
      that identifies: 'test_foo.py::BarTestCase.test_baz'.
    """
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def run(self, test_or_suite, test_result_class=ConsoleTestResult):
        """Run the given test case or test suite."""
        result = test_result_class(self.stream)
        start_time = time.time()
        test_or_suite.run(result)
        time_taken = time.time() - start_time

        result.printSummary()
        self.stream.write(result.separator2 + '\n')
        self.stream.write("Ran %d test%s in %.3fs\n\n"
            % (result.testsRun, result.testsRun != 1 and "s" or "",
               time_taken))
        details = []
        num_skips = len(result.skips)
        if num_skips:
            details.append("%d skip%s"
                % (num_skips, (num_skips != 1 and "s" or "")))
        if not result.wasSuccessful():
            num_failures = len(result.failures)
            if num_failures:
                details.append("%d failure%s"
                    % (num_failures, (num_failures != 1 and "s" or "")))
            num_errors = len(result.errors)
            if num_errors:
                details.append("%d error%s"
                    % (num_errors, (num_errors != 1 and "s" or "")))
            self.stream.write("FAILED (%s)\n" % ', '.join(details))
        elif details:
            self.stream.write("OK (%s)\n" % ', '.join(details))
        else:
            self.stream.write("OK\n")
        return result



#---- internal support stuff

# Recipe: indent (0.2.1)
def _indent(s, width=4, skip_first_line=False):
    """_indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)





#---- mainline

#TODO: pass in add_help_option=False and add it ourself here.
## Optparse's handling of the doc passed in for -h|--help handling is
## abysmal. Hence we'll stick with getopt.
#def _parse_opts(args):
#    """_parse_opts(args) -> (options, tags)"""
#    usage = "usage: %prog [OPTIONS...] [TAGS...]"
#    parser = optparse.OptionParser(prog="test", usage=usage,
#                                   description=__doc__)
#    parser.add_option("-v", "--verbose", dest="log_level",
#                      action="store_const", const=logging.DEBUG,
#                      help="more verbose output")
#    parser.add_option("-q", "--quiet", dest="log_level",
#                      action="store_const", const=logging.WARNING,
#                      help="quieter output")
#    parser.add_option("-l", "--list", dest="action",
#                      action="store_const", const="list",
#                      help="list available tests")
#    parser.set_defaults(log_level=logging.INFO, action="test")
#    opts, raw_tags = parser.parse_args()
#
#    # Trim '.py' from user-supplied tags. They might have gotten there
#    # via shell expansion.
#    ...
#
#    return opts, raw_tags

def _parse_opts(args, default_tags):
    """_parse_opts(args) -> (log_level, action, tags)"""
    opts, raw_tags = getopt.getopt(args, "hvqdlL:n",
        ["help", "verbose", "quiet", "debug", "list", "no-default-tags"])
    log_level = logging.WARN
    action = "test"
    no_default_tags = False
    for opt, optarg in opts:
        if opt in ("-h", "--help"):
            action = "help"
        elif opt in ("-v", "--verbose"):
            log_level = logging.INFO
        elif opt in ("-q", "--quiet"):
            log_level = logging.ERROR
        elif opt in ("-d", "--debug"):
            log_level = logging.DEBUG
        elif opt in ("-l", "--list"):
            action = "list"
        elif opt in ("-n", "--no-default-tags"):
            no_default_tags = True
        elif opt == "-L":
            # Optarg is of the form '<logname>:<levelname>', e.g.
            # "codeintel:DEBUG", "codeintel.db:INFO".
            lname, llevelname = optarg.split(':', 1)
            llevel = getattr(logging, llevelname)
            logging.getLogger(lname).setLevel(llevel)

    # Clean up the given tags.
    if no_default_tags:
        tags = []
    else:
        tags = default_tags
    for raw_tag in raw_tags:
        if splitext(raw_tag)[1] in (".py", ".pyc", ".pyo", ".pyw") \
           and exists(raw_tag):
            # Trim '.py' from user-supplied tags if it looks to be from
            # shell expansion.
            tags.append(splitext(raw_tag)[0])
        elif '/' in raw_tag:
            # Split one '/' to allow the shortname from the test listing
            # to be used as a filter.
            tags += raw_tag.split('/')
        else:
            tags.append(raw_tag)

    return log_level, action, tags


def harness(testdir_from_ns={None: os.curdir}, argv=sys.argv,
            setup_func=None, default_tags=None):
    """Convenience mainline for a test harness "test.py" script.

        "testdir_from_ns" (optional) is basically a set of directories in
            which to look for test cases. It is a dict with:
                <namespace>: <testdir>
            where <namespace> is a (short) string that becomes part of the
            included test names and an implicit tag for filtering those
            tests. By default the current dir is use with an empty namespace:
                {None: os.curdir}
        "setup_func" (optional) is a callable that will be called once
            before any tests are run to prepare for the test suite. It
            is not called if no tests will be run.
        "default_tags" (optional)
    
    Typically, if you have a number of test_*.py modules you can create
    a test harness, "test.py", for them that looks like this:

        #!/usr/bin/env python
        if __name__ == "__main__":
            retval = testlib.harness()
            sys.exit(retval)
    """
    if not logging.root.handlers:
        logging.basicConfig()
    try:
        log_level, action, tags = _parse_opts(argv[1:], default_tags or [])
    except getopt.error:
        _, ex, _ = sys.exc_info()
        log.error(str(ex) + " (did you need a '--' before a '-TAG' argument?)")
        return 1
    log.setLevel(log_level)

    if action == "help":
        print(__doc__)
        return 0
    if action == "list":
        return list_tests(testdir_from_ns, tags)
    elif action == "test":
        result = test(testdir_from_ns, tags, setup_func=setup_func)
        if result is None:
            return None
        return len(result.errors) + len(result.failures)
    else:
        raise TestError("unexpected action/mode: '%s'" % action)


