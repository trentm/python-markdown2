## Testing instructions
- Prefer tests added to test/tm-cases dir as separate files, instead of test/test_markdown2.py unit tests

## Commonly raised issues we're not accepting PRs for:
- Issue #712 XSS via unfiltered javascript, checking img sources for XSS, URI schemes like javascript:, vbscript:, data:. Check PR #766 #714 #744

## PR instructions
- Follow existing format for CHANGES.md additions
- If the PR fixes an existing issue, link it to that issue so that the issue can be automatically closed on merge
- Do not create a new issue to accompany a PR, it clogs up peoples inboxes

## Code guidelines
- Changes to the behaviour of an extra, or other syntax feature, should go in the Wiki page for that extra/feature, not in the README
