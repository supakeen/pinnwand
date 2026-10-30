import json
import copy
import urllib.parse
import unittest.mock
import tornado.testing
import tornado.web

from pinnwand.configuration import Configuration, ConfigurationProvider
from pinnwand import app, utility
from pinnwand.database import manager, utils as database_utils

configuration: Configuration = ConfigurationProvider.get_config()


ratelimit_copy = copy.deepcopy(configuration._ratelimit)
for area in ("read", "create", "delete"):
    ratelimit_copy[area]["capacity"] = 2**64 - 1


@unittest.mock.patch.dict(configuration._ratelimit, ratelimit_copy)
class DeprecatedAPITestCase(tornado.testing.AsyncHTTPTestCase):
    def setUp(self) -> None:
        super().setUp()
        engine = manager.DatabaseManager.get_engine()
        database_utils.create_tables(engine)

    def get_app(self) -> tornado.web.Application:
        return app.make_application()

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
            "/json/remove",
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
        engine = manager.DatabaseManager.get_engine()
        database_utils.create_tables(engine)

    def get_app(self) -> tornado.web.Application:
        return app.make_application()

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

    @unittest.mock.patch(
        "pinnwand.defensive.should_be_ratelimited", return_value=False
    )
    def test_api_new_invalid_json_shapes(self, _ratelimit) -> None:
        valid_file = {"lexer": "text", "content": "hello"}
        bodies = [
            [],
            None,
            {"expiry": [], "files": [valid_file]},
            {"expiry": "1day", "files": {}},
            {"expiry": "1day", "files": [None]},
            {"expiry": "1day", "files": [{"lexer": [], "content": "hello"}]},
            {"expiry": "1day", "files": [{"lexer": "text", "content": 12}]},
            {"expiry": "1day", "files": [{**valid_file, "name": []}]},
        ]
        for body in bodies:
            with self.subTest(body=body):
                response = self.fetch(
                    "/api/v1/paste", method="POST", body=json.dumps(body)
                )
                assert response.code == 400
                assert json.loads(response.body)["code"] == 400

        response = self.fetch("/api/v1/paste", method="POST", body=b"\xff")
        assert response.code == 400

    @unittest.mock.patch(
        "pinnwand.defensive.should_be_ratelimited", return_value=False
    )
    def test_api_new_spam(self, _ratelimit) -> None:
        response = self.fetch(
            "/api/v1/paste",
            method="POST",
            body=json.dumps(
                {
                    "expiry": "1day",
                    "files": [
                        {"lexer": "text", "content": "https://example.com/"}
                    ],
                }
            ),
        )
        assert response.code == 451
        assert json.loads(response.body)["code"] == 451

    @unittest.mock.patch(
        "pinnwand.defensive.should_be_ratelimited", return_value=True
    )
    def test_api_rate_limit_error(self, _ratelimit) -> None:
        response = self.fetch("/api/v1/lexer")
        assert response.code == 429
        assert json.loads(response.body)["code"] == 429

    @unittest.mock.patch(
        "pinnwand.defensive.should_be_ratelimited", return_value=False
    )
    @unittest.mock.patch(
        "pinnwand.utility.list_languages",
        side_effect=RuntimeError("secret detail"),
    )
    def test_api_unexpected_error_is_not_exposed(
        self, _languages, _ratelimit
    ) -> None:
        response = self.fetch("/api/v1/lexer")
        assert response.code == 500
        assert json.loads(response.body)["message"] == "Internal Server Error"

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

    def test_api_detail_many_files(self) -> None:
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

        data = json.loads(response.body)
        name = data["link"].split("/")[-1]

        response = self.fetch(
            f"/api/v1/paste/{name}",
            method="GET",
        )

        assert response.code == 200
        data = json.loads(response.body)

        assert len(data["files"]) == 128
        assert data["files"][0]["name"] == "spam"
        assert data["files"][0]["content"] == "a"
        assert data["files"][0]["lexer"] == "c"
