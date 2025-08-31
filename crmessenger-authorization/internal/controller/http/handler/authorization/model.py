from pydantic import BaseModel

class AuthorizationBody(BaseModel):
    account_id: int
    two_fa_status: bool

class AuthorizationResponse(BaseModel):
    access_token: str
    refresh_token: str

class CheckAuthorizationResponse(BaseModel):
    account_id: int
    two_fa_status: bool
    message: str