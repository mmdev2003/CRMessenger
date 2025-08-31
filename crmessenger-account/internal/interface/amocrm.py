from abc import abstractmethod
from typing import Protocol

from fastapi import Request

from internal.controller.http.handler.amocrm_account.model import *


class IAmocrmAccountController(Protocol):
    @abstractmethod
    async def create_amocrm_account(self, request: Request, body: CreateAmocrmAccountBody): pass


class IAmocrmAccountService(Protocol):
    @abstractmethod
    async def create_amocrm_account(
            self,
            account_id: int,
            amocrm_subdomain: str,
            amocrm_token: str
    ) -> int: pass


class IAmocrmAccountRepo(Protocol):
    @abstractmethod
    async def create_amocrm_account(
            self,
            account_id: int,
            amocrm_subdomain: str,
            amocrm_token: str
    ) -> int: pass
