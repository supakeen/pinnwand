import re
import urllib.parse

import tornado.testing
import tornado.web

from pinnwand import configuration

configuration.ratelimit["read"]["capacity"] = 2**64 - 1
configuration.ratelimit["create"]["capacity"] = 2**64 - 1
configuration.ratelimit["delete"]["capacity"] = 2**64 - 1

from pinnwand import database, http


class CurlTestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        database.Base.metadata.create_all(database._engine)

    def get_app(self) -> tornado.web.Application:
        return http.make_application()

    def test_curl_post_no_lexer(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode({"raw": "a", "expiry": "1day"}),
        )

        assert response.code == 200

    def test_curl_post_no_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode({"lexer": "c", "expiry": "1day"}),
        )

        assert response.code == 400

    def test_curl_post_empty_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "expiry": "1day", "raw": ""}
            ),
        )

        assert response.code == 400

    def test_curl_post_spaced_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "expiry": "1day", "raw": "  "}
            ),
        )

        assert response.code == 400

    def test_curl_post_no_expiry(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode({"lexer": "c", "raw": "a"}),
        )

        assert response.code == 200

    def test_curl_post_nonexistent_lexer(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "no-u", "raw": "a", "expiry": "1day"}
            ),
        )

        assert response.code == 400

    def test_curl_post_nonexistent_expiry(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "no-day"}
            ),
        )

        assert response.code == 400

    def test_curl_post_empty_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "", "expiry": "1day"}
            ),
        )

        assert response.code == 400

    def test_curl_post(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "1day"}
            ),
        )

        assert response.code == 200

    def test_curl_show(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "1day"}
            ),
        )

        paste = (
            re.search(b"Paste URL:   (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        print(paste)
        paste = urllib.parse.urlparse(paste).path

        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 200

    def test_curl_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "1day"}
            ),
        )

        paste = (
            re.search(b"Raw URL:     (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        paste = urllib.parse.urlparse(paste).path

        print(repr(paste))

        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 200

    def test_curl_remove(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        paste = (
            re.search(b"Paste URL:   (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        paste = urllib.parse.urlparse(paste).path

        removal = (
            re.search(b"Removal URL: (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        removal = urllib.parse.urlparse(removal).path

        # Can we visit the paste?
        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 200

        # Can we visit the removal?
        response = self.fetch(
            removal,
            method="GET",
        )
        assert response.code == 200

        # Can we still visit the paste?
        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 404

    def test_curl_raw(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        paste = (
            re.search(b"Paste URL:   (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        paste = urllib.parse.urlparse(paste).path

        raw = (
            re.search(b"Raw URL:     (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        raw = urllib.parse.urlparse(raw).path

        # Can we visit the paste?
        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 200

        response = self.fetch(
            raw,
            method="GET",
        )
        assert response.code == 200
        assert response.body == b"a"

    def test_curl_raw_spaced(self) -> None:
        response = self.fetch(
            "/curl",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "raw": " a ", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        print(response.body)

        paste = (
            re.search(b"Paste URL:   (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        paste = urllib.parse.urlparse(paste).path

        raw = (
            re.search(b"Raw URL:     (.*)", response.body)
            .group(1)  # type: ignore
            .decode("ascii")
        )
        raw = urllib.parse.urlparse(raw).path

        # Can we visit the paste?
        response = self.fetch(
            paste,
            method="GET",
        )

        assert response.code == 200

        # Can we visit the raw?
        response = self.fetch(
            raw,
            method="GET",
        )
        assert response.code == 200
        assert response.body == b" a "
