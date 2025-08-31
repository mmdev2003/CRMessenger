from datetime import datetime
from dataclasses import dataclass

@dataclass
class Account:
    id: int

    email: str
    password: str

    email_two_fa: bool
    google_two_fa_key: str

    created_at: datetime
    updated_at: datetime
    @classmethod
    def serialize(cls, rows):
        return [
            cls(
                id=row.id,
                email=row.email,
                password=row.password,
                email_two_fa=row.email_two_fa,
                google_two_fa_key=row.google_two_fa_key,
                created_at=row.created_at,
                updated_at=row.updated_at
        )
            for row in rows
        ]
