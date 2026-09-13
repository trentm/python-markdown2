"""Reproduce #635 with synthetic distinct code spans; no timing assertions.

Run with the same interpreter before and after the change:
    python perf/issue635.py
"""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
import markdown2


def measure(count):
    source = '\n\n'.join('`value_%s`' % i for i in range(count))
    expected = '\n\n'.join('<p><code>value_%s</code></p>' % i for i in range(count)) + '\n'
    totals, unescapes = [], []
    for _ in range(3):
        converter = markdown2.Markdown()
        original = converter._unescape_special_chars
        timings = []

        def timed(text):
            start = time.perf_counter()
            result = original(text)
            timings.append(time.perf_counter() - start)
            return result

        converter._unescape_special_chars = timed
        start = time.perf_counter()
        output = converter.convert(source)
        totals.append(time.perf_counter() - start)
        unescapes.append(sum(timings))
        assert output == expected
    return {
        'spans': count,
        'total_seconds_median': statistics.median(totals),
        'unescape_seconds_median': statistics.median(unescapes),
        'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
    }


if __name__ == '__main__':
    print(json.dumps({'python': sys.version, 'runs': [measure(n) for n in (500, 1000, 2000, 4000)]}, indent=2))
