import logging

from urllib.parse import urljoin

import tornado.web

from pinnwand import utility, database


log = logging.getLogger(__name__)


class Create(tornado.web.RequestHandler):
    def check_xsrf_cookie(self) -> None:
        return

    def get(self) -> None:
        raise tornado.web.HTTPError(400)

    def post(self) -> None:
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
