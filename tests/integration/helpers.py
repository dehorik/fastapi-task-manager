from datetime import UTC, datetime
from uuid import UUID

from auth import TokenPayloadSchema


def get_fake_token_payload(user_id: UUID) -> TokenPayloadSchema:
    return TokenPayloadSchema(
        sub=user_id,
        iat=datetime.now(UTC),
        exp=datetime.now(UTC)
    )
