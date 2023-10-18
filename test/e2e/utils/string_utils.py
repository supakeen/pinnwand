import random
import string


def random_string(size=1000) -> str:
    return random.choice(string.ascii_letters) + "".join(
        [
            random.choice(
                string.ascii_letters
                + string.digits
                + string.punctuation
                + " \n\t"
            )
            for i in range(size)
        ]
    )


def random_letter_string(size=10) -> str:
    return "".join([random.choice(string.ascii_letters) for i in range(size)])


def convert_new_lines(text):
    return text.replace("\n", "\r\n")
