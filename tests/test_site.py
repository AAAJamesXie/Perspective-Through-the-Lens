"""End-to-end checks for the static project site."""

from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest
from urllib.parse import urljoin
from urllib.error import HTTPError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and "href" in values:
            self.links.append(values["href"])
        if tag == "img" and "src" in values:
            self.images.append(values["src"])


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(
            *args, directory=str(ROOT), **kwargs
        )
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_assignment_navigation_and_photos_load(self):
        with urlopen(self.base) as response:
            home = response.read().decode("utf-8")
        home_links = PageLinks()
        home_links.feed(home)
        self.assertIn("./1/index.html", home_links.links)

        assignment_url = urljoin(self.base, "./1/index.html")
        try:
            with urlopen(assignment_url) as response:
                self.assertEqual(response.status, 200)
                assignment = response.read().decode("utf-8")
        except HTTPError as error:
            error.close()
            self.fail(f"Assignment link returned HTTP {error.code}")

        page_links = PageLinks()
        page_links.feed(assignment)
        self.assertGreaterEqual(len(page_links.images), 2)
        for source in page_links.images:
            with self.subTest(source=source):
                with urlopen(urljoin(assignment_url, source)) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers.get_content_type(), "image/jpeg")
                    self.assertGreater(len(response.read()), 10_000)


if __name__ == "__main__":
    unittest.main()
