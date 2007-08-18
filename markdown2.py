#!/usr/bin/env python
# Copyright (c) 2007 ActiveState Corp.

"""Another Python implementation of Markdown

Markdown is "a text-to-HTML conversion tool for web writers"
(http://daringfireball.net/projects/markdown/).  There is already a
Python markdown processor
(http://www.freewisdom.org/projects/python-markdown/) but (1) I've run
into a number of problems with it (improper Markdown processing) and (2)
emails to the author's given contact address have bounced.

[from Markdown.pl] Markdown is a text-to-HTML filter; it translates an
easy-to-read / easy-to-write structured text format into HTML.
Markdown's text format is most similar to that of plain text email, and
supports features such as headers, *emphasis*, code blocks, blockquotes,
and links.

Markdown's syntax is designed not as a generic markup language, but
specifically to serve as a front-end to (X)HTML. You can  use span-level
HTML tags anywhere in a Markdown document, and you can use block level
HTML tags (like <div> and <table> as well).
"""
#Dev Notes:
# - Python's regex syntax doesn't have '\z', so I'm using '\Z'. I'm
#   not yet sure if there implications with this. Compare 'pydoc sre'
#   and 'perldoc perlre'.

__version_info__ = (1, 0, 1, 0) # first three nums match Markdown.pl
__version__ = '.'.join(map(str, __version_info__))

import os
import sys
from pprint import pprint
import re
import logging
import md5
import optparse
from random import random


#---- globals

DEBUG = False
log = logging.getLogger("markdown")

DEFAULT_TAB_WIDTH = 4

# Table of hash values for escaped characters:
g_escape_table = dict((ch, md5.md5(ch).hexdigest())
                      for ch in '\\`*_{}[]()>#+-.!')



#---- exceptions

class MarkdownError(Exception):
    pass



#---- public api

def markdown_path(path, html4tags=False, tab_width=DEFAULT_TAB_WIDTH):
    text = open(path, 'r').read()
    return Markdown(html4tags=html4tags, tab_width=tab_width).convert(text)

def markdown(text, html4tags=False, tab_width=DEFAULT_TAB_WIDTH):
    return Markdown(html4tags=html4tags, tab_width=tab_width).convert(text)

class Markdown(object):
    urls = None
    titles = None
    html_blocks = None

    # Used to track when we're inside an ordered or unordered list
    # (see _ProcessListItems() for details):
    list_level = 0

    _ws_only_line_re = re.compile(r"^[ \t]+$", re.M)

    def __init__(self, html4tags=False, tab_width=4):
        if html4tags:
            self.empty_element_suffix = ">"
        else:
            self.empty_element_suffix = " />"
        self.tab_width = tab_width
        self._outdent_re = re.compile(r'^(\t|[ ]{1,%d})' % tab_width, re.M)

    def reset(self):
        self.urls = {}
        self.titles = {}
        self.html_blocks = {}
        self.list_level = 0

    def convert(self, text):
        """Convert the given text."""
        # Main function. The order in which other subs are called here is
        # essential. Link and image substitutions need to happen before
        # _EscapeSpecialChars(), so that any *'s or _'s in the <a>
        # and <img> tags get encoded.

        # Clear the global hashes. If we don't clear these, you get conflicts
        # from other articles when generating a page which contains more than
        # one article (e.g. an index page that shows the N most recent
        # articles):
        self.reset()

        # Standardize line endings:
        text = re.sub("\r\n|\r", "\n", text)

        # Make sure $text ends with a couple of newlines:
        text += "\n\n"

        # Convert all tabs to spaces.
        text = self._detab(text)

        # Strip any lines consisting only of spaces and tabs.
        # This makes subsequent regexen easier to write, because we can
        # match consecutive blank lines with /\n+/ instead of something
        # contorted like /[ \t]*\n+/ .
        text = self._ws_only_line_re.sub("", text)

        # Turn block-level HTML blocks into hash entries
        text = self._hash_html_blocks(text)
        #print "XXX ----\n", text, "----"

        # Strip link definitions, store in hashes.
        text = self._strip_link_definitions(text)

        text = self._run_block_gamut(text)

        text = self._unescape_special_chars(text)
        return text + "\n"

    # Cribbed from a post by Bart Lateur:
    # <http://www.nntp.perl.org/group/perl.macperl.anyperl/154>
    _detab_re = re.compile(r'^(.*?)\t', re.M)
    def _detab_sub(self, match):
        g1 = match.group(1)
        return g1 + (' ' * (self.tab_width - len(g1) % self.tab_width))
    def _detab(self, text):
        r"""Remove (leading?) tabs from a file.

            >>> m = Markdown()
            >>> m._detab("\tfoo")
            '    foo'
            >>> m._detab("  \tfoo")
            '    foo'
            >>> m._detab("\t  foo")
            '      foo'
            >>> m._detab("  foo")
            '  foo'
            >>> m._detab("  foo\n\tbar\tblam")
            '  foo\n    bar blam'
        """
        return self._detab_re.sub(self._detab_sub, text)

    def _hash_html_block_sub(self, match):
        g1 = match.group(1)
        key = md5.md5(g1).hexdigest()
        self.html_blocks[key] = g1
        return "\n\n" + key + "\n\n"

    def _hash_html_blocks(self, text):
        less_than_tab = self.tab_width - 1

        # Hashify HTML blocks:
        # We only want to do this for block-level HTML tags, such as headers,
        # lists, and tables. That's because we still want to wrap <p>s around
        # "paragraphs" that are wrapped in non-block-level tags, such as anchors,
        # phrase emphasis, and spans. The list of tags we're looking for is
        # hard-coded:
        block_tags_a = 'p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|script|noscript|form|fieldset|iframe|math|ins|del'
        block_tags_b = 'p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|script|noscript|form|fieldset|iframe|math'

        # First, look for nested blocks, e.g.:
        #   <div>
        #       <div>
        #       tags for inner block must be indented.
        #       </div>
        #   </div>
        #
        # The outermost tags must start at the left margin for this to match, and
        # the inner nested divs must be indented.
        # We need to do this before the next, more liberal match, because the next
        # match will start at the first `<div>` and stop at the first `</div>`.
        _strict_tag_block_re = re.compile(r"""
            (                       # save in \1
                ^                   # start of line  (with re.M)
                <(%s)               # start tag = \2
                \b                  # word break
                (.*\n)*?            # any number of lines, minimally matching
                </\2>               # the matching end tag
                [ \t]*              # trailing spaces/tabs
                (?=\n+|\Z)          # followed by a newline or end of document
            )
            """ % block_tags_a,
            re.X | re.M)
        text = _strict_tag_block_re.sub(self._hash_html_block_sub, text)

        # Now match more liberally, simply from `\n<tag>` to `</tag>\n`
        _liberal_tag_block_re = re.compile(r"""
            (                       # save in \1
                ^                   # start of line  (with re.M)
                <(%s)               # start tag = \2
                \b                  # word break
                (.*\n)*?            # any number of lines, minimally matching
                .*</\2>             # the matching end tag
                [ \t]*              # trailing spaces/tabs
                (?=\n+|\Z)          # followed by a newline or end of document
            )
            """ % block_tags_b,
            re.X | re.M)
        text = _liberal_tag_block_re.sub(self._hash_html_block_sub, text)

        # Special case just for <hr />. It was easier to make a special
        # case than to make the other regex more complicated.   
        _hr_tag_re = re.compile(r"""
            (?:
                (?<=\n\n)       # Starting after a blank line
                |               # or
                \A\n?           # the beginning of the doc
            )
            (                       # save in \1
                [ ]{0,%d}
                <(hr)               # start tag = \2
                \b                  # word break
                ([^<>])*?           # 
                /?>                 # the matching end tag
                [ \t]*
                (?=\n{2,}|\Z)       # followed by a blank line or end of document
            )
            """ % less_than_tab, re.X)
        text = _hr_tag_re.sub(self._hash_html_block_sub, text)

        # Special case for standalone HTML comments:
        _html_comment_re = re.compile(r"""
            (?:
                (?<=\n\n)       # Starting after a blank line
                |               # or
                \A\n?           # the beginning of the doc
            )
            (                       # save in $1
                [ ]{0,%d}
                (?:
                    <!
                    (--.*?--\s*)+
                    >
                )
                [ \t]*
                (?=\n{2,}|\Z)       # followed by a blank line or end of document
            )
            """ % less_than_tab, re.X | re.S)
        text = _html_comment_re.sub(self._hash_html_block_sub, text)

        return text


    def _strip_link_definitions(self, text):
        # Strips link definitions from text, stores the URLs and titles in
        # hash references.
        less_than_tab = self.tab_width - 1
    
        # Link defs are in the form: ^[id]: url "optional title"
        _link_def_re = re.compile(r"""
            ^[ ]{0,%d}\[(.+)\]: # id = \1
              [ \t]*
              \n?               # maybe *one* newline
              [ \t]*
            <?(\S+?)>?          # url = \2
              [ \t]*
              \n?               # maybe one newline
              [ \t]*
            (?:
                (?<=\s)         # lookbehind for whitespace
                ["(]
                (.+?)           # title = \3
                [")]
                [ \t]*
            )?  # title is optional
            (?:\n+|\Z)
            """ % less_than_tab, re.X | re.M)
        return _link_def_re.sub(self._extract_link_def_sub, text)

    def _extract_link_def_sub(self, match):
        id, url, title = match.groups()
        key = id.lower()    # Link IDs are case-insensitive
        self.urls[key] = self._encode_amps_and_angles(url)
        if title:
            self.titles[key] = title.replace('"', '&quot;')
        return ""

    _hr_res = [
        re.compile(r"^[ ]{0,2}([ ]?\*[ ]?){3,}[ \t]*$", re.M),
        re.compile(r"^[ ]{0,2}([ ]?\-[ ]?){3,}[ \t]*$", re.M),
        re.compile(r"^[ ]{0,2}([ ]?\_[ ]?){3,}[ \t]*$", re.M),
    ]

    def _run_block_gamut(self, text):
        # These are all the transformations that form block-level
        # tags like paragraphs, headers, and list items.

        text = self._do_headers(text)

        # Do Horizontal Rules:
        hr = "\n<hr"+self.empty_element_suffix+"\n"
        for hr_re in self._hr_res:
            text = hr_re.sub(hr, text)

        text = self._do_lists(text)

        text = self._do_code_blocks(text)

        text = self._do_block_quotes(text)

        # We already ran _HashHTMLBlocks() before, in Markdown(), but that
        # was to escape raw HTML in the original Markdown source. This time,
        # we're escaping the markup we've just created, so that we don't wrap
        # <p> tags around block-level tags.
        text = self._hash_html_blocks(text)

        text = self._form_paragraphs(text)

        return text

    def _run_span_gamut(self, text):
        # These are all the transformations that occur *within* block-level
        # tags like paragraphs, headers, and list items.
    
        text = self._do_code_spans(text)
    
        text = self._escape_special_chars(text)
    
        # Process anchor and image tags.
        text = self._do_links(text)
    
        # Make links out of things like `<http://example.com/>`
        # Must come after _do_links(), because you can use < and >
        # delimiters in inline links like [this](<url>).
        text = self._do_auto_links(text)
    
        text = self._encode_amps_and_angles(text)
    
        text = self._do_italics_and_bold(text)
    
        # Do hard breaks:
        text = re.sub(r" {2,}\n", " <br%s\n" % self.empty_element_suffix, text)
    
        return text

    _html_tokenize_re = re.compile(r"""
        (
            # tag
            </?         
            (?:\w+)                                     # tag name
            (?:\s+(?:[\w-]+:)?[\w-]+=(?:".*?"|'.*?'))*  # attributes
            \s*/?>
            |
            <!--.*?-->      # comment
            |
            <\?.*?\?>       # processing instruction
        )
        """, re.X)
    
    def _escape_special_chars(self, text):
        # Python markdown note: the HTML tokenization here differs from
        # that in Markdown.pl, hence the behaviour for subtle cases can
        # differ (I believe the tokenizer here does a better job because
        # it isn't susceptible to unmatched '<' and '>' in HTML tags).
        escaped = []
        is_tag = False
        for token in self._html_tokenize_re.split(text):
            if is_tag:
                # Within tags, encode * and _ so they don't conflict
                # with their use in Markdown for italics and strong.
                # We're replacing each such character with its
                # corresponding MD5 checksum value; this is likely
                # overkill, but it should prevent us from colliding
                # with the escape values by accident.
                escaped.append(token.replace('*', g_escape_table['*'])
                                    .replace('_', g_escape_table['_']))
            else:
                escaped.append(self._encode_backslash_escapes(token))
            is_tag = not is_tag
        return ''.join(escaped)

    _tail_of_inline_link_re = re.compile(r'''
          # Match tail of: [text](/url/) or [text](/url/ "title")
          \(            # literal paren
            [ \t]*
            <?(?P<url>.*?)>?    # \1
            [ \t]*
            (                   # \2
              (['"])            # quote char = \3
              (?P<title>.*?)
              \3                # matching quote
            )?                  # title is optional
          \)
        ''', re.X | re.S)
    _tail_of_reference_link_re = re.compile(r'''
          # Match tail of: [text][id]
          [ ]?          # one optional space
          (?:\n[ ]*)?   # one optional newline followed by spaces
          \[
            (?P<id>.*?)
          \]
        ''', re.X | re.S)

    def _do_links(self, text):
        """Turn Markdown link shortcuts into XHTML <a> and <img> tags.

        This is a combination of Markdown.pl's _DoAnchors() and
        _DoImages(). They are done together because that simplified the
        approach. It was necessary to use a different approach than
        Markdown.pl because of the lack of atomic matching support in
        Python's regex engine used in $g_nested_brackets.
        """
        MAX_LINK_TEXT_SENTINEL = 300

        curr_pos = 0
        while True: # Handle the next link.
            # The next '[' is the start of:
            # - an inline anchor:   [text](url "title")
            # - a reference anchor: [text][id]
            # - an inline img:      ![text](url "title")
            # - a reference img:    ![text][id]
            # - a link definition:  [id]: url "title"
            #   These have already been stripped in
            #   _strip_link_definitions() so no need to watch for them.
            # - not markup:         [...anything else...
            try:
                start_idx = text.index('[', curr_pos)
            except ValueError:
                break
            text_length = len(text)

            # Find the matching closing ']'.
            # Markdown.pl allows *matching* brackets in link text so we
            # will here too. Markdown.pl *doesn't* currently allow
            # matching brackets in img alt text -- we'll differ in that
            # regard.
            bracket_depth = 0
            for p in range(start_idx+1, min(start_idx+MAX_LINK_TEXT_SENTINEL, 
                                            text_length-1)):
                ch = text[p]
                if ch == ']':
                    bracket_depth -= 1
                    if bracket_depth < 0:
                        break
                elif ch == '[':
                    bracket_depth += 1
            else:
                # Closing bracket not found within sentinel length.
                # This isn't markup.
                curr_pos = start_idx + 1
                continue
            link_text = text[start_idx+1:p]

            # Now determine what this in by the remainder.
            p += 1
            if p == text_length:
                return text

            # Inline anchor or img?
            if text[p] == '(': # attempt at perf improvement
                match = self._tail_of_inline_link_re.match(text, p)
                if match:
                    # Handle an inline anchor or img.
                    is_img = start_idx > 0 and text[start_idx-1] == "!"
                    if is_img:
                        start_idx -= 1

                    url, title = match.group("url"), match.group("title")
                    # We've got to encode these to avoid conflicting
                    # with italics/bold.
                    url = url.replace('*', g_escape_table['*']) \
                             .replace('_', g_escape_table['_'])
                    if title or is_img:
                        if is_img and title is None:
                            # Markdown.pl includes title='' on image
                            # links. Not *sure* this is intended.
                            title = ""
                        title_str = ' title="%s"' \
                            % title.replace('*', g_escape_table['*']) \
                                   .replace('_', g_escape_table['_']) \
                                   .replace('"', '&quot;')
                    else:
                        title_str = ''
                    if is_img:
                        result = '<img src="%s" alt="%s"%s%s' \
                            % (url, link_text.replace('"', '&quot;'),
                               title_str, self.empty_element_suffix)
                    else:
                        result = '<a href="%s"%s>%s</a>' \
                                 % (url, title_str, link_text)
                    text = text[:start_idx] + result + text[match.end():]
                    curr_pos = start_idx + len(result)
                    continue

            # Reference anchor or img?
            else:
                match = self._tail_of_reference_link_re.match(text, p)
                if match:
                    # Handle a reference-style anchor or img.
                    is_img = start_idx > 0 and text[start_idx-1] == "!"
                    if is_img:
                        start_idx -= 1
                    link_id = match.group("id").lower()
                    if not link_id:
                        link_id = link_text.lower()  # for links like [this][]
                    if link_id in self.urls:
                        url = self.urls[link_id]
                        # We've got to encode these to avoid conflicting
                        # with italics/bold.
                        url = url.replace('*', g_escape_table['*']) \
                                 .replace('_', g_escape_table['_'])
                        title = self.titles.get(link_id)
                        if title:
                            title = title.replace('*', g_escape_table['*']) \
                                         .replace('_', g_escape_table['_'])
                            title_str = ' title="%s"' % title
                        else:
                            title_str = ''
                        if is_img:
                            result = '<img src="%s" alt="%s"%s%s' \
                                % (url, link_text.replace('"', '&quot;'),
                                   title_str, self.empty_element_suffix)
                        else:
                            result = '<a href="%s"%s>%s</a>' \
                                % (url, title_str, link_text)
                        text = text[:start_idx] + result + text[match.end():]
                        curr_pos = start_idx + len(result)
                    else:
                        # This id isn't defined, leave the markup alone.
                        curr_pos = match.end()
                    continue

            # Otherwise, it isn't markup.
            curr_pos = start_idx + 1

        return text 


    _setext_h_re = re.compile(r'^(.+)[ \t]*\n(=+|-+)[ \t]*\n+', re.M)
    def _setext_h_sub(self, match):
        n = {"=": 1, "-": 2}[match.group(2)[0]]
        return "<h%d>%s</h%d>\n\n" \
               % (n, self._run_span_gamut(match.group(1)), n)

    _atx_h_re = re.compile(r'''
        ^(\#{1,6})  # \1 = string of #'s
        [ \t]*
        (.+?)       # \2 = Header text
        [ \t]*
        \#*         # optional closing #'s (not counted)
        \n+
        ''', re.X | re.M)
    def _atx_h_sub(self, match):
        n = len(match.group(1))
        return "<h%d>%s</h%d>\n\n" \
               % (n, self._run_span_gamut(match.group(2)), n)

    def _do_headers(self, text):
        # Setext-style headers:
        #     Header 1
        #     ========
        #  
        #     Header 2
        #     --------
        text = self._setext_h_re.sub(self._setext_h_sub, text)

        # atx-style headers:
        #   # Header 1
        #   ## Header 2
        #   ## Header 2 with closing hashes ##
        #   ...
        #   ###### Header 6
        text = self._atx_h_re.sub(self._atx_h_sub, text)

        return text


    _marker_ul_chars  = '*+-'
    _marker_any = '(?:[%s]|\d+[.])' % _marker_ul_chars

    def _list_sub(self, match):
        lst = match.group(1)
        lst_type = match.group(3) in self._marker_ul_chars and "ul" or "ol"
        result = self._process_list_items(lst)
        return "<%s>\n%s</%s>\n" % (lst_type, result, lst_type)

    def _do_lists(self, text):
        # Form HTML ordered (numbered) and unordered (bulleted) lists.

        # Re-usable pattern to match any entire ul or ol list:
        less_than_tab = self.tab_width - 1
        whole_list = r'''
            (                   # \1 = whole list
              (                 # \2
                [ ]{0,%d}
                (%s)            # \3 = first list item marker
                [ \t]+
              )
              (?:.+?)
              (                 # \4
                  \Z
                |
                  \n{2,}
                  (?=\S)
                  (?!           # Negative lookahead for another list item marker
                    [ \t]*
                    %s[ \t]+
                  )
              )
            )
        ''' % (less_than_tab, self._marker_any, self._marker_any)
    
        # We use a different prefix before nested lists than top-level lists.
        # See extended comment in _process_list_items().
        #
        # Note: There's a bit of duplication here. My original implementation
        # created a scalar regex pattern as the conditional result of the test on
        # $g_list_level, and then only ran the $text =~ s{...}{...}egmx
        # substitution once, using the scalar as the pattern. This worked,
        # everywhere except when running under MT on my hosting account at Pair
        # Networks. There, this caused all rebuilds to be killed by the reaper (or
        # perhaps they crashed, but that seems incredibly unlikely given that the
        # same script on the same server ran fine *except* under MT. I've spent
        # more time trying to figure out why this is happening than I'd like to
        # admit. My only guess, backed up by the fact that this workaround works,
        # is that Perl optimizes the substition when it can figure out that the
        # pattern will never change, and when this optimization isn't on, we run
        # afoul of the reaper. Thus, the slightly redundant code to that uses two
        # static s/// patterns rather than one conditional pattern.

        if self.list_level:
            sub_list_re = re.compile("^"+whole_list, re.X | re.M | re.S)
            text = sub_list_re.sub(self._list_sub, text)
        else:
            list_re = re.compile(r"(?:(?<=\n\n)|\A\n?)"+whole_list,
                                 re.X | re.M | re.S)
            text = list_re.sub(self._list_sub, text)
    
        return text
    
    _list_item_re = re.compile(r'''
        (\n)?               # leading line = \1
        (^[ \t]*)           # leading whitespace = \2
        (%s) [ \t]+         # list marker = \3
        ((?:.+?)            # list item text = \4
         (\n{1,2}))         # eols = \5
        (?= \n* (\Z | \2 (%s) [ \t]+))
        ''' % (_marker_any, _marker_any),
        re.M | re.X | re.S)

    _last_li_endswith_two_eols = False
    def _list_item_sub(self, match):
        item = match.group(4)
        leading_line = match.group(1)
        leading_space = match.group(2)
        if leading_line or "\n\n" in item or self._last_li_endswith_two_eols:
            item = self._run_block_gamut(self._outdent(item))
        else:
            # Recursion for sub-lists:
            item = self._do_lists(self._outdent(item))
            if item.endswith('\n'):
                item = item[:-1]
            item = self._run_span_gamut(item)
        self._last_li_endswith_two_eols = (len(match.group(5)) == 2)
        return "<li>%s</li>\n" % item

    def _process_list_items(self, list_str):
        # Process the contents of a single ordered or unordered list,
        # splitting it into individual list items.
    
        # The $g_list_level global keeps track of when we're inside a list.
        # Each time we enter a list, we increment it; when we leave a list,
        # we decrement. If it's zero, we're not in a list anymore.
        #
        # We do this because when we're not inside a list, we want to treat
        # something like this:
        #
        #       I recommend upgrading to version
        #       8. Oops, now this line is treated
        #       as a sub-list.
        #
        # As a single paragraph, despite the fact that the second line starts
        # with a digit-period-space sequence.
        #
        # Whereas when we're inside a list (or sub-list), that line will be
        # treated as the start of a sub-list. What a kludge, huh? This is
        # an aspect of Markdown's syntax that's hard to parse perfectly
        # without resorting to mind-reading. Perhaps the solution is to
        # change the syntax rules such that sub-lists must start with a
        # starting cardinal number; e.g. "1." or "a.".
        self.list_level += 1
        self._last_li_endswith_two_eols = False
        list_str = list_str.rstrip('\n') + '\n'
        list_str = self._list_item_re.sub(self._list_item_sub, list_str)
        self.list_level -= 1
        return list_str


    def _code_block_sub(self, match):
        codeblock = match.group(1)
        codeblock = self._encode_code(self._outdent(codeblock))
        codeblock = self._detab(codeblock)
        codeblock = codeblock.lstrip('\n')  # trim leading newlines
        codeblock = codeblock.rstrip()      # trim trailing whitespace
        return "\n\n<pre><code>%s\n</code></pre>\n\n" % codeblock

    def _do_code_blocks(self, text):
        """Process Markdown `<pre><code>` blocks."""
        code_block_re = re.compile(r'''
            (?:\n\n|\A)
            (               # $1 = the code block -- one or more lines, starting with a space/tab
              (?:
                (?:[ ]{%d} | \t)  # Lines must start with a tab or a tab-width of spaces
                .*\n+
              )+
            )
            ((?=^[ ]{0,%d}\S)|\Z)   # Lookahead for non-space at line-start, or end of doc
            ''' % (self.tab_width, self.tab_width),
            re.M | re.X)

        return code_block_re.sub(self._code_block_sub, text)


    _code_span_re = re.compile(r'''
            (`+)        # \1 = Opening run of `
            (.+?)       # \2 = The code block
            (?<!`)
            \1          # Matching closer
            (?!`)
        ''', re.X | re.S)

    def _code_span_sub(self, match):
        c = match.group(2).strip(" \t")
        c = self._encode_code(c)
        return "<code>%s</code>" % c

    def _do_code_spans(self, text):
        #   *   Backtick quotes are used for <code></code> spans.
        # 
        #   *   You can use multiple backticks as the delimiters if you want to
        #       include literal backticks in the code span. So, this input:
        #     
        #         Just type ``foo `bar` baz`` at the prompt.
        #     
        #       Will translate to:
        #     
        #         <p>Just type <code>foo `bar` baz</code> at the prompt.</p>
        #     
        #       There's no arbitrary limit to the number of backticks you
        #       can use as delimters. If you need three consecutive backticks
        #       in your code, use four for delimiters, etc.
        #
        #   *   You can use spaces to get literal backticks at the edges:
        #     
        #         ... type `` `bar` `` ...
        #     
        #       Turns to:
        #     
        #         ... type <code>`bar`</code> ...
        return self._code_span_re.sub(self._code_span_sub, text)

    def _encode_code(self, text):
        """Encode/escape certain characters inside Markdown code runs.
        The point is that in code, these characters are literals,
        and lose their special Markdown meanings.
        """
        replacements = [
            # Encode all ampersands; HTML entities are not
            # entities within a Markdown code span.
            ('&', '&amp;'),
            # Do the angle bracket song and dance:
            ('<', '&lt;'),
            ('>', '&gt;'),
            # Now, escape characters that are magic in Markdown:
            ('*', g_escape_table['*']),
            ('_', g_escape_table['_']),
            ('{', g_escape_table['{']),
            ('}', g_escape_table['}']),
            ('[', g_escape_table['[']),
            (']', g_escape_table[']']),
            ('\\', g_escape_table['\\']),
        ]
        for before, after in replacements:
            text = text.replace(before, after)
        return text

    _strong_re = re.compile(r"(\*\*|__)(?=\S)(.+?[*_]*)(?<=\S)\1", re.S)
    _em_re = re.compile(r"(\*|_)(?=\S)(.+?)(?<=\S)\1", re.S)
    def _do_italics_and_bold(self, text):
        # <strong> must go first:
        text = self._strong_re.sub(r"<strong>\2</strong>", text)
        text = self._em_re.sub(r"<em>\2</em>", text)
        return text
    

    _block_quote_re = re.compile(r'''
        (                           # Wrap whole match in \1
          (
            ^[ \t]*>[ \t]?          # '>' at the start of a line
              .+\n                  # rest of the first line
            (.+\n)*                 # subsequent consecutive lines
            \n*                     # blanks
          )+
        )
        ''', re.M | re.X)
    _bq_one_level_re = re.compile('^[ \t]*>[ \t]?', re.M);

    _html_pre_block_re = re.compile(r'(\s*<pre>.+?</pre>)', re.S)
    def _dedent_two_spaces_sub(self, match):
        return re.sub(r'(?m)^  ', '', match.group(1))

    def _block_quote_sub(self, match):
        bq = match.group(1)
        bq = self._bq_one_level_re.sub('', bq)  # trim one level of quoting
        bq = self._ws_only_line_re.sub('', bq)  # trim whitespace-only lines
        bq = self._run_block_gamut(bq)          # recurse

        bq = re.sub('(?m)^', '  ', bq)
        # These leading spaces screw with <pre> content, so we need to fix that:
        bq = self._html_pre_block_re.sub(self._dedent_two_spaces_sub, bq)

        return "<blockquote>\n%s\n</blockquote>\n\n" % bq

    def _do_block_quotes(self, text):
        return self._block_quote_re.sub(self._block_quote_sub, text)


    def _form_paragraphs(self, text):
        # Strip leading and trailing lines:
        text = text.strip('\n')

        # Wrap <p> tags.
        grafs = re.split(r"\n{2,}", text)
        for i, graf in enumerate(grafs):
            if graf in self.html_blocks:
                # Unhashify HTML blocks
               grafs[i] = self.html_blocks[graf] 
            else:
                # Wrap <p> tags.
                graf = self._run_span_gamut(graf)
                grafs[i] = "<p>" + graf.lstrip(" \t") + "</p>"

        return "\n\n".join(grafs)


    # Ampersand-encoding based entirely on Nat Irons's Amputator MT plugin:
    #   http://bumppo.net/projects/amputator/
    _ampersand_re = re.compile(r'&(?!#?[xX]?(?:[0-9a-fA-F]+|\w+);)')
    _naked_lt_re = re.compile(r'<(?![a-z/?\$!])', re.I)

    def _encode_amps_and_angles(self, text):
        # Smart processing for ampersands and angle brackets that need
        # to be encoded.
        text = self._ampersand_re.sub('&amp;', text)
    
        # Encode naked <'s
        text = self._naked_lt_re.sub('&lt;', text)
        return text

    def _encode_backslash_escapes(self, text):
        for ch, escape in g_escape_table.items():
            text = text.replace("\\"+ch, escape)
        return text

    _auto_link_re = re.compile(r'<((https?|ftp):[^\'">\s]+)>', re.I)
    def _auto_link_sub(self, match):
        g1 = match.group(1)
        return '<a href="%s">%s</a>' % (g1, g1)

    _auto_email_link_re = re.compile(r"""
          <
           (?:mailto:)?
          (
              [-.\w]+
              \@
              [-a-z0-9]+(\.[-a-z0-9]+)*\.[a-z]+
          )
          >
        """, re.I | re.X)
    def _auto_email_link_sub(self, match):
        return self._encode_email_address(
            self._unescape_special_chars(match.group(1)))

    def _do_auto_links(self, text):
        text = self._auto_link_re.sub(self._auto_link_sub, text)
        text = self._auto_email_link_re.sub(self._auto_email_link_sub, text)
        return text
    
    def _encode_email_address(self, addr):
        #  Input: an email address, e.g. "foo@example.com"
        #
        #  Output: the email address as a mailto link, with each character
        #      of the address encoded as either a decimal or hex entity, in
        #      the hopes of foiling most address harvesting spam bots. E.g.:
        #
        #    <a href="&#x6D;&#97;&#105;&#108;&#x74;&#111;:&#102;&#111;&#111;&#64;&#101;
        #       x&#x61;&#109;&#x70;&#108;&#x65;&#x2E;&#99;&#111;&#109;">&#102;&#111;&#111;
        #       &#64;&#101;x&#x61;&#109;&#x70;&#108;&#x65;&#x2E;&#99;&#111;&#109;</a>
        #
        #  Based on a filter by Matthew Wickline, posted to the BBEdit-Talk
        #  mailing list: <http://tinyurl.com/yu7ue>
        chars = [_xml_encode_email_char_at_random(ch)
                 for ch in "mailto:" + addr]
        # Strip the mailto: from the visible part.
        addr = '<a href="%s">%s</a>' \
               % (''.join(chars), ''.join(chars[7:]))
        return addr
    
    
    def _unescape_special_chars(self, text):
        # Swap back in all the special characters we've hidden.
        for ch, hash in g_escape_table.items():
            text = text.replace(hash, ch)
        return text

    def _outdent(self, text):
        # Remove one level of line-leading tabs or spaces
        return self._outdent_re.sub('', text)
    

def _xml_encode_email_char_at_random(ch):
    r = random()
    # Roughly 10% raw, 45% hex, 45% dec.
    # '@' *must* be encoded. I [John Gruber] insist.
    if r > 0.9 and ch != "@":
        return ch
    elif r < 0.45:
        # The [1:] is to drop leading '0': 0x63 -> x63
        return '&#%s;' % hex(ord(ch))[1:]
    else:
        return '&#%s;' % ord(ch)


#---- mainline

def _test():
    import doctest
    doctest.testmod()

def main(argv=sys.argv):
    usage = "usage: %prog [OPTIONS...]"
    version = "%prog "+__version__
    parser = optparse.OptionParser(prog="markdown2", usage=usage,
                                   version=version,
                                   description=__doc__)
    parser.format_description = lambda self, d: d
    parser.add_option("-v", "--verbose", dest="log_level",
                      action="store_const", const=logging.DEBUG,
                      help="more verbose output")
    parser.add_option("--html4tags", action="store_true", default=False, 
                      help="use HTML 4 style for empty element tags")
    parser.add_option("--self-test", action="store_true",
                      help="run self-tests")
    parser.add_option("--compare", action="store_true",
                      help="run against Markdown.pl as well (for testing)")
    parser.set_defaults(log_level=logging.INFO, compare=False)
    opts, paths = parser.parse_args()
    log.setLevel(opts.log_level)

    if opts.self_test:
        return _test()

    from os.path import join, dirname
    markdown_pl = join(dirname(__file__), "test", "Markdown.pl")
    for path in paths:
        if opts.compare:
            print "-- Markdown.pl"
            os.system('perl %s "%s"' % (markdown_pl, path))
            print "-- markdown2.py"
        sys.stdout.write(markdown_path(path, html4tags=opts.html4tags))


if __name__ == "__main__":
    logging.basicConfig()
    sys.exit( main(sys.argv) )

