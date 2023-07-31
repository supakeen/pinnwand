import urllib.parse

import tornado.testing
import tornado.web

from pinnwand import configuration

configuration.ratelimit["read"]["capacity"] = 2**64 - 1
configuration.ratelimit["create"]["capacity"] = 2**64 - 1
configuration.ratelimit["delete"]["capacity"] = 2**64 - 1

from pinnwand import database, http


class WebsiteTestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        database.Base.metadata.create_all(database._engine)

    def get_app(self) -> tornado.web.Application:
        return http.make_application()

    def test_website_index(self) -> None:
        response = self.fetch(
            "/",
            method="GET",
        )

        assert response.code == 200

    def test_website_index_with_lexer(self) -> None:
        response = self.fetch(
            "/+c",
            method="GET",
        )

        assert response.code == 200

    def test_website_index_with_nonexistent_lexer(self) -> None:
        response = self.fetch(
            "/+no-u",
            method="GET",
        )

        assert response.code == 404

    def test_website_removal(self) -> None:
        response = self.fetch(
            "/removal",
            method="GET",
        )

        assert response.code == 200

    def test_website_about(self) -> None:
        response = self.fetch(
            "/about",
            method="GET",
        )

        assert response.code == 200

    def test_website_expiry(self) -> None:
        response = self.fetch(
            "/expiry",
            method="GET",
        )

        assert response.code == 200

    def test_website_nonexistent_page(self) -> None:
        response = self.fetch(
            "/nonexistent",
            method="GET",
        )

        assert response.code == 404

    def test_website_show_nonexistent_paste(self) -> None:
        response = self.fetch(
            "/show/doesntexist",
            method="GET",
        )

        assert response.code == 404

    def test_website_raw_nonexistent_paste(self) -> None:
        response = self.fetch(
            "/raw/doesntexist",
            method="GET",
        )
        assert response.code == 404

        response = self.fetch(
            "/doesntexist/raw",
            method="GET",
        )
        assert response.code == 404

    def test_website_hex_nonexistent_paste(self) -> None:
        response = self.fetch(
            "/hex/doesntexist",
            method="GET",
        )
        assert response.code == 404

        response = self.fetch(
            "/doesntexist/hex",
            method="GET",
        )
        assert response.code == 404

    def test_website_create_post_nothing(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            body="",
        )

        assert response.code == 403

    def test_website_create_post_only_xsrf(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode({"_xsrf": "dummy"}, True),
        )

        assert response.code == 400

    def test_website_create_post_nonexistent_expiry(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "no-day",
                    "filename": ["a"],
                    "raw": ["a"],
                    "lexer": ["python"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_only_raws(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {"_xsrf": "dummy", "expiry": "1day", "raw": ["a"]}, True
            ),
        )

        assert response.code == 400

    def test_website_create_post_only_lexers(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {"_xsrf": "dummy", "expiry": "1day", "lexer": ["python"]},
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_only_filenames(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {"_xsrf": "dummy", "expiry": "1day", "filename": ["foo"]},
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_empty_raws(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "lexer": ["text"],
                    "raw": [],
                    "filename": ["foo"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_empty_lexers(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "lexer": [],
                    "raw": ["a"],
                    "filename": ["foo"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_empty_filenames(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "lexer": ["text"],
                    "raw": ["a"],
                    "filename": [],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_mismatched(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "expiry": "1day",
                    "_xsrf": "dummy",
                    "filename": ["a"],
                    "raw": ["a", "b"],
                    "lexer": ["python"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_single(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "filename": ["a"],
                    "raw": ["a"],
                    "lexer": ["python"],
                },
                True,
            ),
        )

        assert response.code == 200

    def test_website_create_post_multiple(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "filename": ["a", "b"],
                    "raw": ["a", "b"],
                    "lexer": ["python", "text"],
                },
                True,
            ),
        )

        assert response.code == 200

    def test_website_create_post_many(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "filename": ["a", "b"] * 64,
                    "raw": ["a", "b"] * 64,
                    "lexer": ["python", "text"] * 64,
                },
                True,
            ),
        )

        assert response.code == 200

    def test_website_create_post_too_large(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "filename": ["a"],
                    "raw": ["a" * (configuration.paste_size + 1)],
                    "lexer": ["python"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_many_too_large(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "filename": ["a"] * 4,
                    "raw": ["a" * (configuration.paste_size // 2)] * 4,
                    "lexer": ["text"] * 4,
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_raw_only_space(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "lexer": ["text", "text"],
                    "raw": ["  ", "foo"],
                    "filename": ["foo", "bar"],
                },
                True,
            ),
        )

        assert response.code == 400

    def test_website_create_post_nonexistent_lexer(self) -> None:
        response = self.fetch(
            "/create",
            method="POST",
            headers={"Cookie": "_xsrf=dummy"},
            body=urllib.parse.urlencode(
                {
                    "_xsrf": "dummy",
                    "expiry": "1day",
                    "lexer": ["nonexistent"],
                    "raw": ["foo"],
                    "filename": ["foo"],
                },
                True,
            ),
        )

        assert response.code == 400


class DeprecatedWebsiteTestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        database.Base.metadata.create_all(database._engine)

    def get_app(self) -> tornado.web.Application:
        return http.make_application()

    def test_website_index_post_no_lexer(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode({"code": "a", "expiry": "1day"}),
        )

        assert response.code == 400

    def test_website_index_post_no_code(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode({"lexer": "c", "expiry": "1day"}),
        )

        assert response.code == 400

    def test_website_index_post_no_expiry(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode({"lexer": "c", "code": "a"}),
        )

        assert response.code == 400

    def test_website_index_post_nonexistent_lexer(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "no-u", "code": "a", "expiry": "1day"}
            ),
        )

        assert response.code == 400

    def test_website_index_post_nonexistent_expiry(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "no-day"}
            ),
        )

        assert response.code == 400

    def test_website_index_post_empty_code(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "", "expiry": "1day"}
            ),
        )

        assert response.code == 200

    def test_website_index_post(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
        )

        assert response.code == 200

    def test_website_show(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
        )

        paste = response.effective_url.split("/")[-1]

        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 200

    def test_website_raw(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
        )

        paste = response.effective_url.split("/")[-1]

        response = self.fetch(
            f"/raw/{paste}",
            method="GET",
        )
        assert response.code == 200

        response = self.fetch(
            f"/{paste}/raw",
            method="GET",
        )
        assert response.code == 200

    def test_website_hex(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
        )

        paste = response.effective_url.split("/")[-1]

        response = self.fetch(
            f"/hex/{paste}",
            method="GET",
        )
        assert response.code == 200

        response = self.fetch(
            f"/{paste}/hex",
            method="GET",
        )
        assert response.code == 200

    def test_website_remove(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        # Ensure that a cookie was set for the correct path
        assert (
            f"Path={response.headers['Location']}"
            in response.headers["Set-Cookie"]
        )

        # Get the removal ID
        # XXX let's do this with a regex, shall we?
        removal = (
            response.headers["Set-Cookie"].split(";")[0].split("=")[1].strip()
        )
        paste = response.headers["Location"].split("/")[-1]

        # Can we visit the paste?
        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 200

        # Can we visit the removal?
        response = self.fetch(
            f"/remove/{removal}",
            method="GET",
        )
        assert response.code == 200

        # Can we still visit the paste?
        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 404

        # How about raw?
        response = self.fetch(
            f"/raw/{paste}",
            method="GET",
        )

        assert response.code == 404

    def test_website_remove_nonexistent_paste(self) -> None:
        # Can we visit the removal?
        response = self.fetch(
            f"/remove/ABCD",
            method="GET",
        )
        assert response.code == 404

    def test_website_repaste_nonexistent_paste(self) -> None:
        # Can we visit the repaste?
        response = self.fetch(
            f"/repaste/ABCD",
            method="GET",
        )
        assert response.code == 404

    def test_website_repaste(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        paste = response.headers["Location"].split("/")[-1]

        # Can we visit the paste?
        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 200

        # Can we visit the repaste?
        response = self.fetch(
            f"/repaste/{paste}",
            method="GET",
        )
        assert response.code == 200

    def test_website_hex_nonexistent_paste(self) -> None:
        response = self.fetch(
            f"/hex/ABCD",
            method="GET",
        )
        assert response.code == 404

    def test_website_hex(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        paste = response.headers["Location"].split("/")[-1]

        # Can we visit the paste?
        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 200

        response = self.fetch(
            f"/hex/{paste}",
            method="GET",
        )
        assert response.code == 200

    def test_website_download_nonexistent_paste(self) -> None:
        response = self.fetch(
            f"/download/ABCD",
            method="GET",
        )
        assert response.code == 404

    def test_website_download(self) -> None:
        response = self.fetch(
            "/",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "c", "code": "a", "expiry": "1day"}
            ),
            follow_redirects=False,
        )

        paste = response.headers["Location"].split("/")[-1]

        # Can we visit the paste?
        response = self.fetch(
            f"/show/{paste}",
            method="GET",
        )

        assert response.code == 200

        response = self.fetch(
            f"/download/{paste}",
            method="GET",
        )
        assert response.code == 200

    def test_website_logo(self) -> None:
        response = self.fetch(
            "/static/logo.png",
            method="GET",
        )

        assert response.code == 200
