import logging
import json

from datetime import timedelta
from typing import Any

from urllib.parse import urljoin

import tornado.web

from pinnwand import utility, database, error, configuration, defensive


log = logging.getLogger(__name__)


class Base(tornado.web.RequestHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        _, exc, _ = kwargs["exc_info"]
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

        if expiry not in configuration.expiries:
            log.info("Paste.post: a paste was submitted with an invalid expiry")
            raise tornado.web.HTTPError(400, "invalid expiry")

        auto_scale = data.get("long", None) is None

        files = data.get("files", [])

        if not files:
            raise tornado.web.HTTPError(400, "no files provided")

        with database.session() as session, utility.SlugContext(
            auto_scale
        ) as slug_context:
            paste = database.Paste(
                next(slug_context),
                configuration.expiries[expiry],
                "v1-api",
            )

            for file in files:
                lexer = file.get("lexer", "")
                content = file.get("content")
                filename = file.get("name")

                if lexer not in utility.list_languages():
                    raise tornado.web.HTTPError(400, "invalid lexer")

                if not content:
                    raise tornado.web.HTTPError(400, "invalid content (empty)")

                try:
                    paste.files.append(
                        database.File(
                            next(slug_context),
                            content,
                            lexer,
                            filename,
                        )
                    )
                except error.ValidationError:
                    raise tornado.web.HTTPError(
                        400, "invalid content (exceeds size limit)"
                    )

            if sum(len(f.fmt) for f in paste.files) > configuration.paste_size:
                raise tornado.web.HTTPError(
                    400, "invalid content (exceeds size limit)"
                )

            paste.files[0].slug = paste.slug

            session.add(paste)

            try:
                session.commit()
            except Exception:  # XXX be more precise
                log.warning("%r", slug_context._slugs)
                raise

            # Send the client to the paste
            url_request = self.request.full_url()
            url_paste = urljoin(url_request, f"/{paste.slug}")
            url_removal = urljoin(url_request, f"/remove/{paste.removal}")

            self.write({"link": url_paste, "removal": url_removal})
