import os
import re
import warnings
from pathlib import Path

import pytest


def _gather_md_tests(srcdir):
    pass



def parametrize(args, subdir):
    datadir = Path(os.getenv("DATADIR", Path(__file__).parent)).absolute()
    srcdir = datadir / subdir

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
    

    sources = {}
    expected = {}
    markers = {}
    options = {}
    
    items = {}
    for path in srcdir.glob("*.text"):
        name = f"{srcdir.name}-{path.name}" 
        assert name not in sources

        items[name] = item = Item(path)

        sources[name] = path
        expected[name] = path.with_suffix(".html")
        assert expected[name].exists()   
        
        # extracts all the tags for path
        src = path.with_suffix(".tags")
        if src.exists():
            markers[name] = [ m.replace("-", "_").replace(".", "_") for m in src.read_text().partition("#")[0].split()]
            

        # extracts all the options
        src = path.with_suffix(".opts")
        if src.exists():
            with warnings.catch_warnings():
                # files as link_patterns_double_hit.opts trigger "invalid escape sequence \s"
                warnings.simplefilter("ignore")
                options[name] = eval(src.read_text())

    # we build the parametrized
    def _fn(fn):
        parameters = []
        for name in sorted(sources):
            kwargs = {"id": name}
            if name in markers:
                kwargs["marks"] = [getattr(pytest.mark, m) for m in markers[name]]
            param = pytest.param(sources[name], expected[name], options.get(name, None), **kwargs)  
            parameters.append(param)
        return pytest.mark.parametrize(args, parameters)(fn)
    return _fn
