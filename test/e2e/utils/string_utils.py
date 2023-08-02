import random
import string


def random_string(size=1000) -> str:
    return "".join(
        [
            random.choice(string.ascii_letters + string.digits)
            for i in range(size)
        ]
    )
