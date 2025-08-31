from pydantic import BaseModel


class CreateUserBotBody(BaseModel):
    tg_phone_number: str
    tg_api_id: int
    tg_hash_id: str


class AuthenticateUserBot(BaseModel):
    tg_phone_number: str
    tg_authorization_code: str
    tg_api_id: int
    tg_hash_id: str


class IncludeHandlersBody(BaseModel):
    userbot_tg_user_id: int


class StartAllUserbotBody(BaseModel):
    interserver_secret_key: str
