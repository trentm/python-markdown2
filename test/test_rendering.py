import conftest
import html
import markdown2


@conftest.parametrize("source, expected, options, marks", "tm-cases")
def test_tm_cases(source, expected, options, marks):
    def filterfn(txt):
        return html.unescape(txt) if "htmlentities" in marks else txt

    found = filterfn(markdown2.markdown(source.read_text(), **(options or {})))
    assert found == filterfn(expected.read_text())


@conftest.parametrize("source, expected, options", "markdowntest-cases")
def test_markdowntest_cases(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()


@conftest.parametrize("source, expected, options, marks", "php-markdown-cases")
def test_php_markdown_cases(source, expected, options, marks):
    def filterfn(txt):
        return html.unescape(txt) if "htmlentities" in marks else txt

    found = filterfn(markdown2.markdown(source.read_text(), **(options or {})))
    assert found == filterfn(expected.read_text())


@conftest.parametrize("source, expected, options", "php-markdown-extra-cases")
def test_php_markdown_extra_cases(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()
