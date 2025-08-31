from dataclasses import dataclass
from datetime import datetime


@dataclass
class Account:
    id: int

    login: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, row):
        return [
            cls(
                id=row.id,
                login=row.login,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
        ]
