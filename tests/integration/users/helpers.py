from random import randint, choices
from string import ascii_lowercase


def generate_username() -> str:
    return "".join(choices(ascii_lowercase, k=randint(6, 10)))


def generate_password() -> str:
    return "".join(str(randint(1, 9)) for _ in range(randint(8, 12)))
