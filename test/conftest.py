import re  # pylint: disable=unused-import
import os
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
                marks = []
                with src.open() as fp:
                    for line in fp:
                        if not line.strip() or line.strip().startswith("#"):
                            continue
                        marks.extend(line.partition("#")[0].split())
                return [sanitize(m) for m in marks]

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
        name = "{parent}-{name}".format(parent=srcdir.name, name=path.with_suffix('').name)
        assert name not in items
        items[name] = Item(path)
    return items


def parametrize(arguments, subdir):
    global ALL_SUBDIRS
    datadir = Path(os.getenv("DATADIR", Path(__file__).parent)).absolute()
    srcdir = datadir / subdir

    ALL_SUBDIRS.append(srcdir)
    items = _gather_md_tests(srcdir)

    # we build the parametrized
    def _fn(fn):
        parameters = []
        for name, item in sorted(items.items()):
            marks = [getattr(pytest.mark, m) for m in item.markers or []]
            args = (item.src, item.expected, item.options)
            if "marks" in arguments:
                args = [*args, set(m.name for m in marks)]
            kwargs = {"id": name, "marks": marks}
            param = pytest.param(*args, **kwargs)
            parameters.append(param)
        return pytest.mark.parametrize(arguments, parameters)(fn)

    return _fn


def pytest_addoption(parser):
    group = parser.getgroup("helloworld")
    group.addoption(
        "--list",
        action="store_true",
        dest="list-tests",
        help="list all tests",
    )


def pytest_collection_finish(session):
    if getattr(session.config.option, "list-tests"):
        for subdir in ALL_SUBDIRS:
            for name, item in sorted(_gather_md_tests(subdir).items()):
                print("{} {}".format(name, item.markers))
        pytest.exit("Done!")
