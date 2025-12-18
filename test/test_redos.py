import logging
import subprocess
import sys
import time
from pathlib import Path

log = logging.getLogger("test")
LIB_DIR = Path(__file__).parent.parent / "lib"


def pull_387_example_1():
    # https://github.com/trentm/python-markdown2/pull/387
    return "[#a" + " " * 3456


def pull_387_example_2():
    # https://github.com/trentm/python-markdown2/pull/387
    return "```" + "\n" * 3456


def pull_387_example_3():
    # https://github.com/trentm/python-markdown2/pull/387
    return "-*-" + " " * 3456


def pull_402():
    # https://github.com/trentm/python-markdown2/pull/402
    return " " * 100_000 + "$"


def issue493():
    # https://github.com/trentm/python-markdown2/issues/493
    return "**_" + "*_" * 38730 * 10 + "\x00"


def issue_633():
    # https://github.com/trentm/python-markdown2/issues/633
    return '<p m="1"' * 2500 + " " * 5000 + "</div"

def issue_668():
    # https://github.com/trentm/python-markdown2/issues/668
    # not technically a redos, but still an error that caused a DOS
    return 'a_b **x***y* c_d'


# whack everything in a dict for easy lookup later on
CASES = {
    fn.__name__: (fn, extras)
    for fn, extras in [
        (pull_387_example_1, None),
        (pull_387_example_2, None),
        (pull_387_example_3, None),
        (pull_402, None),
        (issue493, None),
        (issue_633, None),
        (issue_668, ['code-friendly']),
    ]
}


if __name__ == "__main__":
    logging.basicConfig()

    if "--execute" in sys.argv:
        testcase = CASES[sys.argv[sys.argv.index("--execute") + 1]]
        sys.path.insert(0, str(LIB_DIR))
        from markdown2 import markdown

        markdown(testcase[0](), extras=testcase[1])
        sys.exit(0)

    print("-- ReDoS tests")

    fails = []
    start_time = time.time()
    for testcase in CASES:
        print(f"markdown2/redos/{testcase} ... ", end="")

        testcase_start_time = time.time()
        try:
            subprocess.run([sys.executable, __file__, "--execute", testcase], timeout=3)
        except subprocess.TimeoutExpired:
            fails.append(testcase)
            print(f"FAIL ({time.time() - testcase_start_time:.3f}s)")
        else:
            print(f"ok ({time.time() - testcase_start_time:.3f}s)")

    print("----------------------------------------------------------------------")
    print(f"Ran {len(CASES)} tests in {time.time() - start_time:.3f}s")

    if fails:
        print("FAIL:", fails)
    else:
        print("OK")

    sys.exit(len(fails))
