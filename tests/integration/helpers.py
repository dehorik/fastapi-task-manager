from datetime import UTC, datetime
from typing import Dict
from uuid import UUID

from auth.schemas import TokenPayloadSchema
from auth.tokens import encode_token


def get_fake_token_payload(user_id: UUID) -> TokenPayloadSchema:
    return TokenPayloadSchema(
        sub=user_id,
        iat=datetime.now(UTC),
        exp=datetime.now(UTC)
    )


def get_token(user_id: UUID) -> str:
    return encode_token({"sub": str(user_id)})


def get_auth_headers(user_id: UUID) -> Dict[str, str]:
    return {"Authorization": f"Bearer {get_token(user_id)}"}
