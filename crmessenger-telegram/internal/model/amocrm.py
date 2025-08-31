from dataclasses import dataclass
from datetime import datetime


@dataclass
class AmocrmSource:
    amocrm_source_id: int
    userbot_tg_user_id: int

    amocrm_pipeline_id: int
    amocrm_external_id: str
    amocrm_scope_id: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                userbot_tg_user_id=row.userbot_tg_user_id,
                amocrm_source_id=row.amocrm_source_id,
                amocrm_pipeline_id=row.amocrm_pipeline_id,
                amocrm_external_id=row.amocrm_external_id,
                amocrm_scope_id=row.amocrm_scope_id,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]


@dataclass
class Contact:
    id: int

    first_name: str
    last_name: str
    tg_chat_id: int

    amocrm_contact_id: int
    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                first_name=row.first_name,
                last_name=row.last_name,
                tg_chat_id=row.tg_chat_id,
                amocrm_contact_id=row.amocrm_contact_id,
                created_at=row.created_at,
            )
            for row in rows
        ]


@dataclass
class Chat:
    id: int

    contact_id: int
    amocrm_conversation_id: str
    amocrm_chat_id: str

    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                contact_id=row.contact_id,
                amocrm_conversation_id=row.amocrm_conversation_id,
                amocrm_chat_id=row.amocrm_chat_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class Message:
    id: int
    chat_id: int

    role: str
    text: str
    amocrm_message_id: str

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                chat_id=row.chat_id,
                role=row.role,
                text=row.text,
                amocrm_message_id=row.amocrm_message_id
            )
            for row in rows
        ]
