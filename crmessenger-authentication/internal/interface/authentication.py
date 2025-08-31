import io
from abc import abstractmethod
from typing import Protocol
from fastapi import Request

from internal.controller.http.handler.authentication.model import *
from internal import model


class IAuthenticationController(Protocol):
    @abstractmethod
    async def register(self, body: RegisterBody): pass

    @abstractmethod
    async def confirm_register(self, account_id: int): pass

    @abstractmethod
    async def login(self, body: LoginBody): pass

    @abstractmethod
    async def generate_two_fa(self, request: Request): pass

    @abstractmethod
    async def set_two_fa(self, request: Request, body: SetTwoFaBody): pass

    @abstractmethod
    async def delete_two_fa(self, request: Request, body: DeleteTwoFaBody): pass

    @abstractmethod
    async def verify_two_fa(self, request: Request, body: VerifyTwoFaBody): pass

    @abstractmethod
    async def forget_password(self, body: ForgotPasswordBody): pass

    @abstractmethod
    async def forgot_password_confirm(self, token: str): pass

    @abstractmethod
    async def recovery_password(self, request: Request, body: RecoveryPasswordBody): pass

    @abstractmethod
    async def change_password(self, request: Request, body: ChangePasswordBody): pass


class IAuthenticationService(Protocol):
    @abstractmethod
    async def register(self, email: str, password: str) -> model.AuthorizationDataDTO: pass

    @abstractmethod
    async def confirm_register(self, account_id: int) -> None: pass

    @abstractmethod
    async def login(
            self,
            email: str,
            password: str,
    ) -> model.AuthorizationDataDTO | None: pass

    @abstractmethod
    async def generate_two_fa_key(self, account_id: int) -> tuple[str, io.BytesIO]: pass

    @abstractmethod
    async def set_two_fa_key(self, account_id: int, two_fa_key: str, two_fa_code: str) -> None: pass

    @abstractmethod
    async def delete_two_fa_key(self, account_id: int, two_fa_code: str) -> None: pass

    @abstractmethod
    async def verify_two_fa_key(self, account_id: int, two_fa_code: str) -> bool: pass

    @abstractmethod
    async def forget_password(self, email: str) -> None: pass

    @abstractmethod
    async def forgot_password_confirmation(self, token: str) -> model.AuthorizationDataDTO: pass

    @abstractmethod
    async def recovery_password(self, account_id: int, new_password: str) -> None: pass

    @abstractmethod
    async def change_password(self, account_id: int, new_password: str, old_password: str) -> None: pass


class IAuthenticationRepo(Protocol):
    @abstractmethod
    async def create_account(self, email: str, password: str) -> int: pass

    @abstractmethod
    async def update_email_two_fa(self, account_id: int, email_two_fa: bool) -> None: pass

    @abstractmethod
    async def account_by_id(self, account_id: int) -> list[model.Account]: pass

    @abstractmethod
    async def account_by_email(self, email: str) -> list[model.Account]: pass

    @abstractmethod
    async def set_two_fa_key(self, account_id: int, two_fa_key: str) -> None: pass

    @abstractmethod
    async def delete_two_fa_key(self, account_id: int) -> None: pass

    @abstractmethod
    async def update_password(self, account_id: int, new_password: str) -> None: pass
