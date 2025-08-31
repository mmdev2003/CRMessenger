from dataclasses import dataclass
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession


@dataclass
class Userbot:
    tg_user_id: int

    tg_phone_number: str
    session_string: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                tg_user_id=row.tg_user_id,
                tg_phone_number=row.tg_phone_number,
                session_string=row.session_string,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]


@dataclass
class QrSession:
    client: TelegramClient
    string_session: StringSession
    status: str
