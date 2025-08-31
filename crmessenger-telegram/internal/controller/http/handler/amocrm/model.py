from pydantic import BaseModel


class CreateAmocrmSourceBody(BaseModel):
    userbot_tg_user_id: int
    amocrm_pipeline_id: int


class DeleteAmocrmSourceBody(BaseModel):
    amocrm_token: str
    amocrm_subdomain: str
    amocrm_source_id: int


class TextMessageFromAmoCrmBody(BaseModel):
    account_id: str

    class Message(BaseModel):
        receiver: dict
        sender: dict
        source: dict
        conversation: dict
        message: dict

    message: Message
