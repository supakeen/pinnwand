import json
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urljoin

import tornado.web

from pinnwand import configuration, database, defensive, error, logger, utility
from pinnwand.db import models

log = logger.get_logger(__name__)


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
            paste = models.Paste(
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
                        models.File(
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


class PasteDetail(Base):
    async def get(self, slug: str) -> None:
        if defensive.ratelimit(self.request, area="read"):
            raise error.RatelimitError()

        with database.session() as session:
            paste = (
                session.query(models.Paste)
                .filter(models.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            if paste.exp_date < datetime.utcnow():
                session.delete(paste)
                session.commit()

                log.warning(
                    "Show.get: paste was expired, is your cronjob running?"
                )

                raise tornado.web.HTTPError(404)

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
