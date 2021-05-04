import logging
import re
import ipaddress

from typing import Dict, Union

import token_bucket

from tornado.httputil import HTTPServerRequest

from pinnwand import error, configuration


log = logging.getLogger(__name__)


ratelimit_area: Dict[
    str,
    Dict[
        Union[ipaddress.IPv4Address, ipaddress.IPv6Address],
        token_bucket.Limiter,
    ],
] = {}


def ratelimit(request: HTTPServerRequest, area: str = "global") -> bool:
    """Test if a requesting IP is ratelimited for a certain area. Areas are
    different functionalities of the website, for example 'view' or 'input' to
    differentiate between creating new pastes (low volume) or high volume
    viewing.

    Important: this does not work well for IPv6 addresses where really when a
    ratelimit is hit, we should walk up the CIDRs (/64, /48, etc) as those
    ranges usually belong to the same person. If this is encountered in real
    life this function will have to be expanded."""

    if area not in ratelimit_area:
        ratelimit_area[area] = {}

    # TODO handle valueerror as validationerror?
    address = ipaddress.ip_address(request.remote_ip)

    if address not in ratelimit_area[area]:
        ratelimit_area[area][address] = token_bucket.Limiter(
            configuration.ratelimit[area]["refill"],
            configuration.ratelimit[area]["capacity"],
            token_bucket.MemoryStorage(),
        )

    if not ratelimit_area[area][address].consume(1):
        log.warning("%s hit rate limit for %r", address, area)
        return True

    return False


def spamscore(text: str) -> int:
    """Give a naive spamscore for some text, spam to pinnwand instances seems
    to mostly consist of lists of links so we count the link count vs the total
    text in the paste.

    This will then give a value 0-100, which can be used with a configuration
    option to deny pastes over a certain percentage."""

    # TODO Is this a good URL regex?
    match = re.compile(
        r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    )

    text_size = len(text)
    link_size = sum(len(link) for link in match.findall(text))

    score = int((link_size / text_size) * 100)

    log.debug("spamscore: rated at %r score", score)

    return score
