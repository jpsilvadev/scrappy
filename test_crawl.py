import unittest

from crawl import normalize_url


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(
            normalize_url("https://www.boot.dev/blog/path"), "www.boot.dev/blog/path"
        )
        self.assertEqual(
            normalize_url("http://www.boot.dev/blog/path"), "www.boot.dev/blog/path"
        )

    def test_normalize_url_root(self):
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_trailing_slash(self):
        input_url = "https://www.boot.dev/blog/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog"
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
