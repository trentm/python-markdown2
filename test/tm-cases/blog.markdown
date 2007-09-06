Yesterday we (ActiveState) announced Open Komodo, an open-source project seeded with much of the core of Komodo Edit and Komodo IDE with the goals of produce a platform/framework for and (codename Komodo Snapdragon) an IDE for client-side open web development. 

That's a mouthful. <a href="http://blogs.activestate.com/shanec/2007/09/holy-komodo.html">Shane</a> and <a href="http://ascher.ca/blog/2007/09/05/open-komodo-thoughts/">David</a> have done a good job giving some wider perspective on what the Open Komodo project could mean (if all goes well). David went so far as to invent new language to make his points.

Some quick thoughts from a coder's perspective:

- The source will be available in a Mercurial repository in (quoting Shane paraphrasing Mike Shaver) "Two F**king Months!". Early November -- or early if we can.

- Komodo is a Mozilla-based application with the added heavy use of PyXPCOM for much of the core logic. That means the app comes together like this: 

  - Get a slightly tweaked mozilla build (C++, JavaScript, XUL).
  - Get a slightly tweaks Python build (C).
  - Add a bunch of core logic (Python). For example, the guts of Komodo's Find/Replace system is written in Python -- using Python's unicode-aware regular expression engine.
  - Add Komodo chrome (XUL, JavaScript, CSS, DTDs).

  What this means is that work on and add significant functionality to Komodo, all you tend to need to know is XUL, JavaScript and Python. From early on in Komodo's development we've felt that this is one of Komodo's aces in the hole: developing in the dynamic languages is *so much faster*. I remember David Ascher making the comment way back that if Subversion had been written in Python, it would have been ready years sooner. And now two of the primary DVCS, Mercurial and Bazaar, are written in Python.

- Komodo uses the same extension mechanisms as Firefox. It is easy to build a .xpi to add functionality to Komodo. We really hope that a community of Komodo extension authors will develop.

- Komodo builds and runs on Windows, Linux and Mac OS X. Given some work there is little reason the Open Komodo code base couldn't be made to run well on Solaris, BSD, etc.




