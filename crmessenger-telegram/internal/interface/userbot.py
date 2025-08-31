from abc import abstractmethod
from typing import Protocol, Callable, Any
from typing_extensions import Awaitable

from telethon import events

from internal import model


class IUserbotHttpController(Protocol):

    @abstractmethod
    async def generate_qr_code(self): pass

    @abstractmethod
    async def qr_code_status(self, session_id: str): pass


class ITgMiddleware(Protocol):
    def get_event_handler(self) -> Callable[[events], Awaitable[Any]]: pass


class IUserbotTgController(Protocol):
    @abstractmethod
    async def message_handler(self, event: events.NewMessage.Event): pass

    @abstractmethod
    async def joined_chat(self, event: events.ChatAction.Event): pass


class IUserbotService(Protocol):
    @abstractmethod
    async def generate_qr_code(self) -> tuple[str, str]: pass

    @abstractmethod
    async def qr_code_status(self, session_id: str) -> tuple[str, str | None]: pass

    @abstractmethod
    async def start_all(self): pass

    @abstractmethod
    async def send_message_to_telegram(self, userbot_tg_user_id: int, tg_chat_id: int, text: str): pass


class IUserbotRepo(Protocol):
    @abstractmethod
    async def create_userbot(
            self,
            tg_user_id: int,
            session_string: str,
            tg_phone_number: str
    ) -> int: pass

    @abstractmethod
    async def all_userbot(self) -> list[model.Userbot]: pass

    @abstractmethod
    async def userbot_by_tg_user_id(self, userbot_tg_user_id: int) -> list[model.Userbot]: pass


class IAmocrmClient(Protocol):
    @abstractmethod
    async def create_source(
            self,
            source_name: str,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            amocrm_token: str,
            amocrm_subdomain: str,
    ) -> int: pass

    @abstractmethod
    async def connect_channel_to_account(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
    ) -> str: pass

    @abstractmethod
    async def create_contact(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            contact_name: str,
            first_name: str,
            last_name: str
    ) -> int: pass

    @abstractmethod
    async def create_lead(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            amocrm_contact_id: int,
            amocrm_pipeline_id: int,
    ) -> int: pass

    @abstractmethod
    async def update_message_status(
            self,
            message_id: str,
            status: int,
            amocrm_scope_id: str,
            error_code: int = None,
            error: str = None
    ) -> None: pass

    @abstractmethod
    async def create_chat(
            self,
            amocrm_conversation_id: str,
            amocrm_contact_id: int,
            amocrm_scope_id: str,
            contact_name: str,
    ) -> str: pass

    @abstractmethod
    async def assign_chat_to_contact(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            amocrm_chat_id: str,
            amocrm_contact_id: int
    ) -> None: pass

    @abstractmethod
    async def send_message_from_contact(
            self,
            amocrm_contact_id: int,
            amocrm_conversation_id: str,
            amocrm_chat_id: str,
            amocrm_scope_id: str,
            amocrm_external_id: str,
            contact_name: str,
            text: str,
    ) -> str: pass

    @abstractmethod
    async def import_message_from_userbot_to_amocrm(
            self,
            amocrm_conversation_id: str,
            amocrm_chat_id: str,
            amocrm_contact_id: int,
            amocrm_external_id: str,
            amocrm_scope_id: str,
            userbot_tg_user_id: int,
            contact_name: str,
            text: str,
    ) -> str: pass

    @abstractmethod
    async def delete_source(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            source_id: int,
    ): pass
