from urllib.parse import urljoin

import tornado.web

from pinnwand import crud, database, defensive, logger, error

log = logger.get_logger(__name__)


class Create(tornado.web.RequestHandler):
    def check_xsrf_cookie(self) -> None:
        return

    def get(self) -> None:
        raise tornado.web.HTTPError(400)
    
    def write_error(self, status_code: int, **kwargs) -> None:
        type_, exc, _ = kwargs["exc_info"]
        if type_ is error.ValidationError:
            self.set_status(400)
            self.write({"state": "error", "code": status_code, "message": str(exc)})
        
        super().write_error(status_code, **kwargs)

    def post(self) -> None:
        if defensive.ratelimit(self.request, area="create"):
            self.set_status(429)
            self.write("Enhance your calm, you have exceeded the ratelimit.")
            return

        lexer = self.get_body_argument("lexer", "text")
        raw = self.get_body_argument("raw", "", strip=False)
        expiry = self.get_body_argument("expiry", "1day")

        self.set_header("Content-Type", "text/plain")
        
        files = [crud.PastedFile(lexer, raw, "curl")]
        with database.session() as session:
            paste = crud.create_paste(session, files, expiry, auto_scale=True, source="curl")

        # The removal cookie is set for the specific path of the paste it is
        # related to
        self.set_cookie(
            "removal", paste.removal_slug, path=f"/{paste.paste_slug}"
        )

        url_request = self.request.full_url()
        url_paste = urljoin(url_request, f"/{paste.paste_slug}")
        url_removal = urljoin(url_request, f"/remove/{paste.removal_slug}")
        url_raw = urljoin(url_request, f"/raw/{paste.paste_slug}")

        self.write(
            f"Paste URL:   {url_paste}\nRaw URL:     {url_raw}\nRemoval URL: {url_removal}\n"
        )
