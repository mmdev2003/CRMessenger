from pydantic import BaseModel

class CreateAccountBody(BaseModel):
    account_id: int
    login: str
    inter_server_secret_key: str
