from datetime import datetime, timedelta, UTC
from typing import Dict, Any

import jwt

from core import settings


def encode_token(paylaod: Dict[str, Any]) -> str:
    paylaod["iat"] = datetime.now(UTC)
    paylaod["exp"] = datetime.now(UTC) + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)

    return jwt.encode(
        paylaod,
        key=settings.TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        key=settings.TOKEN_SECRET_KEY,
        algorithms=settings.ALGORITHM
    )
