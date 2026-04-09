import pytest

from pinnwand import defensive


def test_spamscore_no_links() -> None:
    text = "This is just plain text with no links at all."
    assert defensive.spamscore(text) == 0


def test_spamscore_only_links() -> None:
    text = "https://example.com/page"
    assert defensive.spamscore(text) == 100


def test_spamscore_mixed_content() -> None:
    text = "Check out https://example.com for more information about our product."
    score = defensive.spamscore(text)
    assert 0 < score < 100
    # ~23 chars out of ~70 total: ~32%
    assert 25 < score < 40


def test_spamscore_multiple_links() -> None:
    text = "Visit https://example.com and https://another.org and https://third.net for details."
    score = defensive.spamscore(text)
    # ~55 chars out of ~85 total: ~65%
    assert 60 < score < 70


def test_spamscore_http_scheme() -> None:
    text = "Visit http://example.com for more info."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_https_scheme() -> None:
    text = "Visit https://secure.example.com for more info."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_ws_scheme() -> None:
    text = "Connect to ws://websocket.example.com for real-time updates."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_wss_scheme() -> None:
    text = "Connect to wss://secure-websocket.example.com for updates."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_grpc_scheme() -> None:
    text = "Use grpc://api.example.com for API calls."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_ftp_scheme() -> None:
    text = "Download from ftp://files.example.com/archive for files."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_ftps_scheme() -> None:
    text = "Download from ftps://secure-files.example.com/data for files."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_url_with_path() -> None:
    text = "Visit https://example.com/very/long/path/to/resource/page for information."
    score = defensive.spamscore(text)
    assert score > 50


def test_spamscore_url_with_query() -> None:
    text = "Visit https://example.com/page?param=value&other=data for details."
    score = defensive.spamscore(text)
    assert score > 0


def test_spamscore_typical_spam() -> None:
    # Typical spam paste with many links and little text
    text = """https://spam-site.com/buy-now
https://spam-deals.org/click-here
https://spam-offers.net/limited-offer
https://spam-sale.com/act-fast
Buy now!"""
    score = defensive.spamscore(text)
    # Should have a very high spam score
    assert score > 80


def test_spamscore_typical_code() -> None:
    text = """def hello_world():
    '''A simple function that prints hello world.
    For more info see https://docs.python.org/
    '''
    print("Hello, World!")
    return True"""
    score = defensive.spamscore(text)
    # Should have a low spam score
    assert score < 30


def test_spamscore_domain_with_numbers() -> None:
    text = "Visit https://example123.com for more info."
    score = defensive.spamscore(text)
    assert score > 0
    assert score > 40


def test_spamscore_multiple_domains_with_numbers() -> None:
    text = "Check https://site1.com and https://page2.org and https://app3.net for details."
    score = defensive.spamscore(text)
    assert score > 50


@pytest.mark.parametrize(
    "text,expected_range",
    [
        ("No links here", (0, 0)),
        ("https://a.com", (90, 100)),
        ("Text https://link.com more text", (50, 55)),
        ("Short http://example.com text", (60, 65)),
    ],
)
def test_spamscore_ranges(text: str, expected_range: tuple) -> None:
    score = defensive.spamscore(text)
    min_score, max_score = expected_range
    assert min_score <= score <= max_score


def test_spamscore_empty_string() -> None:
    with pytest.raises(ZeroDivisionError):
        defensive.spamscore("")


def test_spamscore_whitespace_only() -> None:
    text = "    \n\t\n    "
    assert defensive.spamscore(text) == 0
