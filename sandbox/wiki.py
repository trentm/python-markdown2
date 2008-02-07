
import sys
import re
from os.path import *

sys.path.insert(0, dirname(dirname(abspath(__file__))))
import markdown2

wiki_page = """
# This is my WikiPage!

This is AnotherPage and YetAnotherPage.
"""

link_patterns = [
    # Match a wiki page link LikeThis.
    (re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)"), r"/\1")
]
processor = markdown2.Markdown(extras=["link-patterns"],
                               link_patterns=link_patterns)
print processor.convert(wiki_page)
