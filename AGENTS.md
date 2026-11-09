## Testing instructions
- Prefer tests added to test/tm-cases dir as separate files, instead of test/test_markdown2.py unit tests

## Commonly raised issues we're not accepting PRs for:
- Issue #712 XSS via unfiltered javascript, checking img sources for XSS, URI schemes like javascript:, vbscript:, data:. Check PR #766 #714 #744