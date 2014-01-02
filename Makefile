# python-markdown2 Makefile
SHELL=/bin/bash

.PHONY: all
all:

.PHONY: test
test:
	cd test && python testall.py

.PHONY: testone
testone:
	cd test && python test.py -- -knownfailure

.PHONY: pygments
pygments:
	[[ -d deps/pygments ]] || ( \
		mkdir -p deps && \
		hg clone https://bitbucket.org/birkenfeld/pygments-main deps/pygments)
	(cd deps/pygments && hg pull && hg update)
	# And for Python 3 usage:
	rm -rf deps/pygments3
	mkdir -p deps/pygments3
	cp -PR deps/pygments/pygments deps/pygments3/pygments
	2to3 -w --no-diffs deps/pygments3/pygments

clean:
	rm -rf build dist MANIFEST


.PHONY: versioncheck
versioncheck:
	[[ `grep '^__version_info__' lib/markdown2.py | cut -d'(' -f2 | cut -d')' -f1 | sed 's/, /./g'` \
	    == `grep '^## ' CHANGES.md | head -1 | awk '{print $$3}'` ]]
	@echo Version check ok.

.PHONY: cutarelease
cutarelease: versioncheck
	./tools/cutarelease.py -f lib/markdown2.py

