import json
from datetime import timedelta
from typing import Any
from urllib.parse import urljoin

import tornado.web

from pinnwand import configuration, crud, database, defensive, error, logger, utility

log = logger.get_logger(__name__)


class Base(tornado.web.RequestHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        type_, exc, _ = kwargs["exc_info"]

        if type_ is error.ValidationError:
            self.set_status(400)
            self.write({"state": "error", "code": 400, "message": str(exc)})
        
        super().write_error(status_code, **kwargs)
        self.write({"state": "error", "code": status_code, "message": str(exc)})


class Lexer(Base):
    async def get(self) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        self.write(utility.list_languages())


class Expiry(Base):
    async def get(self) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        self.write(
            {
                name: str(timedelta(seconds=delta))
                for name, delta in configuration.expiries.items()
            }
        )


class Paste(Base):
    def check_xsrf_cookie(self) -> None:
        return

    async def get(self) -> None:
        raise tornado.web.HTTPError(405)

    async def post(self) -> None:
        if defensive.ratelimit(self.request, area="create"):
            raise error.RatelimitError()

        try:
            data = tornado.escape.json_decode(self.request.body)
        except json.decoder.JSONDecodeError:
            raise tornado.web.HTTPError(400, "could not parse json body")

        expiry = data.get("expiry")
        if expiry is None:
            raise tornado.web.HTTPError(400, "expiry is required")
        
        auto_scale = data.get("long", None) is None
        files = [
            crud.PastedFile(
                file.get("lexer", ""),
                file.get("content"),
                file.get("name"),
            )
            for file in data.get("files", [])
        ]

        with database.session() as session:
            result = crud.create_paste(session, files, expiry, auto_scale, "v1-api")

        # Send the paste to the client
        url_request = self.request.full_url()
        url_paste = urljoin(url_request, f"/{result.paste_slug}")
        url_removal = urljoin(url_request, f"/remove/{result.removal_slug}")

        self.write({"link": url_paste, "removal": url_removal})


class PasteDetail(Base):
    async def get(self, slug: str) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        with database.session() as session:
            paste = crud.get_paste(session, slug)

            self.write(
                {
                    "files": [
                        {
                            "name": file.filename,
                            "lexer": file.lexer,
                            "content": file.raw,
                        }
                        for file in paste.files
                    ],
                }
            )
