import warnings
from datetime import datetime, timedelta, UTC
from typing import Dict, Any

import jwt

from core import settings


def encode_token(payload: Dict[str, Any]) -> str:
    if not settings.MODE == "test":
        overridden_keys = {"iat", "exp"}.intersection(payload.keys())
        if overridden_keys:
            warnings.warn(
                f"it is not recommended to pass custom {" and ".join(overridden_keys)} parameters",
                stacklevel=2
            )

    payload.setdefault("iat", datetime.now(UTC))
    payload.setdefault(
        "exp",
        datetime.now(UTC) + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    )

    return jwt.encode(
        payload,
        key=settings.TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        key=settings.TOKEN_SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
