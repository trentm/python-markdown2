"""Tests for reused Markdown instance state isolation (issue #763)."""

import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
import markdown2  # noqa: E402


class TestReuseInstanceIsolation(unittest.TestCase):
    """Each convert() call on a reused instance must behave like a fresh one."""

    def test_escape_table_reset_between_calls(self):
        """Backslash-escaped text must not be affected by a previous convert()."""
        md = markdown2.Markdown()
        md.convert("[a link](https://example.com/page)")
        result_reused = md.convert(r"Type \https://example.com/page to see it.")
        result_fresh = markdown2.Markdown().convert(r"Type \https://example.com/page to see it.")
        self.assertEqual(result_reused, result_fresh)

    def test_code_table_reset_between_calls(self):
        """Code spans from earlier documents must not leak into later ones."""
        md = markdown2.Markdown()
        md.convert("`first_code_span`")
        # The hash for first_code_span must not persist and corrupt the new doc
        result_reused = md.convert("plain `second_code_span` text")
        result_fresh = markdown2.Markdown().convert("plain `second_code_span` text")
        self.assertEqual(result_reused, result_fresh)

    def test_performance_does_not_degrade(self):
        """Processing time per document must not grow with the number of documents."""
        md = markdown2.Markdown()
        doc = "[link{}](https://example.com) `code{}`\n"

        # warm up
        for i in range(5):
            md.convert(doc.format(i, i))

        t_start_early = time.monotonic()
        for i in range(5, 10):
            md.convert(doc.format(i, i))
        t_early = time.monotonic() - t_start_early

        # process 50 more documents to accumulate stale table entries
        for i in range(10, 60):
            md.convert(doc.format(i, i))

        t_start_late = time.monotonic()
        for i in range(60, 65):
            md.convert(doc.format(i, i))
        t_late = time.monotonic() - t_start_late

        # With the fix, late processing is not significantly slower than early.
        # Use max(..., 1e-5) so the comparison is valid when both times round
        # to 0.0 on fast CI runners (Windows).
        self.assertLess(t_late, max(t_early, 1e-5) * 10,
                        f"Performance degraded: early={t_early*1000:.1f}ms late={t_late*1000:.1f}ms")


if __name__ == "__main__":
    unittest.main()
