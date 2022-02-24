import os
import re
import warnings
from pathlib import Path

import pytest

ALL_SUBDIRS = []


def _gather_md_tests(srcdir):
    def sanitize(txt):
        return txt.replace(" ", "").replace("-", "_").replace(".", "_")

    class Item:
        def __init__(self, src):
            self.src = src
            self.expected = src.with_suffix(".html")
            assert self.expected.exists()

        @property
        def markers(self):
            src = self.src.with_suffix(".tags")
            if src.exists():
                return [ sanitize(m) for m in src.read_text().partition("#")[0].split()]

        @property
        def options(self):
            src = self.src.with_suffix(".opts")
            if not src.exists():
                return
            with warnings.catch_warnings():
                # files as link_patterns_double_hit.opts trigger "invalid escape sequence \s"
                warnings.simplefilter("ignore")
                return eval(src.read_text())

    items = {}
    for path in srcdir.glob("*.text"):
        name = f"{srcdir.name}-{path.name}" 
        assert name not in items
        items[name] = Item(path)
    return items


def parametrize(args, subdir):
    global ALL_SUBDIRS
    datadir = Path(os.getenv("DATADIR", Path(__file__).parent)).absolute()
    srcdir = datadir / subdir

    ALL_SUBDIRS.append(srcdir)
    items = _gather_md_tests(srcdir)

    # we build the parametrized
    def _fn(fn):
        parameters = []
        for name, item in sorted(items.items()):
            kwargs = {
                "id": name,
                "marks": [getattr(pytest.mark, m) for m in item.markers or []]
            }
            param = pytest.param(item.src, item.expected, item.options, **kwargs)  
            parameters.append(param)
        return pytest.mark.parametrize(args, parameters)(fn)
    return _fn


def pytest_addoption(parser):
    group = parser.getgroup("helloworld")
    group.addoption(
        "--list",
        action="store_true",
        dest="list-tests",
        help='list all tests',
    )


def pytest_collection_finish(session):
    if getattr(session.config.option, "list-tests"):
        for subdir in ALL_SUBDIRS:
            for name, item in sorted(_gather_md_tests(subdir).items()):
                print(f"{name} {item.markers}")
        pytest.exit('Done!')
