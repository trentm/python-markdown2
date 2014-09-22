#!/usr/bin/env python

"""
Convert a Markdown document using
[wiki-tables](https://github.com/trentm/python-markdown2/wiki/wiki-tables)
to a Markdown document using
[tables](https://github.com/trentm/python-markdown2/wiki/tables)

Limitations:
- Doesn't handle tables inside blockquotes.
- "tables" require a head section, "wiki-tables" does not. That creates an
  ambiguity on conversion: what to use for the head row? We'll do the
  following.

  First we'll look at the first row, and if the cells are em'd or strong'd
  like this:

        ||**Param**||**Type**||**Description**||
        ||kernel_args||Object||Boot parms to update||
        ||boot_modules||Array||List of boot module objects||
        ||kernel_flags||Object||Kernel flags to update||
        ||platform||String||Set platform as the bootable platform||

        ||*Code*||*Type*||*Description*||
        ||204||None||Boot parameters successfully set||
        ||404||None||No such Server||

  Then we'll use that as the header row. If not we'll bail. This is "strict"
  mode... and the only supported mode for now.
"""

from __future__ import print_function

__version__ = "1.0.0"

import codecs
import os
from pprint import pprint, pformat
import re
import sys

p = print
def e(*args, **kwargs):
    kwargs['file'] = sys.stderr
    p(*args, **kwargs)



#---- internal support stuff

def wiki_tables_to_tables(path):
    def _wiki_table_sub(match):
        ttext = match.group(0).strip()
        #e('wiki table: %r' % match.group(0))
        rows = []
        for line in ttext.splitlines(0):
            line = line.strip()[2:-2].strip()
            row = [c.strip() for c in re.split(r'(?<!\\)\|\|', line)]
            rows.append(row)
        #e(pformat(rows))

        head = []
        for cell in rows[0]:
            if cell.startswith('**') and cell.endswith('**'):
                head.append(cell[2:-2].strip())
            elif cell.startswith('*') and cell.endswith('*'):
                head.append(cell[1:-1].strip())
            else:
                raise RuntimeError(
                    'wiki-table in "%s" has no header row, bailing: %r'
                    % (path, ttext))

        underline = []
        for cell in head:
            underline.append('-' * max(1, len(cell)))

        body = rows[1:]
        table = [head, underline] + body
        table_str = '\n'.join(('| ' + ' | '.join(r) + ' |') for r in table)
        return table_str + '\n'

    text = codecs.open(path, 'rb', 'utf8').read()

    # If there is a leading markdown2 metadata block with;
    #    markdown2extras: ..., wiki-tables, ...
    # then update that to 'tables'.
    _metadata_pat = re.compile("""^---[ \t]*\n((?:[ \t]*[^ \t:]+[ \t]*:[^\n]*\n)+)---[ \t]*\n""")
    match = _metadata_pat.match(text)
    if match:
        metadata_str = match.group(0)
        if re.search(r'^markdown2extras\s*:.*?\bwiki-tables\b', metadata_str, re.M):
            text = text.replace('wiki-tables', 'tables', 1)

    less_than_tab = 3
    wiki_table_re = re.compile(r'''
        (?:(?<=\n\n)|\A\n?)            # leading blank line
        ^([ ]{0,%d})\|\|.+?\|\|[ ]*\n  # first line
        (^\1\|\|.+?\|\|\n)*        # any number of subsequent lines
        ''' % less_than_tab, re.M | re.X)
    return wiki_table_re.sub(_wiki_table_sub, text)




#---- mainline

def main(argv):
    for path in argv[1:]:
        tables = wiki_tables_to_tables(path)
        sys.stdout.write(tables.encode(
            sys.stdout.encoding or "utf-8", 'xmlcharrefreplace'))

if __name__ == "__main__":
    sys.exit( main(sys.argv) )
