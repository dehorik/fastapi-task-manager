from auth.hashing import get_password_hash, verify_password


def test_hashing() -> None:
    """
    Тест функций get_password_hash и verify_password.
    При неисправности хоть одной из них тест пройден не будет
    """

    password = "11111111"
    hash_1 = get_password_hash(password)
    hash_2 = get_password_hash(password)

    assert verify_password(password, hash_1)
    assert verify_password(password, hash_2)
    assert hash_1 != hash_2

    fake_password = "qwerty12"
    assert not verify_password(fake_password, hash_1)
