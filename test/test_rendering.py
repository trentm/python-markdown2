import conftest

import markdown2


@conftest.parametrize("source, expected, options", "tm-cases")
def test_render(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()


@conftest.parametrize("source, expected, options", "markdowntest-cases")
def test_render2(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()

@conftest.parametrize("source, expected, options", "php-markdown-cases")
def test_render3(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()


@conftest.parametrize("source, expected, options", "php-markdown-extra-cases")
def test_render4(source, expected, options):
    found = markdown2.markdown(source.read_text(), **(options or {}))
    assert found == expected.read_text()
