from abc import abstractmethod
from typing import Protocol

from internal import model

class ICRMessengerAuthorizationClient(Protocol):
    @abstractmethod
    async def authorization(self, account_id: int, two_fa_status: bool) -> model.JWTTokens: pass

    @abstractmethod
    async def check_authorization(self, access_token: str) -> model.AuthorizationData: pass
