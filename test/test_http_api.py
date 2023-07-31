import json
import urllib.parse

import tornado.testing
import tornado.web

from pinnwand import configuration

configuration.ratelimit["read"]["capacity"] = 2**64 - 1
configuration.ratelimit["create"]["capacity"] = 2**64 - 1
configuration.ratelimit["delete"]["capacity"] = 2**64 - 1

from pinnwand import configuration, database, http, utility


class DeprecatedAPITestCase(tornado.testing.AsyncHTTPTestCase):
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

    def test_api_new_empty_code(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "expiry": "1day", "code": ""}
            ),
        )

        assert response.code == 400

    def test_api_new_space_code(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "expiry": "1day", "code": "  "}
            ),
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
                {
                    "code": "a" * (configuration.paste_size // 2),
                    "lexer": "python",
                    "expiry": "1day",
                }
            ),
        )

        print(response.body)
        assert response.code == 200

    def test_api_new_large_file(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {
                    "code": "a" * (configuration.paste_size + 1),
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

    def test_api_show_spaced(self) -> None:
        response = self.fetch(
            "/json/new",
            method="POST",
            body=urllib.parse.urlencode(
                {"lexer": "python", "code": "    foo  ", "expiry": "1day"}
            ),
        )

        assert response.code == 200

        data = json.loads(response.body)

        assert "paste_id" in data
        assert "removal_id" in data

        response = self.fetch(f"/json/show/{data['paste_id']}")

        assert response.code == 200

        data = json.loads(response.body)

        assert data["raw"] == "    foo  "

    def test_api_show_web(self) -> None:
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
        assert "paste_url" in data
        assert "raw_url" in data

        response = self.fetch(data["paste_url"])
        assert response.code == 200

        response = self.fetch(data["raw_url"])
        assert response.code == 200

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
        assert json.loads(response.body).keys() == configuration.expiries.keys()


class APIv1TestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        database.Base.metadata.create_all(database._engine)

    def get_app(self) -> tornado.web.Application:
        return http.make_application()

    def test_api_new(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {"name": "spam", "content": "eggs", "lexer": "c"},
                    ],
                }
            ),
        )

        assert response.code == 200

        data = json.loads(response.body)

        assert "link" in data
        assert "removal" in data

    def test_api_new_invalid_body(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=b"hi",
        )

        assert response.code == 400

    def test_api_new_no_files(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps({"expiry": "1day", "files": []}),
        )

        assert response.code == 400

        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps({"expiry": "1day"}),
        )

        assert response.code == 400

    def test_api_new_no_lexer(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [{"name": "spam", "content": "eggs"}],
                }
            ),
        )

        assert response.code == 400

    def test_api_new_invalid_lexer(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {
                            "name": "spam",
                            "content": "eggs",
                            "lexer": "nonexistent",
                        },
                    ],
                }
            ),
        )

        assert response.code == 400

    def test_api_new_no_content(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {"expiry": "1day", "files": [{"name": "spam", "lexer": "c"}]}
            ),
        )

        assert response.code == 400

    def test_api_new_no_expiry(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {"files": [{"name": "spam", "content": "eggs", "lexer": "c"}]}
            ),
        )

        assert response.code == 400

    def test_api_new_small_file(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {
                            "name": "spam",
                            "content": "a" * (configuration.paste_size // 2),
                            "lexer": "c",
                        },
                    ],
                }
            ),
        )

        assert response.code == 200

    def test_api_new_large_file(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {
                            "name": "spam",
                            "content": "a" * (configuration.paste_size + 1),
                            "lexer": "c",
                        },
                    ],
                }
            ),
        )

        assert response.code == 400

    def test_api_new_many_file(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {
                            "name": "spam",
                            "content": "a",
                            "lexer": "c",
                        },
                    ]
                    * 128,
                }
            ),
        )

        assert response.code == 200

    def test_api_new_many_file_large(self) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {
                            "name": "spam",
                            "content": "a",
                            "lexer": "text" * (configuration.paste_size // 2),
                        },
                    ]
                    * 4,
                }
            ),
        )

        assert response.code == 400

    def test_api_new_wrong_method(self) -> None:
        response = self.fetch("/api/v1/paste")
        assert response.code == 405
