import conftest
import html
import markdown2

def read_text(path, marks):
    from html import unescape
    encoding = "utf-8" if "unicode" in marks else None
    txt = path.read_text(encoding=encoding)
    if "htmlentities" in marks:
        return unescape(txt)
    return txt


def read_and_process(path, options, marks):
    encoding = "utf-8" if "unicode" in marks else None
    txt = markdown2.markdown(path.read_text(encoding=encoding), **(options or {}))
    if "htmlentities" in marks:
        return html.unescape(txt)
    return txt


@conftest.parametrize("source, expected, options, marks", "tm-cases")
def test_tm_cases(source, expected, options, marks):
    found = read_and_process(source, options, marks)
    assert found == read_text(expected, marks)


@conftest.parametrize("source, expected, options", "markdowntest-cases")
def test_markdowntest_cases(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()


@conftest.parametrize("source, expected, options, marks", "php-markdown-cases")
def test_php_markdown_cases(source, expected, options, marks):
    found = read_and_process(source, options, marks)
    assert found == read_text(expected, marks)

@conftest.parametrize("source, expected, options", "php-markdown-extra-cases")
def test_php_markdown_extra_cases(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()
