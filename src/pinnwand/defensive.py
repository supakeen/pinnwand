import re
from typing import Dict
from functools import wraps

import token_bucket
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler
from pinnwand import error, logger
from pinnwand.configuration import Configuration, ConfigurationProvider


log = logger.get_logger(__name__)


ratelimit_area: Dict[str, token_bucket.Limiter] = {}


def should_be_ratelimited(ip_address: str, area: str = "global") -> bool:
    """Test if a requesting IP is ratelimited for a certain area. Areas are
    different functionalities of the website, for example 'view' or 'input' to
    differentiate between creating new pastes (low volume) or high volume
    viewing.

    Important: this does not work well for IPv6 addresses where really when a
    ratelimit is hit, we should walk up the CIDRs (/64, /48, etc) as those
    ranges usually belong to the same person. If this is encountered in real
    life this function will have to be expanded."""

    configuration: Configuration = ConfigurationProvider.get_config()

    if area not in ratelimit_area:
        ratelimit_area[area] = token_bucket.Limiter(
            configuration.ratelimit[area]["refill"],
            configuration.ratelimit[area]["capacity"],
            token_bucket.MemoryStorage(),
        )

    if not ratelimit_area[area].consume(
        ip_address.encode("utf-8"),
        configuration.ratelimit[area]["consume"],
    ):
        log.warning("%s hit rate limit for %r", ip_address, area)
        return True

    return False


def ratelimit(area: str):
    """A ratelimiting decorator for tornado's request handlers."""

    def wrapper(func):
        @wraps(func)
        def inner(request_handler: RequestHandler, *args, **kwargs):
            if should_be_ratelimited(request_handler.request.remote_ip, area):
                raise error.RatelimitError()
            return func(request_handler, *args, **kwargs)

        return inner

    return wrapper


def spamscore(text: str) -> int:
    """Give a naive spamscore for some text, spam to pinnwand instances seems
    to mostly consist of lists of links so we count the link count vs the total
    text in the paste.

    This will then give a value 0-100, which can be used with a configuration
    option to deny pastes over a certain percentage."""

    match = re.compile(
        r"(?:http|ws|grpc|ftp)(?:s?.//[a-z-]+\.[a-z]+/?[^\"\'\ \n\r\t\v]+)"
    )

    text_size = len(text)
    link_size = sum(len(link) for link in match.findall(text))

    score = int((link_size / text_size) * 100)

    log.debug("spamscore: rated at %r score", score)

    return score
