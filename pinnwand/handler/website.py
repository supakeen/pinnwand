import logging

from typing import Any

import docutils.core
import tornado.web

from pinnwand import database, path, utility, error

log = logging.getLogger(__name__)


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


class Create(Base):
    """The index page shows the new paste page with a list of all available
       lexers from Pygments."""

    async def get(self, lexers: str = "") -> None:
        """Render the new paste form, optionally have a lexer preselected from
           the URL."""

        lexers_available = utility.list_languages()
        lexers_selected = [
            lexer for lexer in lexers.split("+") if lexer.strip()
        ]

        # Our default lexer is just that, text
        if not lexers_selected:
            lexers_selected = ["text"]

        # Make sure all lexers are available
        if not all(lexer in lexers_available for lexer in lexers_selected):
            log.debug("CreatePaste.get: non-existent lexer requested")
            raise tornado.web.HTTPError(404)

        await self.render(
            "create.html",
            lexers=lexers_selected,
            lexers_available=lexers_available,
            pagetitle="Create new paste",
            message=None,
            paste=None,
        )

    async def post(self) -> None:
        """This is a historical endpoint to create pastes, pastes are marked as
           old-web and will get a warning on top of them to remove any access to
           this route.

           pinnwand has since evolved with an API which should be used and a
           multi-file paste.

           See the 'CreateAction' for the new-style creation of pastes."""

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
    """The create action is the 'new' way to create pastes and supports multi
       file pastes."""

    def post(self) -> None:  # type: ignore
        """POST handler for the 'web' side of things."""

        expiry = self.get_body_argument("expiry")

        if expiry not in utility.expiries:
            log.info(
                "CreateAction.post: a paste was submitted with an invalid expiry"
            )
            raise error.ValidationError()

        auto_scale = self.get_body_argument("long", None) is None

        lexers = self.get_body_arguments("lexer")
        raws = self.get_body_arguments("raw")
        filenames = self.get_body_arguments("filename")

        if not all([lexers, raws, filenames]):
            # Prevent empty argument lists from making it through
            raise error.ValidationError()

        with database.session() as session:
            paste = database.Paste(utility.expiries[expiry], "web", auto_scale)

            if any(len(L) != len(lexers) for L in [lexers, raws, filenames]):
                log.info("CreateAction.post: mismatching argument lists")
                raise error.ValidationError()

            for (lexer, raw, filename) in zip(lexers, raws, filenames):
                if lexer not in utility.list_languages():
                    log.info("CreateAction.post: a file had an invalid lexer")
                    raise error.ValidationError()

                if not raw:
                    log.info("CreateAction.post: a file had an empty raw")
                    raise error.ValidationError()

                paste.files.append(
                    database.File(
                        raw, lexer, filename if filename else None, auto_scale
                    )
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


class Repaste(Base):
    """Repaste is a specific case of the paste page. It only works for pre-
       existing pastes and will prefill the textarea and lexer."""

    async def get(self, slug: str) -> None:  # type: ignore
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

            lexers_available = utility.list_languages()

            await self.render(
                "create.html",
                lexers=["text"],  # XXX make this majority of file lexers?
                lexers_available=lexers_available,
                pagetitle="repaste",
                message=None,
                paste=paste,
            )


class Show(Base):
    """Show a paste."""

    async def get(self, slug: str) -> None:  # type: ignore
        """Fetch paste from database by slug and render the paste."""
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
                pagetitle=f"View paste {paste.slug}",
                can_delete=can_delete,
                linenos=False,
            )


class RedirectShow(Base):
    """Redirect old-style "/show/" paths to new-style "/" paths."""

    async def get(self, slug: str) -> None:  # type: ignore
        """Fetch paste from database and redirect to /slug if the paste
           exists."""
        with database.session() as session:
            paste = (
                session.query(database.Paste)
                .filter(database.Paste.slug == slug)
                .first()
            )

            if not paste:
                raise tornado.web.HTTPError(404)

            self.redirect(f"/{paste.slug}")


class FileRaw(Base):
    """Show a file as plaintext."""

    async def get(self, file_id: str) -> None:  # type: ignore
        """Get a file from the database and show it in the plain."""

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


class FileDownload(Base):
    """Download a file."""

    async def get(self, file_id: str) -> None:  # type: ignore
        """Get a file from the database and download it in the plain."""

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


class Remove(Base):
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


class RestructuredTextPage(Base):
    def initialize(self, file: str) -> None:
        self.file = file

    async def get(self) -> None:
        try:
            with open(path.page / self.file) as f:
                html = docutils.core.publish_parts(
                    f.read(), writer_name="html"
                )["html_body"]
        except FileNotFoundError:
            raise tornado.web.HTTPError(404)

        self.render(
            "restructuredtextpage.html",
            html=html,
            pagetitle=(path.page / self.file).stem,
        )


class Logo(Base):
    def initialize(self, path: str) -> None:
        self.path = path

    def get(self) -> None:
        self.set_header("Content-Type", "image/png")

        with open(self.path, "rb") as f:
            self.write(f.read())
