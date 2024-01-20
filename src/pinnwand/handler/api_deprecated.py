import json
from datetime import timedelta
from typing import Any
from urllib.parse import urljoin

import tornado.escape
import tornado.web
from tornado.escape import url_escape

from pinnwand import configuration, crud, database, defensive, error, logger, utility

log = logger.get_logger(__name__)


class Base(tornado.web.RequestHandler):
    """Base page for all 'web' pages to inherit from. This page handles
    default methods for GET and POST but more importantly overwrites
    `write_error` to render error pages.

    It automatically converts ValidationError to a 400 error page but leaves
    other HTTPErrors alone."""

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        if status_code == 404:
            self.render(
                "error.html",
                text="That page does not exist",
                status_code=404,
                pagetitle="error",
            )
        else:
            type_, exc, traceback = kwargs["exc_info"]

            if type_ == error.ValidationError:
                self.set_status(400)
                self.render(
                    "error.html",
                    text=str(exc),
                    status_code=400,
                    pagetitle="error",
                )
            elif type_ == error.RatelimitError:
                self.set_status(429)
                self.render(
                    "error.html",
                    text=str(exc),
                    status_code=429,
                    pagetitle="error",
                )
            elif type_ == error.SpamError:
                self.set_status(451)
                self.render(
                    "error.html",
                    text=str(exc),
                    status_code=429,
                    pagetitle="error",
                )
            else:
                self.render(
                    "error.html",
                    text="unknown error",
                    status_code=500,
                    pagetitle="error",
                )

    async def get(self) -> None:
        raise tornado.web.HTTPError(404)

    async def post(self) -> None:
        raise tornado.web.HTTPError(405)


class Show(Base):
    """Show a paste on the deprecated API."""

    async def get(self, slug: str) -> None:  # type: ignore
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        with database.session() as session:
            paste = crud.get_paste(session, slug)

            self.write(
                {
                    "paste_id": paste.slug,
                    "raw": paste.files[0].raw,
                    "fmt": paste.files[0].fmt,
                    "lexer": paste.files[0].lexer,
                    "expiry": paste.exp_date.isoformat(),
                    "filename": paste.files[0].filename,
                }
            )


class Create(Base):
    """Create a paste on the deprecated API."""

    def check_xsrf_cookie(self) -> None:
        """No XSRF cookies on the API."""
        return

    async def get(self) -> None:
        raise tornado.web.HTTPError(405)

    async def post(self) -> None:
        if defensive.ratelimit(self.request, area="create"):
            raise error.RatelimitError()

        lexer = self.get_body_argument("lexer")
        raw = self.get_body_argument("code", strip=False)
        expiry = self.get_body_argument("expiry")
        filename = self.get_body_argument("filename", None)

        files = [crud.PastedFile(lexer, raw, filename)]

        with database.session() as session:
            paste = crud.create_paste(session, files, expiry, auto_scale=True, source="deprecated-api")

        req_url = self.request.full_url()
        location = paste.paste_slug
        if filename:
            location += "#" + url_escape(filename)

        self.write(
            {
                "paste_id": paste.paste_slug,
                "removal_id": paste.removal_slug,
                "paste_url": urljoin(req_url, f"/{location}"),
                "raw_url": urljoin(req_url, f"/raw/{paste.paste_slug}"),
            }
        )


class Remove(Base):
    """Remove a paste through the deprecated API."""

    def check_xsrf_cookie(self) -> None:
        """No XSRF cookies on the API."""
        return

    async def post(self) -> None:
        if defensive.ratelimit(self.request, area="delete"):
            raise error.RatelimitError()

        with database.session() as session:
            paste = crud.get_paste_by_removal(session, self.get_body_argument("removal_id"))

            session.delete(paste)
            session.commit()

            # this is set this way because tornado tries to protect us
            # by not allowing lists to be returned, looking at this code
            # it really shouldn't be a list but we have to keep it for
            # backwards compatibility
            self.set_header("Content-Type", "application/json")
            self.write(
                json.dumps([{"paste_id": paste.slug, "status": "removed"}])
            )


class Lexer(Base):
    """List lexers through the deprecated API."""

    async def get(self) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        self.write(utility.list_languages())


class Expiry(Base):
    """List expiries through the deprecated API."""

    async def get(self) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        self.write(
            {
                name: str(timedelta(seconds=delta))
                for name, delta in configuration.expiries.items()
            }
        )
