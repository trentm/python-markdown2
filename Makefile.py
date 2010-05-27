
"""Makefile for the python-markdown2 project.

${common_task_list}

See `mk -h' for options.
"""

import sys
import os
from os.path import join, dirname, normpath, abspath, exists, basename
import re
import webbrowser
from pprint import pprint

from mklib.common import MkError
from mklib import Task
from mklib.sh import run_in_dir



class bugs(Task):
    """Open bug database page."""
    def make(self):
        webbrowser.open("http://code.google.com/p/python-markdown2/issues/list")

class site(Task):
    """Open the Google Code project page."""
    def make(self):
        webbrowser.open("http://code.google.com/p/python-markdown2/")

class sdist(Task):
    """python setup.py sdist"""
    def make(self):
        run_in_dir("%spython setup.py sdist -f --formats zip"
                % _setup_command_prefix(),
            self.dir, self.log.debug)

class pypi_upload(Task):
    """Update release to pypi."""
    def make(self):
        tasks = (sys.platform == "win32"
                 and "bdist_wininst upload"
                 or "sdist --formats zip upload")
        run_in_dir("%spython setup.py %s" % (_setup_command_prefix(), tasks),
            self.dir, self.log.debug)

        sys.path.insert(0, join(self.dir, "lib"))
        url = "http://pypi.python.org/pypi/markdown2/"
        import webbrowser
        webbrowser.open_new(url)

class googlecode_upload(Task):
    """Upload sdist to Google Code project site."""
    deps = ["sdist"]
    def make(self):
        helper_in_cwd = exists(join(self.dir, "googlecode_upload.py"))
        if helper_in_cwd:
            sys.path.insert(0, self.dir)
        try:
            import googlecode_upload
        except ImportError:
            raise MkError("couldn't import `googlecode_upload` (get it from http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py)")
        if helper_in_cwd:
            del sys.path[0]

        sys.path.insert(0, join(self.dir, "lib"))
        import markdown2
        sdist_path = join(self.dir, "dist",
            "markdown2-%s.zip" % markdown2.__version__)
        status, reason, url = googlecode_upload.upload_find_auth(
            sdist_path,
            "python-markdown2", # project_name
            "markdown2 %s source package" % markdown2.__version__, # summary
            ["Featured", "Type-Archive"]) # labels
        if not url:
            raise MkError("couldn't upload sdist to Google Code: %s (%s)"
                          % (reason, status))
        self.log.info("uploaded sdist to `%s'", url)

        project_url = "http://code.google.com/p/python-markdown2/"
        import webbrowser
        webbrowser.open_new(project_url)



class test(Task):
    """Run all tests (except known failures)."""
    def make(self):
        for ver, python in self._gen_pythons():
            if ver < (2,3):
                # Don't support Python < 2.3.
                continue
            elif ver >= (3, 0):
                # Don't yet support Python 3.
                continue
            ver_str = "%s.%s" % ver
            print "-- test with Python %s (%s)" % (ver_str, python)
            assert ' ' not in python
            run_in_dir("%s test.py -- -knownfailure" % python,
                       join(self.dir, "test"))

    def _python_ver_from_python(self, python):
        assert ' ' not in python
        o = os.popen('''%s -c "import sys; print(sys.version)"''' % python)
        ver_str = o.read().strip()
        ver_bits = re.split("\.|[^\d]", ver_str, 2)[:2]
        ver = tuple(map(int, ver_bits))
        return ver
    
    def _gen_python_names(self):
        yield "python"
        for ver in [(2,4), (2,5), (2,6), (2,7), (3,0), (3,1)]:
            yield "python%d.%d" % ver
            if sys.platform == "win32":
                yield "python%d%d" % ver

    def _gen_pythons(self):
        sys.path.insert(0, join(self.dir, "externals", "which"))
        import which  # get it from http://trentm.com/projects/which
        python_from_ver = {}
        for name in self._gen_python_names():
            for python in which.whichall(name):
                ver = self._python_ver_from_python(python)
                if ver not in python_from_ver:
                    python_from_ver[ver] = python
        for ver, python in sorted(python_from_ver.items()):
            yield ver, python
        

class todo(Task):
    """Print out todo's and xxx's in the docs area."""
    def make(self):
        for path in _paths_from_path_patterns(['.'],
                excludes=[".svn", "*.pyc", "TO""DO.txt", "Makefile.py",
                          "*.png", "*.gif", "*.pprint", "*.prof",
                          "tmp-*"]):
            self._dump_pattern_in_path("TO\DO\\|XX\X", path)

        path = join(self.dir, "TO""DO.txt")
        todos = re.compile("^- ", re.M).findall(open(path, 'r').read())
        print "(plus %d TODOs from TO""DO.txt)" % len(todos)

    def _dump_pattern_in_path(self, pattern, path):
        os.system("grep -nH '%s' '%s'" % (pattern, path))

class pygments(Task):
    """Get a copy of pygments in externals/pygments.

    This will be used by the test suite.
    """
    def make(self):
        pygments_dir = join(self.dir, "externals", "pygments")
        if exists(pygments_dir):
            run_in_dir("hg pull", pygments_dir, self.log.info)
            run_in_dir("hg update", pygments_dir, self.log.info)
        else:
            if not exists(dirname(pygments_dir)):
                os.makedirs(dirname(pygments_dir))
            run_in_dir("hg clone http://dev.pocoo.org/hg/pygments-main %s"
                        % basename(pygments_dir),
                       dirname(pygments_dir), self.log.info)

class announce_release(Task):
    """Send a release announcement. Don't send this multiple times!."""
    headers = {
        "To": [
            "python-markdown2@googlegroups.com",
            "python-announce@python.org"
        ],
        "From": ["Trent Mick <trentm@gmail.com>"],
        "Subject": "ANN: python-markdown2 %(version)s -- A fast and complete Python implementation of Markdown",
        "Reply-To": "python-markdown2@googlegroups.com",
    }
    if False: # for dev/debugging
        headers["To"] = ["trentm@gmail.com"]
    
    body = r"""
        ### Where?

        - Project Page: <http://code.google.com/p/python-markdown2/>
        - PyPI: <http://pypi.python.org/pypi/markdown2/>

        ### What's new?
        
        %(whatsnew)s
        
        Full changelog: <http://code.google.com/p/python-markdown2/source/browse/trunk/CHANGES.txt>
        
        ### What is 'markdown2'?
        
        `markdown2.py` is a fast and complete Python implementation of
        [Markdown](http://daringfireball.net/projects/markdown/) -- a
        text-to-HTML markup syntax.
        
        ### Module usage
        
            >>> import markdown2
            >>> markdown2.markdown("*boo!*")  # or use `html = markdown_path(PATH)`
            u'<p><em>boo!</em></p>\n'
        
            >>> markdowner = Markdown()
            >>> markdowner.convert("*boo!*")
            u'<p><em>boo!</em></p>\n'
            >>> markdowner.convert("**boom!**")
            u'<p><strong>boom!</strong></p>\n'

        ### Command line usage
        
            $ cat hi.markdown
            # Hello World!
            $ markdown2 hi.markdown
            <h1>Hello World!</h1>

        This implementation of Markdown implements the full "core" syntax plus a
        number of extras (e.g., code syntax coloring, footnotes) as described on
        <http://code.google.com/p/python-markdown2/wiki/Extras>.

        Cheers,
        Trent

        --
        Trent Mick
        trentm@gmail.com
        http://trentm.com/blog/
    """
    
    def _parse_changes_txt(self):
        changes_txt = open(join(self.dir, "CHANGES.txt")).read()
        sections = re.split(r'\n(?=##)', changes_txt)
        for section in sections[1:]:
            first, tail = section.split('\n', 1)
            if "not yet released" in first:
                continue
            break

        whatsnew_text = tail.strip()
        version = first.strip().split()[-1]
        if version.startswith("v"):
            version = version[1:]

        return version, whatsnew_text
    
    def make(self):
        import getpass
        if getpass.getuser() != "trentm":
            raise RuntimeError("You're not `trentm`. That's not "
                "expected here.")

        version, whatsnew = self._parse_changes_txt()
        data = {
            "whatsnew": whatsnew,
            "version": version,
        }

        headers = {}
        for name, v in self.headers.items():
            if isinstance(v, basestring):
                value = v % data
            else:
                value = v
            headers[name] = value
        body = _dedent(self.body, skip_first_line=True) % data
        
        # Ensure all the footer lines end with two spaces: markdown syntax
        # for <br/>.
        lines = body.splitlines(False)
        idx = lines.index("Cheers,") - 1
        for i in range(idx, len(lines)):
            lines[i] += '  '
        body = '\n'.join(lines)

        print "=" * 70, "body"
        print body
        print "=" * 70
        answer = _query_yes_no(
            "Send release announcement email for v%s to %s?" % (
                version, ", ".join(self.headers["To"])),
            default="no")
        if answer != "yes":
            return

        sys.path.insert(0, join(self.dir, "lib"))
        import markdown2
        body_html = markdown2.markdown(body)
        
        email_it_via_gmail(headers, text=body, html=body_html)
        self.log.info("announcement sent")



#---- internal support stuff

# Recipe http://code.activestate.com/recipes/576824/
def email_it_via_gmail(headers, text=None, html=None, password=None):
    """Send an email -- with text and HTML parts.
    
    @param headers {dict} A mapping with, at least: "To", "Subject" and
        "From", header values. "To", "Cc" and "Bcc" values must be *lists*,
        if given.
    @param text {str} The text email content.
    @param html {str} The HTML email content.
    @param password {str} Is the 'From' gmail user's password. If not given
        it will be prompted for via `getpass.getpass()`.
    
    Derived from http://code.activestate.com/recipes/473810/ and
    http://stackoverflow.com/questions/778202/smtplib-and-gmail-python-script-problems
    """
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    import smtplib
    import getpass
    
    if text is None and html is None:
        raise ValueError("neither `text` nor `html` content was given for "
            "sending the email")
    if not ("To" in headers and "From" in headers and "Subject" in headers):
        raise ValueError("`headers` dict must include at least all of "
            "'To', 'From' and 'Subject' keys")

    # Create the root message and fill in the from, to, and subject headers
    msg_root = MIMEMultipart('related')
    for name, value in headers.items():
        msg_root[name] = isinstance(value, list) and ', '.join(value) or value
    msg_root.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want
    # to display.
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    # Attach HTML and text alternatives.
    if text:
        msg_text = MIMEText(text.encode('utf-8'))
        msg_alternative.attach(msg_text)
    if html:
        msg_text = MIMEText(html.encode('utf-8'), 'html')
        msg_alternative.attach(msg_text)

    to_addrs = headers["To"] \
        + headers.get("Cc", []) \
        + headers.get("Bcc", [])
    from_addr = msg_root["From"]
    
    # Get username and password.
    from_addr_pats = [
        re.compile(".*\((.+@.+)\)"),  # Joe (joe@example.com)
        re.compile(".*<(.+@.+)>"),  # Joe <joe@example.com>
    ]
    for pat in from_addr_pats:
        m = pat.match(from_addr)
        if m:
            username = m.group(1)
            break
    else:
        username = from_addr
    if not password:
        password = getpass.getpass("%s's password: " % username)
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587) # port 465 or 587
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(username, password)
    smtp.sendmail(from_addr, to_addrs, msg_root.as_string())
    smtp.close()


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


# Recipe: query_yes_no (1.0)
def _query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


# Recipe: paths_from_path_patterns (0.3.7)
def _should_include_path(path, includes, excludes):
    """Return True iff the given path should be included."""
    from os.path import basename
    from fnmatch import fnmatch

    base = basename(path)
    if includes:
        for include in includes:
            if fnmatch(base, include):
                try:
                    log.debug("include `%s' (matches `%s')", path, include)
                except (NameError, AttributeError):
                    pass
                break
        else:
            try:
                log.debug("exclude `%s' (matches no includes)", path)
            except (NameError, AttributeError):
                pass
            return False
    for exclude in excludes:
        if fnmatch(base, exclude):
            try:
                log.debug("exclude `%s' (matches `%s')", path, exclude)
            except (NameError, AttributeError):
                pass
            return False
    return True

_NOT_SPECIFIED = ("NOT", "SPECIFIED")
def _paths_from_path_patterns(path_patterns, files=True, dirs="never",
                              recursive=True, includes=[], excludes=[],
                              on_error=_NOT_SPECIFIED):
    """_paths_from_path_patterns([<path-patterns>, ...]) -> file paths

    Generate a list of paths (files and/or dirs) represented by the given path
    patterns.

        "path_patterns" is a list of paths optionally using the '*', '?' and
            '[seq]' glob patterns.
        "files" is boolean (default True) indicating if file paths
            should be yielded
        "dirs" is string indicating under what conditions dirs are
            yielded. It must be one of:
              never             (default) never yield dirs
              always            yield all dirs matching given patterns
              if-not-recursive  only yield dirs for invocations when
                                recursive=False
            See use cases below for more details.
        "recursive" is boolean (default True) indicating if paths should
            be recursively yielded under given dirs.
        "includes" is a list of file patterns to include in recursive
            searches.
        "excludes" is a list of file and dir patterns to exclude.
            (Note: This is slightly different than GNU grep's --exclude
            option which only excludes *files*.  I.e. you cannot exclude
            a ".svn" dir.)
        "on_error" is an error callback called when a given path pattern
            matches nothing:
                on_error(PATH_PATTERN)
            If not specified, the default is look for a "log" global and
            call:
                log.error("`%s': No such file or directory")
            Specify None to do nothing.

    Typically this is useful for a command-line tool that takes a list
    of paths as arguments. (For Unix-heads: the shell on Windows does
    NOT expand glob chars, that is left to the app.)

    Use case #1: like `grep -r`
      {files=True, dirs='never', recursive=(if '-r' in opts)}
        script FILE     # yield FILE, else call on_error(FILE)
        script DIR      # yield nothing
        script PATH*    # yield all files matching PATH*; if none,
                        # call on_error(PATH*) callback
        script -r DIR   # yield files (not dirs) recursively under DIR
        script -r PATH* # yield files matching PATH* and files recursively
                        # under dirs matching PATH*; if none, call
                        # on_error(PATH*) callback

    Use case #2: like `file -r` (if it had a recursive option)
      {files=True, dirs='if-not-recursive', recursive=(if '-r' in opts)}
        script FILE     # yield FILE, else call on_error(FILE)
        script DIR      # yield DIR, else call on_error(DIR)
        script PATH*    # yield all files and dirs matching PATH*; if none,
                        # call on_error(PATH*) callback
        script -r DIR   # yield files (not dirs) recursively under DIR
        script -r PATH* # yield files matching PATH* and files recursively
                        # under dirs matching PATH*; if none, call
                        # on_error(PATH*) callback

    Use case #3: kind of like `find .`
      {files=True, dirs='always', recursive=(if '-r' in opts)}
        script FILE     # yield FILE, else call on_error(FILE)
        script DIR      # yield DIR, else call on_error(DIR)
        script PATH*    # yield all files and dirs matching PATH*; if none,
                        # call on_error(PATH*) callback
        script -r DIR   # yield files and dirs recursively under DIR
                        # (including DIR)
        script -r PATH* # yield files and dirs matching PATH* and recursively
                        # under dirs; if none, call on_error(PATH*)
                        # callback
    """
    from os.path import basename, exists, isdir, join
    from glob import glob

    assert not isinstance(path_patterns, basestring), \
        "'path_patterns' must be a sequence, not a string: %r" % path_patterns
    GLOB_CHARS = '*?['

    for path_pattern in path_patterns:
        # Determine the set of paths matching this path_pattern.
        for glob_char in GLOB_CHARS:
            if glob_char in path_pattern:
                paths = glob(path_pattern)
                break
        else:
            paths = exists(path_pattern) and [path_pattern] or []
        if not paths:
            if on_error is None:
                pass
            elif on_error is _NOT_SPECIFIED:
                try:
                    log.error("`%s': No such file or directory", path_pattern)
                except (NameError, AttributeError):
                    pass
            else:
                on_error(path_pattern)

        for path in paths:
            if isdir(path):
                # 'includes' SHOULD affect whether a dir is yielded.
                if (dirs == "always"
                    or (dirs == "if-not-recursive" and not recursive)
                   ) and _should_include_path(path, includes, excludes):
                    yield path

                # However, if recursive, 'includes' should NOT affect
                # whether a dir is recursed into. Otherwise you could
                # not:
                #   script -r --include="*.py" DIR
                if recursive and _should_include_path(path, [], excludes):
                    for dirpath, dirnames, filenames in os.walk(path):
                        dir_indeces_to_remove = []
                        for i, dirname in enumerate(dirnames):
                            d = join(dirpath, dirname)
                            if dirs == "always" \
                               and _should_include_path(d, includes, excludes):
                                yield d
                            if not _should_include_path(d, [], excludes):
                                dir_indeces_to_remove.append(i)
                        for i in reversed(dir_indeces_to_remove):
                            del dirnames[i]
                        if files:
                            for filename in sorted(filenames):
                                f = join(dirpath, filename)
                                if _should_include_path(f, includes, excludes):
                                    yield f

            elif files and _should_include_path(path, includes, excludes):
                yield path

def _setup_command_prefix():
    prefix = ""
    if sys.platform == "darwin":
        # http://forums.macosxhints.com/archive/index.php/t-43243.html
        # This is an Apple customization to `tar` to avoid creating
        # '._foo' files for extended-attributes for archived files.
        prefix = "COPY_EXTENDED_ATTRIBUTES_DISABLE=1 "
    return prefix


