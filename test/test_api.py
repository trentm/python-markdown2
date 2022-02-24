# port of api.doctests
import markdown2


def test_version():
    "check if the markdown2 package has version information"
    assert hasattr(markdown2, "__version__")
    assert hasattr(markdown2, "__version_info__")


def test_markdown():
    "various ways to call the api"
    assert markdown2.markdown("*boo*") == "<p><em>boo</em></p>\n"

    m = markdown2.Markdown()
    assert m.convert("*boo*") == "<p><em>boo</em></p>\n"

    m = markdown2.MarkdownWithExtras()
    assert m.convert("*boo*") == "<p><em>boo</em></p>\n"
