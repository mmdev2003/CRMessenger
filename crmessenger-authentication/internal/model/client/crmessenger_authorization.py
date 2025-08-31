from pydantic import BaseModel

class JWTTokens(BaseModel):
    access_token: str
    refresh_token: str


class AuthorizationData(BaseModel):
    account_id: int
    message: str
    code: int