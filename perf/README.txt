# Test the perf of some Markdown implementations.

1. Generate some test cases:

        ./gen_perf_cases.py [limit]

   for example:

        ./gen_perf_cases.py 1000

   This created a bunch of (small) test .txt files in "cases". These are
   derived from a bunch of [Python Cookbook][] data. "limit" is a max number
   of "recipes" in the data set for which to generate cases.
   
   The test files are small and don't necessarily a lot of markup, so this
   may not really be a good *breadth* perf suite -- it *is* real data though.

2. Process the Markdown for each "cases/*.txt" with Markdown.pl, markdown.py
   and markdown2.py:

        ./perf.py


# TODO

- strip out the .text cases that markdown.py blows up on? (encoding problems)
- add some larger perf suites (perhaps those test case files that all
  Markdown implementations pass)
- add markdown.php timing



[Python Cookbook]: http://code.activestate.com/recipes/
