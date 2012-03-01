# python-markdown2 Makefile

.PHONY: all
all:

.PHONY: test
test:
	cd test && python testall.py

.PHONY: pygments
pygments:
	[[ ! -d deps/pygments ]] && (mkdir -p deps && hg clone http://dev.pocoo.org/hg/pygments-main deps/pygments)
	(cd deps/pygments && hg pull && hg update)

clean:
	rm -rf build dist MANIFEST

.PHONY: cutarelease
cutarelease:
	./tools/cutarelease.py -f lib/markdown2.py
