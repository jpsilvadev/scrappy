import unittest

from crawl import (
    extract_page_data,
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

    def test_get_heading_from_html_basic(self) -> None:
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2_fallback(self) -> None:
        input_body = "<html><body><h2>Test Subtitle</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Subtitle"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_empty(self) -> None:
        input_body = "<html><body><p>No heading here.</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # ==============================
    # get_first_paragraph_from_html
    # ==============================

    def test_get_first_paragraph_from_html_main_priority(self) -> None:
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_not_in_main(self) -> None:
        input_body = "<html><body><p>Outside paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_empty(self) -> None:
        input_body = "<html><body></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # ==============================
    # get_urls_from_html
    # ==============================

    def test_get_urls_from_html_absolute(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/relative/path"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/relative/path"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple(self) -> None:
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

    def test_get_urls_from_html_no_href(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a name="section">No link here</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    # ==============================
    # get_images_from_html
    # ==============================

    def test_get_images_from_html_relative(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple(self) -> None:
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

    def test_get_images_from_html_no_src(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="Missing src"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    # ==============================
    # extract_page_data
    # ==============================

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_and_images(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Fallback Heading</h2>
            <main>
                <p>Main paragraph.</p>
            </main>
            <a href="/one">One</a>
            <a href="https://crawler-test.com/two">Two</a>
            <img src="/one.png" alt="One">
            <img src="https://cdn.crawler-test.com/two.png" alt="Two">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Fallback Heading",
            "first_paragraph": "Main paragraph.",
            "outgoing_links": [
                "https://crawler-test.com/one",
                "https://crawler-test.com/two",
            ],
            "image_urls": [
                "https://crawler-test.com/one.png",
                "https://cdn.crawler-test.com/two.png",
            ],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
