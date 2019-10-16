import json

import urllib.parse

import tornado.web
import tornado.testing

from pinnwand import http
from pinnwand import database
from pinnwand import utility
from pinnwand import settings


class WebsiteTestCase(tornado.testing.AsyncHTTPTestCase):
    def get_app(self) -> tornado.web.Application:
        return http.make_application()


class APITestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        database.Base.metadata.create_all(database._engine)

    def get_app(self) -> tornado.web.Application:
        return http.make_application()

    def test_api_new(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "code": "foo", "expiry": "1day"}
            ),
        )

        assert response.code == 200

        data = json.loads(response.body)

        assert "paste_id" in data
        assert "removal_id" in data

    def test_api_new_no_lexer(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode({"code": "foo", "expiry": "1day"}),
        )

        assert response.code == 400

    def test_api_new_invalid_lexer(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {
                    "lexer": "123asdf123asdf124awsdf",
                    "code": "foo",
                    "expiry": "1day",
                }
            ),
        )

        assert response.code == 400

    def test_api_new_no_code(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode({"lexer": "python", "expiry": "1day"}),
        )

        assert response.code == 400

    def test_api_new_no_expiry(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode({"code": "foo", "lexer": "python"}),
        )

        assert response.code == 400

    def test_api_new_small_file(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"code": "a" * (63 * 1024), "lexer": "python", "expiry": "1day"}
            ),
        )

        assert response.code == 200

    def test_api_new_large_file(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {
                    "code": "a" * ((settings.PASTE_SIZE + 1) * 1024),
                    "lexer": "python",
                    "expiry": "1day",
                }
            ),
        )

        assert response.code == 400

    def test_api_new_wrong_method(self) -> None:
        response = self.fetch("/json/new")
        assert response.code == 405

    def test_api_return_filename(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {
                    "lexer": "python",
                    "code": "foo",
                    "expiry": "1day",
                    "filename": "example.py",
                }
            ),
        )

        assert response.code == 200
        data = json.loads(response.body)

        response = self.fetch(f"/json/show/{data['paste_id']}")
        data = json.loads(response.body)

        assert data["filename"] == "example.py"

    def test_api_show(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "code": "foo", "expiry": "1day"}
            ),
        )

        assert response.code == 200

        data = json.loads(response.body)

        assert "paste_id" in data
        assert "removal_id" in data

        response = self.fetch(f"/json/show/{data['paste_id']}")

        assert response.code == 200

        data = json.loads(response.body)

        assert data["raw"] == "foo"

    def test_api_show_nonexistent(self) -> None:
        response = self.fetch("/json/show/1234")
        assert response.code == 404

    def test_api_remove(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "code": "foo", "expiry": "1day"}
            ),
        )

        assert response.code == 200

        data = json.loads(response.body)

        assert "paste_id" in data
        assert "removal_id" in data

        removal_id = data["removal_id"]

        response = self.fetch(f"/json/show/{data['paste_id']}")

        assert response.code == 200

        data = json.loads(response.body)

        assert data["raw"] == "foo"

        response = self.fetch(
            f"/json/remove",
            method="POST",
            body=urllib.parse.urlencode({"removal_id": removal_id}),
        )

        assert response.code == 200

        response = self.fetch(f"/json/show/{data['paste_id']}")

        assert response.code == 404

    def test_api_get_lexers(self) -> None:
        response = self.fetch("/json/lexers", method="GET")

        assert response.code == 200
        assert json.loads(response.body) == utility.list_languages()

    def test_api_get_expiries(self) -> None:
        response = self.fetch("/json/expiries", method="GET")

        assert response.code == 200
        assert json.loads(response.body).keys() == utility.expiries.keys()
