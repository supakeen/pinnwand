database_uri = "sqlite:///:memory:"
paste_size = 256 * 1024  # in bytes
footer = 'View <a href="//github.com/supakeen/pinnwand" target="_BLANK">source code</a>, the <a href="/removal">removal</a> or <a href="/expiry">expiry</a> stories, or read the <a href="/about">about</a> page.'
paste_help = "<p>Welcome to pinnwand, this site is a pastebin. It allows you to share code with others. If you write code in the text area below and press the paste button you will be given a link you can share with others so they can view your code as well.</p><p>People with the link can view your pasted code, only you can remove your paste and it expires automatically. Note that anyone could guess the URI to your paste so don't rely on it being private.</p>"
page_path = None
page_list = ["about", "removal", "expiry"]
default_selected_lexer = "text"
preferred_lexers = []  # type: ignore
logo_path = None
report_email = None
expiries = {"1day": 86400, "1week": 604800}
ratelimit = {
    "read": {
        "capacity": 100,
        "consume": 1,
        "refill": 2,
    },
    "create": {
        "capacity": 2,
        "consume": 2,
        "refill": 1,
    },
    "delete": {
        "capacity": 2,
        "consume": 2,
        "refill": 1,
    },
}
spamscore = 50
