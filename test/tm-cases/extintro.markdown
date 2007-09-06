(A short while ago Jaroslaw Zabiello asked a question on the
komodo-discuss list that motivated me to finally write up a beginner intro
to using some new tools in Komodo 4.2 beta 7 for creating Komodo
extensions. Here is my slightly edited response.)

Jaroslaw Zabiello wrote:
> is there any chance for syntax colouring for Mako templates
> (http://makotemplates.org)...

This is certainly possible with Komodo's UDL (User-Defined Languages)
system.

You could take a stab at writing a Mako extension for Komodo (in
particular the Mako UDL definition) yourself. Komodo is still in the early
stages of making this kind of thing easy, but 4.2 (including the recent
beta7) improves on this a bit.

Eric wrote up a (long) intro to writing UDL definitions a while back on
his blog:

   <http://blogs.activestate.com/ericp/2007/01/kid_adding_a_ne.html>

Here is how packing up the Mako UDL into a Komodo extension would
basically work -- if you are willing to help us work out the kinks.

Komodo 4.2 beta 7 includes a sort of SDK in its install tree. On Linux and
Windows this is found at "*installdir*/lib/sdk". That SDK includes two
tools:

    koext       a command line tool for working with Komodo extensions
    luddite     a tools for working with UDL

Put the SDK bin dir on your PATH and you should be able to run `koext` and
`luddite` at the command line. Similar to tools like cvs or svn, these are
tools with multiple sub-commands. (If running these doesn't work for you,
then please let us know so we can make the environment setup more smooth.
There is currently a dependency on having a Python 2.5 installation --
which we should be able to remedy if necessary.)


1. Start your extension source dir (with `koext startext'):

    $ koext help startext
    ...prints instructions on using this command...

    $ koext startext mako_language
    ...follow instructions for other extension meta-data...

2. You should now be able to build your extension:

    $ cd mako_language     # cd in to source dir
    $ koext build

This will build an .xpi file that you can install into your Komodo.
However, the extension doesn't yet *do* anything.

3. Generate stubs for defining a new language for Komodo:

    $ cd mako_language
    $ koext help startlang
    ...
    $ koext startlang Mako --ext .mako --is-html-based

This will generate a few files that you'll then need to fill out with
appropriate information for Mako template files. Namely:

    udl/mako-mainlex.udl
        The lexing/syntax-coloring UDL definition for Mako.
    components/koMako_UDL_Language.py
        The PyXPCOM component that defines the language for
        Komodo.

Properly filling these out is a big topic beyond the scope of this email.
Your best references are:

- Eric's blog post for UDL information.
- The UDL reference in the Komodo documentation.
- Example .udl files in the SDK directory (lib/sdk/udl/...)
- Look at other `ko*_UDL_Language.py` files in your Komodo installation.
  Many of the new languages added to Komodo in the 4.x series are based on
  UDL and work in the exact same way as would your Mako language
  component. Look for RHTML, Smarty, HTML, TemplateToolkit, and Mason.
  They should be quite similar.

Note: Komodo also has a "Komodo Extension" project template that you could
use for starting out. However, we are still working on merging the project
template and the "koext" tool in the SDK (probably for Komodo 4.3).

I realize that this isn't quite as smooth a process as it could be yet,
but with the help of the beta-list we hope to get there in subsequent
releases.
