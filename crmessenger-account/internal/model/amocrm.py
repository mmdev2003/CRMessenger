from dataclasses import dataclass
from datetime import datetime


@dataclass
class AmocrmAccount:
    id: int
    account_id: int

    amocrm_subdomain: str
    amocrm_token: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, row):
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
                amocrm_subdomain=row.amocrm_subdomain,
                amocrm_token=row.amocrm_token,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
        ]
