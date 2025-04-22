from random import randint, choices
from string import ascii_lowercase


def generate_group_name() -> str:
    return "".join(choices(ascii_lowercase, k=randint(16, 26)))


def generate_group_description() -> str:
    return "".join(choices(ascii_lowercase, k=randint(30, 50)))
