#!/usr/bin/env python

"""
Convert [tables](https://github.com/trentm/python-markdown2/wiki/tables)
a given Markdown document such that columns are aligned.

Limitations:
- Can't handle tables where cells have a pipe.
"""

from __future__ import print_function

__version__ = "1.0.0"

import codecs
import os
from pprint import pprint, pformat
import re
import sys
from collections import defaultdict

p = print
def e(*args, **kwargs):
    kwargs['file'] = sys.stderr
    p(*args, **kwargs)



#---- internal support stuff

def tables_align_columns(path):
    def _table_sub(match):
        head, underline, body = match.groups()

        data_rows = [
            [cell.strip() for cell in head.strip().strip('|').split('|')],
        ]
        for line in body.strip('\n').split('\n'):
            data_rows.append([cell.strip() for cell in line.strip().strip('|').split('|')])

        width_from_col_idx = defaultdict(int)
        for data_row in data_rows:
            for col_idx, cell in enumerate(data_row):
                width_from_col_idx[col_idx] = max(
                    2, width_from_col_idx[col_idx], len(cell))

        # Determine aligns for columns.
        ucells = [cell.strip() for cell in underline.strip('| \t\n').split('|')]
        align_from_col_idx = {}
        for col_idx, cell in enumerate(ucells):
            if cell[0] == ':' and cell[-1] == ':':
                align_from_col_idx[col_idx] = 'center'
            elif cell[0] == ':':
                align_from_col_idx[col_idx] = 'left'
            elif cell[-1] == ':':
                align_from_col_idx[col_idx] = 'right'
            else:
                align_from_col_idx[col_idx] = None

        table = []
        for data_row in data_rows:
            row = []
            #e('align_from_col_idx:', align_from_col_idx)
            #e('data_row:', data_row)
            for col_idx, cell in enumerate(data_row):
                width = width_from_col_idx[col_idx]
                try:
                    align = align_from_col_idx[col_idx]
                except KeyError:
                    # Limitation: We hit a table row where a cell has a
                    # literal `|` in it. We can't currently handle that, so
                    # lets just skip this table.
                    e('tables-align-columns: warning: skipping a table '
                      'with literal `|`: %r' % match.group(0))
                    return match.group(0)
                if align == 'center':
                    space = width - len(cell)
                    left = space / 2
                    right = space - left
                    row.append(' '*left + cell + ' '*right)
                elif align == 'right':
                    row.append('%%%ds' % width % cell)
                else:
                    row.append('%%-%ds' % width % cell)
            table.append(row)

        underline = []
        for col_idx, cell in enumerate(data_rows[0]):
            width = width_from_col_idx[col_idx]
            align = align_from_col_idx[col_idx]
            if align == 'center':
                underline.append(':' + u'-'*(width-2) + ':')
            elif align == 'right':
                underline.append(u'-'*(width-1) + ':')
            elif align == 'left':
                underline.append(':' + u'-'*(width-1))
            else:
                underline.append(u'-'*width)
        table[1:1] = [underline]
        #e(pformat(table, width=200))

        table_str = u'\n'.join(('| ' + u' | '.join(r) + ' |') for r in table)
        return table_str + '\n'

    text = codecs.open(path, 'rb', 'utf8').read()

    less_than_tab = 3
    table_re = re.compile(r'''
            (?:(?<=\n\n)|\A\n?)             # leading blank line

            ^[ ]{0,%d}                      # allowed whitespace
            (.*[|].*)  \n                   # $1: header row (at least one pipe)

            ^[ ]{0,%d}                      # allowed whitespace
            (                               # $2: underline row
                # underline row with leading bar
                (?:  \|\ *:?-+:?\ *  )+  \|?  \n
                |
                # or, underline row without leading bar
                (?:  \ *:?-+:?\ *\|  )+  (?:  \ *:?-+:?\ *  )?  \n
            )

            (                               # $3: data rows
                (?:
                    ^[ ]{0,%d}(?!\ )         # ensure line begins with 0 to less_than_tab spaces
                    .*\|.*  \n
                )+
            )
        ''' % (less_than_tab, less_than_tab, less_than_tab), re.M | re.X)
    return table_re.sub(_table_sub, text)




#---- mainline

def main(argv):
    for path in argv[1:]:
        text = tables_align_columns(path)
        sys.stdout.write(text.encode(
            sys.stdout.encoding or "utf-8", 'xmlcharrefreplace'))

if __name__ == "__main__":
    sys.exit( main(sys.argv) )
