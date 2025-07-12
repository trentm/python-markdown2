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


# whack everything in a dict for easy lookup later on
CASES = {
    fn.__name__: fn
    for fn in [
        pull_387_example_1,
        pull_387_example_2,
        pull_387_example_3,
        pull_402,
        issue493,
        issue_633,
    ]
}


if __name__ == "__main__":
    logging.basicConfig()

    if "--execute" in sys.argv:
        testcase = CASES[sys.argv[sys.argv.index("--execute") + 1]]
        sys.path.insert(0, str(LIB_DIR))
        from markdown2 import markdown

        markdown(testcase())
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
