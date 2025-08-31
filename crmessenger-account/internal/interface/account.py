from abc import abstractmethod
from typing import Protocol

from internal.controller.http.handler.account.model import *


class IAccountController(Protocol):
    @abstractmethod
    async def create_account(self, body: CreateAccountBody): pass


class IAccountService(Protocol):
    @abstractmethod
    async def create_account(self, account_id: int, login: str) -> int: pass


class IAccountRepo(Protocol):
    @abstractmethod
    async def create_account(self, account_id: int, login: str) -> int: pass
