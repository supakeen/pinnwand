from typing import Any
from urllib.parse import urljoin

import tornado.web

from pinnwand.configuration import Configuration, ConfigurationProvider
from pinnwand.database import models, manager
from pinnwand import defensive, error, logger, utility

log = logger.get_logger(__name__)


class Create(tornado.web.RequestHandler):
    def check_xsrf_cookie(self) -> None:
        return

    def get(self) -> None:
        raise tornado.web.HTTPError(400)

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        type_, exc, traceback = kwargs["exc_info"]

        if type_ == error.ValidationError:
            self.set_status(400)
            self.write(str(exc))
        elif type_ == error.RatelimitError:
            self.set_status(429)
            self.write("Enhance your calm, you have exceeded the ratelimit.")
        else:
            super().write_error(status_code, **kwargs)

    @defensive.ratelimit(area="create")
    def post(self) -> None:

        configuration: Configuration = ConfigurationProvider.get_config()
        lexer = self.get_body_argument("lexer", "text")
        raw = self.get_body_argument("raw", "", strip=False)
        expiry = self.get_body_argument("expiry", "1day")

        self.set_header("Content-Type", "text/plain")

        if lexer not in utility.list_languages():
            log.info(
                "CurlCreate.post: a paste was submitted with an invalid lexer"
            )
            raise error.ValidationError("Invalid `lexer` supplied.\n")

        # Guard against empty strings
        if not raw or not raw.strip():
            log.info("CurlCreate.post: a paste was submitted without raw")
            raise error.ValidationError("Invalid `raw` supplied.\n")

        if expiry not in configuration.expiries:
            log.info("CurlCreate.post: a paste was submitted without raw")
            raise error.ValidationError("Invalid `expiry` supplied.\n")

        paste = models.Paste(
            utility.slug_create(), configuration.expiries[expiry], "curl"
        )
        file = models.File(paste.slug, raw, lexer)
        paste.files.append(file)

        with manager.DatabaseManager.get_session() as session:
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
