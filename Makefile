all:

.PHONY: test
test:
	cd test && python testall.py

.PHONY: pygments
pygments:
	[[ ! -d externals/pygments ]] && (mkdir -p externals && hg clone http://dev.pocoo.org/hg/pygments-main externals/pygments)
	(cd externals/pygments && hg pull && hg update)

clean:
	rm -rf build dist MANIFEST

.PHONY: cutarelease
cutarelease:
	./tools/cutarelease.py -f lib/markdown2.py
