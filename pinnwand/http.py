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
            "create.html",
            lexer=lexer,
            lexers=lexers,
            pagetitle="new",
            message=None,
            prefill="",
        )

    async def post(self) -> None:
        # This is a historical endpoint to create pastes, pastes are marked as
        # old-web and will get a warning on top of them to remove any access to
        # this route.

        # pinnwand has since evolved with an API which should be used and a
        # multi-file paste.

        # See the 'CreateAction' for the new-style creation of pastes.

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

        paste = database.Paste(utility.expiries[expiry], "deprecated-web")
        file = database.File(raw, lexer)
        file.slug = paste.slug  # XXX fix, this can duplicate!!!
        paste.files.append(file)

        with database.session() as session:
            session.add(paste)
            session.commit()

            # The removal cookie is set for the specific path of the paste it is
            # related to
            self.set_cookie(
                "removal", str(paste.removal), path=f"/{paste.slug}"
            )

            # Send the client to the paste
            self.redirect(f"/{paste.slug}")

    def check_xsrf_cookie(self) -> None:
        """The CSRF token check is disabled. While it would be better if it
           was on the impact is both small (someone could make a paste in
           a users name which could allow pinnwand to be used as a vector for
           exfiltration from other XSS) and some command line utilities
           POST directly to this endpoint without using the JSON endpoint."""
        return


class CreateAction(Base):
    def post(self) -> None:  # type: ignore
        expiry = self.get_body_argument("expiry")

        if expiry not in utility.expiries:
            log.info(
                "CreateAction.post: a paste was submitted with an invalid expiry"
            )
            raise tornado.web.HTTPError(400)

        lexers = self.get_body_arguments("lexer")
        raws = self.get_body_arguments("raw")
        filenames = self.get_body_arguments("filename")

        with database.session() as session:
            paste = database.Paste(utility.expiries[expiry], "web")

            if any(len(L) != len(lexers) for L in [lexers, raws, filenames]):
                print(lexers, raws, filenames)
                log.info("CreateAction.post: mismatching argument lists")
                raise tornado.web.HTTPError(400)

            for (lexer, raw, filename) in zip(lexers, raws, filenames):
                if lexer not in utility.list_languages():
                    log.info("CreateAction.post: a file had an invalid lexer")
                    raise tornado.web.HTTPError(400)

                if not raw:
                    log.info("CreateAction.post: a file had an empty raw")
                    raise tornado.web.HTTPError(400)

                paste.files.append(
                    database.File(raw, lexer, filename if filename else None)
                )

            session.add(paste)
            session.commit()

            # The removal cookie is set for the specific path of the paste it is
            # related to
            self.set_cookie(
                "removal", str(paste.removal), path=f"/{paste.slug}"
            )

            # Send the client to the paste
            self.redirect(f"/{paste.slug}")


class RepastePaste(Base):
    """Repaste is a specific case of the paste page. It only works for pre-
       existing pastes and will prefill the textarea and lexer."""

    async def get(self, slug: str, lexer: str = "") -> None:  # type: ignore
        """Render the new paste form, optionally have a lexer preselected from
           the URL."""

        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

        lexers = utility.list_languages()

        # Our default lexer is just that, text
        if not lexer:
            lexer = "text"

        # Make sure a valid lexer is given
        if lexer not in lexers:
            log.debug("Repaste.get: non-existent lexer requested")
            raise tornado.web.HTTPError(404)

        await self.render(
            "create.html",
            lexer=lexer,
            lexers=lexers,
            pagetitle="repaste",
            message=None,
            prefill=paste.raw,
        )


class ShowPaste(Base):
    async def get(self, slug: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            can_delete = self.get_cookie("removal") == str(paste.removal)

            self.render(
                "show.html",
                paste=paste,
                pagetitle=paste.slug,
                can_delete=can_delete,
                linenos=False,
            )


class RedirectShowPaste(Base):
    async def get(self, slug: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            self.redirect(f"/{paste.slug}")


class RawFile(Base):
    async def get(self, file_id: str) -> None:  # type: ignore
        with database.session() as session:
            file = (
                session.query(database.File)
                .filter(database.File.slug == file_id)
                .first()
            )

            if not file:
                raise tornado.web.HTTPError(404)

            self.set_header("Content-Type", "text/plain; charset=utf-8")
            self.write(file.raw)


class DownloadFile(Base):
    async def get(self, file_id: str) -> None:  # type: ignore
        with database.session() as session:
            file = (
                session.query(database.File)
                .filter(database.File.slug == file_id)
                .first()
            )

            if not file:
                raise tornado.web.HTTPError(404)

            self.set_header("Content-Type", "text/plain; charset=utf-8")
            self.set_header(
                "Content-Disposition", f"attachment; filename={file.slug}"
            )
            self.write(file.raw)


class RemovePaste(Base):
    """Remove a paste."""

    async def get(self, removal: str) -> None:  # type: ignore
        """Look up if the user visiting this page has the removal id for a
           certain paste. If they do they're authorized to remove the paste."""

        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.removal == removal)
                .first()
            )

            if not paste:
                log.info("RemovePaste.get: someone visited with invalid id")
                raise tornado.web.HTTPError(404)

            session.delete(paste)
            session.commit()

        self.redirect("/")


class APIShow(Base):
    async def get(self, slug: str) -> None:  # type: ignore
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

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

        paste = database.Paste(utility.expiries[expiry], "deprecated-api")
        paste.files.append(database.File(raw, lexer, filename))

        with database.session() as session:
            session.add(paste)
            session.commit()

            req_url = self.request.full_url()
            location = paste.slug
            if filename:
                location += "#" + url_escape(filename)
            self.write(
                {
                    "paste_id": paste.slug,
                    "removal_id": paste.removal,
                    "paste_url": urljoin(req_url, f"/{location}"),
                    "raw_url": urljoin(req_url, f"/raw/{location}"),
                }
            )


class APIRemove(Base):
    async def post(self) -> None:
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(
                    database.Paste.removal
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
                json.dumps([{"paste_id": paste.slug, "status": "removed"}])
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


class CurlCreate(Base):
    def check_xsrf_cookie(self) -> None:
        return

    async def post(self) -> None:
        lexer = self.get_body_argument("lexer", "text")
        raw = self.get_body_argument("raw", None)
        expiry = self.get_body_argument("expiry", "1day")

        self.set_header("Content-Type", "text/plain")

        if lexer not in utility.list_languages():
            log.info(
                "CurlCreate.post: a paste was submitted with an invalid lexer"
            )
            self.set_status(400)
            self.write("Invalid `lexer` supplied.\n")
            return

        # Guard against empty strings
        if not raw:
            log.info("CurlCreate.post: a paste was submitted without raw")
            self.set_status(400)
            self.write("Invalid `raw` supplied.\n")
            return

        if expiry not in utility.expiries:
            log.info("CurlCreate.post: a paste was submitted without raw")
            self.set_status(400)
            self.write("Invalid `expiry` supplied.\n")
            return

        paste = database.Paste(utility.expiries[expiry], "curl")
        file = database.File(raw, lexer)
        paste.files.append(file)

        with database.session() as session:
            session.add(paste)
            session.commit()

            # The removal cookie is set for the specific path of the paste it is
            # related to
            self.set_cookie(
                "removal", str(paste.removal), path=f"/{paste.slug}"
            )

            url_request = self.request.full_url()
            url_paste = urljoin(url_request, f"/{paste.slug}")
            url_removal = urljoin(url_request, f"/remove/{paste.removal}")
            url_raw = urljoin(url_request, f"/raw/{file.slug}")

            self.write(
                f"Paste URL:   {url_paste}\nRaw URL:     {url_raw}\nRemoval URL: {url_removal}\n"
            )


def make_application() -> tornado.web.Application:
    return tornado.web.Application(
        [
            (r"/", CreatePaste),
            (r"/\+(.*)", CreatePaste),
            (r"/create", CreateAction),
            (r"/show/([A-Z2-7]+)(?:#.+)?", RedirectShowPaste),
            (r"/repaste/([A-Z2-7]+)", RepastePaste),
            (r"/repaste/([A-Z2-7]+)/\+(.*)", RepastePaste),
            (r"/raw/([A-Z2-7]+)(?:#.+)?", RawFile),
            (r"/download/([A-Z2-7]+)(?:#.+)?", DownloadFile),
            (r"/remove/([A-Z2-7]+)", RemovePaste),
            (r"/about", AboutPage),
            (r"/removal", RemovalPage),
            (r"/expiry", ExpiryPage),
            (r"/json/new", APINew),
            (r"/json/remove", APIRemove),
            (r"/json/show/([A-Z2-7]+)(?:#.+)?", APIShow),
            (r"/json/lexers", APILexers),
            (r"/json/expiries", APIExpiries),
            (r"/curl", CurlCreate),
            (
                r"/static/(.*)",
                tornado.web.StaticFileHandler,
                {"path": path.static},
            ),
            (r"/(.*)(?:#.+)?", ShowPaste),
        ],
        template_path=path.template,
        default_handler_class=Base,
    )
