from datetime import datetime

from pydantic import BaseModel

class RegisterBody(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    account_id: int

class LoginBody(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    account_id: int

class SetTwoFaBody(BaseModel):
    two_fa_key: str
    two_fa_code: str

class DeleteTwoFaBody(BaseModel):
    two_fa_code: str

class VerifyTwoFaBody(BaseModel):
    two_fa_code: str

class VerifyTwoFaResponse(BaseModel):
    is_two_fa_verified: bool

class ForgotPasswordBody(BaseModel):
    email: str

class RecoveryPasswordBody(BaseModel):
    new_password: str

class ChangePasswordBody(BaseModel):
    old_password: str
    new_password: str