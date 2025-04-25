from datetime import UTC, datetime
from random import randint, choices
from string import ascii_lowercase
from typing import Dict
from uuid import UUID

from auth.schemas import TokenPayloadSchema
from auth.tokens import encode_token


def get_fake_token_payload(user_id: UUID) -> TokenPayloadSchema:
    """Хелпер для получения схемы полезной нагрузки токена (для моков)"""

    return TokenPayloadSchema(
        sub=user_id,
        iat=datetime.now(UTC),
        exp=datetime.now(UTC)
    )


def get_token(user_id: UUID) -> str:
    """Выпуск валидного jwt (для моков)"""

    return encode_token({"sub": str(user_id)})


def get_auth_headers(user_id: UUID) -> Dict[str, str]:
    return {"Authorization": f"Bearer {get_token(user_id)}"}


def generate_username() -> str:
    return "".join(choices(ascii_lowercase, k=randint(6, 10)))


def generate_password() -> str:
    return "".join(str(randint(1, 9)) for _ in range(randint(8, 12)))
