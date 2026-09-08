"""Regression tests for the markdown2 command line interface."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FileVarsTestCase(unittest.TestCase):
    source = "<!-- -*- markdown-extras: header-ids -*- -->\n# Heading\n"
    script = Path(__file__).resolve().parent.parent / "lib" / "markdown2.py"

    def run_cli(self, *args, text=""):
        result = subprocess.run(
            [sys.executable, str(self.script), *map(str, args)],
            input=text,
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_file_vars_from_stdin(self):
        html = self.run_cli("--use-file-vars", text=self.source)
        self.assertIn('<h1 id="heading">Heading</h1>', html)

    def test_file_vars_before_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.md"
            path.write_text(self.source, encoding="utf-8")
            html = self.run_cli("--use-file-vars", path)
        self.assertIn('<h1 id="heading">Heading</h1>', html)

    def test_file_vars_after_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.md"
            path.write_text(self.source, encoding="utf-8")
            html = self.run_cli(path, "--use-file-vars")
        self.assertIn('<h1 id="heading">Heading</h1>', html)

    def test_file_vars_with_multiple_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [
                Path(directory) / name for name in ("first.md", "second.md")
            ]
            for path in paths:
                path.write_text(self.source, encoding="utf-8")
            html = self.run_cli("--use-file-vars", *paths)
        self.assertEqual(html.count('<h1 id="heading">Heading</h1>'), 2)

    def test_file_vars_with_output_option(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.html"
            stdout = self.run_cli(
                "--use-file-vars", "--output", output, text=self.source
            )
            self.assertEqual(stdout, "")
            html = output.read_text(encoding="utf-8")
        self.assertIn('<h1 id="heading">Heading</h1>', html)

    def test_file_vars_are_disabled_by_default(self):
        html = self.run_cli(text=self.source)
        self.assertIn("<h1>Heading</h1>", html)
        self.assertNotIn('id="heading"', html)
