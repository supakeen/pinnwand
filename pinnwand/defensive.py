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
