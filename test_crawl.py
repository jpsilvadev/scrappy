import unittest

from crawl import (
    get_first_paragraph_from_html,
    get_heading_from_html,
    get_images_from_html,
    get_urls_from_html,
    normalize_url,
)


class TestCrawl(unittest.TestCase):
    # ==============================
    # normalize_url
    # ==============================

    def test_normalize_url(self) -> None:
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path"), "www.boot.dev/blog/path"
        )
        self.assertEqual(
            normalize_url("http://www.boot.dev/blog/path"), "www.boot.dev/blog/path"
        )

    def test_normalize_url_root(self) -> None:
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_trailing_slash(self) -> None:
        input_url = "https://www.boot.dev/blog/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog"
        self.assertEqual(actual, expected)

    # ==============================
    # get_heading_from_html
    # ==============================

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2_fallback(self):
        input_body = "<html><body><h2>Test Subtitle</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Subtitle"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_empty(self):
        input_body = "<html><body><p>No heading here.</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # ==============================
    # get_first_paragraph_from_html
    # ==============================

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_not_in_main(self):
        input_body = "<html><body><p>Outside paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_empty(self):
        input_body = "<html><body></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # ==============================
    # get_urls_from_html
    # ==============================

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/relative/path"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/relative/path"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a href="https://crawler-test.com/one"><span>One</span></a>
            <a href="https://crawler-test.com/two"><span>Two</span></a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one",
            "https://crawler-test.com/two",
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_no_href(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a name="section">No link here</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    # ==============================
    # get_images_from_html
    # ==============================

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <img src="/one.png" alt="One">
            <img src="/two.png" alt="Two">
        </body></html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one.png",
            "https://crawler-test.com/two.png",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_no_src(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="Missing src"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
