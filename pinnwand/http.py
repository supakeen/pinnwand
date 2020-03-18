import logging
import secrets

from typing import Any, List

import tornado.web

from pinnwand import path, configuration, handler

log = logging.getLogger(__name__)


def make_application() -> tornado.web.Application:
    pages: List[Any] = [
        (r"/", handler.website.Create),
        (r"/\+(.*)", handler.website.Create),
        (r"/create", handler.website.CreateAction),
        (r"/show/([A-Z2-7]+)(?:#.+)?", handler.website.RedirectShow),
        (r"/repaste/([A-Z2-7]+)(?:#.+)?", handler.website.Repaste),
        (r"/raw/([A-Z2-7]+)(?:#.+)?", handler.website.FileRaw),
        (r"/download/([A-Z2-7]+)(?:#.+)?", handler.website.FileDownload),
        (r"/remove/([A-Z2-7]+)", handler.website.Remove),
    ]

    pages += [
        (
            f"/{file}",
            handler.website.RestructuredTextPage,
            {"file": f"{file}.rst"},
        )
        for file in configuration.page_list
    ]

    pages += [
        (r"/api/v1/paste", handler.api_v1.Paste),
        (r"/api/v1/lexer", handler.api_v1.Lexer),
        (r"/api/v1/expiry", handler.api_v1.Expiry),
        (r"/json/new", handler.api_deprecated.Create),
        (r"/json/remove", handler.api_deprecated.Remove),
        (r"/json/show/([A-Z2-7]+)(?:#.+)?", handler.api_deprecated.Show),
        (r"/json/lexers", handler.api_deprecated.Lexer),
        (r"/json/expiries", handler.api_deprecated.Expiry),
        (r"/curl", handler.api_curl.Create),
    ]

    if configuration.logo_path:
        pages += [
            (r"/static/logo.png", handler.website.Logo, {"path": configuration.logo_path}),
            (r"/static/favicon.png", handler.website.Logo, {"path": configuration.logo_path}),
        ]

    pages += [
        (
            r"/static/(.*)",
            tornado.web.StaticFileHandler,
            {"path": path.static},
        ),
        (r"/(.*)(?:#.+)?", handler.website.Show),
    ]

    app = tornado.web.Application(
        pages,
        template_path=path.template,
        default_handler_class=handler.website.Base,
        xsrf_cookies=True,
        cookie_secret=secrets.token_hex(),
    )

    app.configuration = configuration  # type: ignore

    return app
