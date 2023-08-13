import random
import string


def random_string(size=1000) -> str:
    return "".join(
        [
            random.choice(
                string.ascii_letters + string.digits + string.punctuation
            )
            for i in range(size)
        ]
    )
