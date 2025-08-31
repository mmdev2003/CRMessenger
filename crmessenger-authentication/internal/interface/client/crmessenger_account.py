from abc import abstractmethod
from typing import Protocol


class ICRMessengerAccountClient(Protocol):
    @abstractmethod
    async def create_account(self, account_id: int, email: str): pass
