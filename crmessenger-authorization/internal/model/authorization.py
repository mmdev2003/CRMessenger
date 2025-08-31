from dataclasses import dataclass
from datetime import datetime

@dataclass
class Account:
    id: int

    account_id: int
    two_fa_status: bool
    two_fa_key: str
    refresh_token: str

    created_at: datetime
    updated_at: datetime
    @classmethod
    def serialize(cls, rows):
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
                two_fa_status=row.two_fa_status,
                two_fa_key=row.two_fa_key,
                refresh_token=row.refresh_token,
                created_at=row.created_at,
                updated_at=row.updated_at
            ) for row in rows
        ]

@dataclass
class JWTToken:
    access_token: str
    refresh_token: str

@dataclass
class TokenPayload:
    account_id: int
    two_fa_status: bool
    exp: int