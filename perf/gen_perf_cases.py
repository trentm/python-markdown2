#!/usr/bin/env python2.5

import os
from os.path import *
import sys
import re
import datetime
from glob import glob
import operator
import shutil
import codecs


TMP = "tmp-"

def gen_aspn_cases(limit=0):
    base_dir = TMP+'aspn-cases'
    if exists(base_dir):
        print "'%s' exists, skipping" % base_dir
        return 
    os.makedirs(base_dir)
    sys.stdout.write("generate %s" % base_dir); sys.stdout.flush()
    recipes_path = expanduser("~/as/code.as.com/db/aspn/recipes.pprint")
    recipe_dicts = eval(open(recipes_path).read())
    for i, r in enumerate(recipe_dicts):
        sys.stdout.write('.'); sys.stdout.flush()
        f = codecs.open(join(base_dir, "r%04d.text" % i), "w", "utf-8")
        f.write(r["desc"])
        f.close()

        for j, c in enumerate(sorted(r["comments"],
                        key=operator.itemgetter("pub_date"))):
            text = _markdown_from_aspn_html(c["comment"])
            headline = c["title"].strip()
            if headline:
                if headline[-1] not in ".!?,:;'\"":
                    headline += '.'
                headline = _markdown_from_aspn_html(headline).strip()
                text = "**" + headline + "**  " + text
            f = codecs.open(join(base_dir, "r%04dc%02d.text" % (i, j)),
                            'w', "utf-8")
            f.write(text)
            f.close()

        if limit and i >= limit:
            break
    sys.stdout.write('\n')

def gen_test_cases():
    base_dir = TMP+"test-cases"
    if exists(base_dir):
        print "'%s' exists, skipping" % base_dir
        return 
    os.makedirs(base_dir)
    print "generate %s" % base_dir
    for test_cases_dir in glob(join("..", "test", "*-cases")):
        for text_file in glob(join(test_cases_dir, "*.text")):
            shutil.copy(text_file, join(base_dir, basename(text_file)))


#---- internal support stuff

br_pat = re.compile(r"</?br ?/?>", re.I)
br_eol_pat = re.compile(r"</?br ?/?>$", re.I | re.MULTILINE)
pre_pat = re.compile(r"<pre>(.*?)</pre>", re.I | re.DOTALL)
single_line_code_pat = re.compile(r"<(tt|code)>(.*?)</\1>", re.I)
a_pat = re.compile(r'''<a(\s+[\w:-]+=["'].*?["'])*>(.*?)</a>''', re.I | re.S | re.U)
href_attr_pat = re.compile(r'''href=(["'])(.*?)\1''', re.I)
title_attr_pat = re.compile(r'''title=(["'])(.*?)\1''', re.I)
i_pat = re.compile(r"<(i)>(.*?)</\1>", re.I)

def _markdown_from_aspn_html(html):
    from cgi import escape

    markdown = html

    markdown = br_eol_pat.sub('\n', markdown)  # <br>EOL
    markdown = br_pat.sub('\n', markdown)  # <br>

    while True: # <code>, <tt> on a single line
        match = single_line_code_pat.search(markdown)
        if not match:
            break
        markdown = single_line_code_pat.sub(r"`\2`", markdown)

    while True: # <i> on a single line
        match = i_pat.search(markdown)
        if not match:
            break
        markdown = i_pat.sub(r"*\2*", markdown)

    while True: # <a>
        match = a_pat.search(markdown)
        if not match:
            break
        start, end = match.span()
        attrs, content = match.group(1), match.group(2)
        href_match = href_attr_pat.search(attrs)
        if href_match:
            href = href_match.group(2)
        else:
            href = None
        title_match = title_attr_pat.search(attrs)
        if title_match:
            title = title_match.group(2)
        else:
            title = None
        escaped_href = href.replace('(', '\\(').replace(')', '\\)')
        if title is None:
            replacement = '[%s](%s)' % (content, escaped_href)
        else:
            replacement = '[%s](%s "%s")' % (content, escaped_href, 
                                             title.replace('"', "'"))
        markdown = markdown[:start] + replacement + markdown[end:]
        
    markdown = markdown.replace("&nbsp;", ' ')

    # <pre> part 1: Pull out <pre>-blocks and put in placeholders
    pre_marker = "THIS_IS_MY_PRE_MARKER_BLAH"
    pre_blocks = []
    while True: # <pre>
        match = pre_pat.search(markdown)
        if not match:
            break
        start, end = match.span()
        lines = match.group(1).splitlines(0)
        if lines and not lines[0].strip():
            del lines[0]
        _dedentlines(lines)
        pre_blocks.append(lines)
        marker = pre_marker + str(len(pre_blocks) - 1)
        markdown = markdown[:start].rstrip() + marker + markdown[end:].lstrip()

    # <pre> part 2: Put <pre>-blocks back in.
    for i, pre_block in enumerate(pre_blocks):
        marker = pre_marker + str(i)
        try:
            idx = markdown.index(marker)
        except ValueError:
            print "marker: %r" % marker
            raise
        if not markdown[:idx].strip():
            #TODO: Correct this false diagnosis. Problem is not limited
            #      to <h1>
            #TODO: problem with 1203#c6 "Frozen dictionaries": comment title
            #      insertion onto start of an indented-pre/code block
            #
            # There is a bug in python-markdown with an indented block
            # at the start of a buffer: the first line can get rendered
            # as a <h1>. Workaround that by adding a '.' paragraph
            # before.
            # At the time of this writing those comments affected are:
            #    16#c9, 31#c3, 155#c1, 203#c20, 230#c3, 356#c2, 490#c1,
            #    504#c2, 1127#c12
            #log.warn("adding '.'-para Python Markdown hack")
            prefix = ['.']
        else:
            prefix = []
        lines = prefix + ['', ''] + ['    '+ln for ln in lines] + ['', '']
        replacement = '\n'.join(lines)
        markdown = markdown.replace(marker, replacement, 1)

    lines = markdown.splitlines(0)

    # Removing empty lines at start and end.
    while lines and not lines[0].strip():
        del lines[0]
    while lines and not lines[-1].strip():
        del lines[-1]

    # Strip trailing whitespace because don't want auto-<br>'s.
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()

    markdown = '\n'.join(lines) + '\n'

    #TODO: manual fixes:
    # - comment 1, recipe 7

    return markdown

# Recipe: dedent (0.1.2)
def _dedentlines(lines, tabsize=8, skip_first_line=False):
    """_dedentlines(lines, tabsize=8, skip_first_line=False) -> dedented lines
    
        "lines" is a list of lines to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.
    
    Same as dedent() except operates on a sequence of lines. Note: the
    lines list is modified **in-place**.
    """
    DEBUG = False
    if DEBUG: 
        print "dedent: dedent(..., tabsize=%d, skip_first_line=%r)"\
              % (tabsize, skip_first_line)
    indents = []
    margin = None
    for i, line in enumerate(lines):
        if i == 0 and skip_first_line: continue
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += tabsize - (indent % tabsize)
            elif ch in '\r\n':
                continue # skip all-whitespace lines
            else:
                break
        else:
            continue # skip all-whitespace lines
        if DEBUG: print "dedent: indent=%d: %r" % (indent, line)
        if margin is None:
            margin = indent
        else:
            margin = min(margin, indent)
    if DEBUG: print "dedent: margin=%r" % margin

    if margin is not None and margin > 0:
        for i, line in enumerate(lines):
            if i == 0 and skip_first_line: continue
            removed = 0
            for j, ch in enumerate(line):
                if ch == ' ':
                    removed += 1
                elif ch == '\t':
                    removed += tabsize - (removed % tabsize)
                elif ch in '\r\n':
                    if DEBUG: print "dedent: %r: EOL -> strip up to EOL" % line
                    lines[i] = lines[i][j:]
                    break
                else:
                    raise ValueError("unexpected non-whitespace char %r in "
                                     "line %r while removing %d-space margin"
                                     % (ch, line, margin))
                if DEBUG:
                    print "dedent: %r: %r -> removed %d/%d"\
                          % (line, ch, removed, margin)
                if removed == margin:
                    lines[i] = lines[i][j+1:]
                    break
                elif removed > margin:
                    lines[i] = ' '*(removed-margin) + lines[i][j+1:]
                    break
            else:
                if removed:
                    lines[i] = lines[i][removed:]
    return lines

def _dedent(text, tabsize=8, skip_first_line=False):
    """_dedent(text, tabsize=8, skip_first_line=False) -> dedented text

        "text" is the text to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.
    
    textwrap.dedent(s), but don't expand tabs to spaces
    """
    lines = text.splitlines(1)
    _dedentlines(lines, tabsize=tabsize, skip_first_line=skip_first_line)
    return ''.join(lines)


#---- mainline

if __name__ == "__main__":
    try:
        limit = int(sys.argv[1])
    except:
        limit = 0
    gen_aspn_cases(limit)
    gen_test_cases()

