import json
import logging

from typing import Any
from urllib.parse import urljoin

import tornado.web
from tornado.escape import url_escape

from pinnwand import database, path, utility, error

log = logging.getLogger(__name__)


class Base(tornado.web.RequestHandler):
    def write_error(self, status_code: int, **kwargs: Any) -> None:
        print("write_error")
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


class CreatePaste(Base):
    """The index page shows the new paste page with a list of all available
       lexers from Pygments."""

    async def get(self, lexer: str = "") -> None:
        """Render the new paste form, optionally have a lexer preselected from
           the URL."""

        lexers = utility.list_languages()

        # Our default lexer is just that, text
        if not lexer:
            lexer = "text"

        # Make sure a valid lexer is given
        if lexer not in lexers:
            log.debug("CreatePaste.get: non-existent logger requested")
            raise tornado.web.HTTPError(404)

        await self.render(
            "new.html",
            lexer=lexer,
            lexers=lexers,
            pagetitle="new",
            message=None,
        )

    async def post(self) -> None:
        lexer = self.get_body_argument("lexer")
        raw = self.get_body_argument("code")
        expiry = self.get_body_argument("expiry")

        if lexer not in utility.list_languages():
            log.info("Paste.post: a paste was submitted with an invalid lexer")
            raise tornado.web.HTTPError(400)

        # Guard against empty strings
        if not raw:
            return self.redirect(f"/+{lexer}")

        if expiry not in utility.expiries:
            log.info("Paste.post: a paste was submitted with an invalid expiry")
            raise tornado.web.HTTPError(400)

        paste = database.Paste(raw, lexer, utility.expiries[expiry], "web")

        with database.session() as session:
            session.add(paste)
            session.commit()

            # The removal cookie is set for the specific path of the paste it is
            # related to
            self.set_cookie(
                "removal", str(paste.removal_id), path=f"/show/{paste.paste_id}"
            )

            # Send the client to the paste
            self.redirect(f"/show/{paste.paste_id}")

    def check_xsrf_cookie(self) -> None:
        """The CSRF token check is disabled. While it would be better if it
           was on the impact is both small (someone could make a paste in
           a users name which could allow pinnwand to be used as a vector for
           exfiltration from other XSS) and some command line utilities
           POST directly to this endpoint without using the JSON endpoint."""
        return


class ShowPaste(Base):
    async def get(self, paste_id: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.paste_id == paste_id)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            can_delete = self.get_cookie("removal") == str(paste.removal_id)

            self.render(
                "show.html",
                paste=paste,
                pagetitle=paste.filename or "show",
                can_delete=can_delete,
                linenos=False,
            )


class RawPaste(Base):
    async def get(self, paste_id: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.paste_id == paste_id)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            self.set_header("Content-Type", "text/plain; charset=utf-8")
            self.write(paste.raw)


class RemovePaste(Base):
    """Remove a paste."""

    async def get(self, removal_id: str) -> None:  # type: ignore
        """Look up if the user visiting this page has the removal id for a
           certain paste. If they do they're authorized to remove the paste."""

        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.removal_id == removal_id)
                .first()
            )

            if not paste:
                log.info("RemovePaste.get: someone visited with invalid id")
                raise tornado.web.HTTPError(404)

            session.delete(paste)
            session.commit()

        self.redirect("/")


class APIShow(Base):
    async def get(self, paste_id: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.paste_id == paste_id)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            self.write(
                {
                    "paste_id": paste.paste_id,
                    "raw": paste.raw,
                    "fmt": paste.fmt,
                    "lexer": paste.lexer,
                    "expiry": paste.exp_date.isoformat(),
                    "filename": paste.filename,
                }
            )


class APINew(Base):
    async def get(self) -> None:
        raise tornado.web.HTTPError(405)

    async def post(self) -> None:
        lexer = self.get_body_argument("lexer")
        raw = self.get_body_argument("code")
        expiry = self.get_body_argument("expiry")
        filename = self.get_body_argument("filename", None)

        if not raw:
            log.info("APINew.post: a paste was submitted without content")
            raise tornado.web.HTTPError(400)

        if lexer not in utility.list_languages():
            log.info("APINew.post: a paste was submitted with an invalid lexer")
            raise tornado.web.HTTPError(400)

        if expiry not in utility.expiries:
            log.info(
                "APINew.post: a paste was submitted with an invalid expiry"
            )
            raise tornado.web.HTTPError(400)

        paste = database.Paste(
            raw, lexer, utility.expiries[expiry], "api", filename
        )

        with database.session() as session:
            session.add(paste)
            session.commit()

            req_url = self.request.full_url()
            location = paste.paste_id
            if filename:
                location += "#" + url_escape(filename)
            self.write(
                {
                    "paste_id": paste.paste_id,
                    "removal_id": paste.removal_id,
                    "paste_url": urljoin(req_url, f"/show/{location}"),
                    "raw_url": urljoin(req_url, f"/raw/{location}"),
                }
            )


class APIRemove(Base):
    async def post(self) -> None:
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(
                    database.Paste.removal_id
                    == self.get_body_argument("removal_id")
                )
                .first()
            )

            if not paste:
                self.set_status(400)
                return

            session.delete(paste)
            session.commit()

            # this is set this way because tornado tries to protect us
            # by not allowing lists to be returned, looking at this code
            # it really shouldn't be a list but we have to keep it for
            # backwards compatibility
            self.set_header("Content-Type", "application/json")
            self.write(
                json.dumps([{"paste_id": paste.paste_id, "status": "removed"}])
            )


class APILexers(Base):
    async def get(self) -> None:
        self.write(utility.list_languages())


class APIExpiries(Base):
    async def get(self) -> None:
        self.write(
            {name: str(delta) for name, delta in utility.expiries.items()}
        )


class RemovalPage(Base):
    """Serve the removal page."""

    async def get(self) -> None:
        self.render("removal.html", pagetitle="removal")


class AboutPage(Base):
    """Serve the about page."""

    async def get(self) -> None:
        self.render("about.html", pagetitle="about")


class ExpiryPage(Base):
    """Serve the expiry page."""

    async def get(self) -> None:
        self.render("expiry.html", pagetitle="expiry")


def make_application() -> tornado.web.Application:
    return tornado.web.Application(
        [
            (r"/", CreatePaste),
            (r"/\+(.*)", CreatePaste),
            (r"/show/(.*)(?:#.+)?", ShowPaste),
            (r"/raw/(.*)(?:#.+)?", RawPaste),
            (r"/remove/(.*)", RemovePaste),
            (r"/about", AboutPage),
            (r"/removal", RemovalPage),
            (r"/expiry", ExpiryPage),
            (r"/json/new", APINew),
            (r"/json/remove", APIRemove),
            (r"/json/show/(.*)(?:#.+)?", APIShow),
            (r"/json/lexers", APILexers),
            (r"/json/expiries", APIExpiries),
            (
                r"/static/(.*)",
                tornado.web.StaticFileHandler,
                {"path": path.static},
            ),
        ],
        template_path=path.template,
        default_handler_class=Base,
    )
