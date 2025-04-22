from random import randint, choices
from string import ascii_lowercase


def generate_task_name() -> str:
    return "".join(choices(ascii_lowercase, k=randint(10, 20)))


def generate_task_description() -> str:
    return "".join(choices(ascii_lowercase, k=randint(30, 50)))
