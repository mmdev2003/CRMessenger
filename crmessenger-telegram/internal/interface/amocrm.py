from abc import abstractmethod
from typing import Protocol

from internal.controller.http.handler.amocrm.model import *
from internal import model


class IAmocrmController(Protocol):
    @abstractmethod
    async def send_message_from_amocrm_to_telegram(self, body: TextMessageFromAmoCrmBody): pass

    @abstractmethod
    async def create_amocrm_source(self, body: CreateAmocrmSourceBody): pass

    @abstractmethod
    async def delete_amocrm_source(self, body: DeleteAmocrmSourceBody): pass


class IAmocrmService(Protocol):
    @abstractmethod
    async def create_amocrm_source(self, userbot_tg_user_id: int): pass

    @abstractmethod
    async def delete_amocrm_source(self, amocrm_token: str, amocrm_subdomain: str, amocrm_source_id: int): pass

    @abstractmethod
    async def amocrm_source_by_amocrm_external_id(self, amocrm_external_id: str) -> list[model.AmocrmSource]: pass

    @abstractmethod
    async def amocrm_source_by_userbot_tg_user_id(self, userbot_tg_user_id: int) -> list[model.AmocrmSource]: pass

    @abstractmethod
    async def new_chat(
            self,
            amocrm_scope_id: str,
            amocrm_pipeline_id: int,
            contact_tg_username: str,
            contact_first_name: str,
            contact_last_name: str,
            contact_tg_chat_id: int,
    ) -> tuple[int, str, str, int]: pass

    @abstractmethod
    async def chat_by_amocrm_chat_id(self, amocrm_chat_id: int) -> list[model.Chat]: pass

    @abstractmethod
    async def contact_by_id(self, contact_id: int) -> list[model.Contact]: pass

    @abstractmethod
    async def import_message_from_userbot_to_amocrm(
            self,
            amocrm_scope_id: str,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            userbot_tg_user_id: int,
            contact_tg_username: str,
            contact_tg_chat_id: int,
            contact_first_name: str,
            contact_last_name: str,
            text: str,
    ):pass

    @abstractmethod
    async def send_message_from_contact_to_amocrm(
            self,
            amocrm_scope_id: str,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            userbot_tg_user_id: int,
            contact_tg_username: str,
            contact_tg_chat_id: int,
            contact_first_name: str,
            contact_last_name: str,
            text: str,
            is_group_chat: bool = False,
    ): pass

    @abstractmethod
    async def create_message(self, chat_id: int, amocrm_message_id: str, role: str, text: str) -> int: pass


class IAmocrmRepo(Protocol):
    @abstractmethod
    async def create_amocrm_source(
            self,
            userbot_tg_user_id: int,
            amocrm_source_id: int,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            amocrm_scope_id: str,
    ) -> int: pass

    @abstractmethod
    async def amocrm_source_by_userbot_tg_user_id(self, userbot_tg_user_id: int) -> list[model.AmocrmSource]: pass

    @abstractmethod
    async def amocrm_source_by_amocrm_external_id(self, amocrm_external_id: str) -> list[model.AmocrmSource]: pass

    @abstractmethod
    async def create_contact(
            self,
            first_name: str,
            last_name: str,
            tg_chat_id: int,
            amocrm_contact_id: int,
    ) -> int: pass

    @abstractmethod
    async def contact_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Contact]: pass

    @abstractmethod
    async def contact_by_id(self, contact_id: int) -> list[model.Contact]: pass

    @abstractmethod
    async def create_chat(self, contact_id: int, amocrm_conversation_id: str, amocrm_chat_id: str): pass

    @abstractmethod
    async def chat_by_contact_id(self, contact_id: int) -> list[model.Chat]: pass

    @abstractmethod
    async def chat_by_amocrm_chat_id(self, amocrm_chat_id: int) -> list[model.Chat]: pass

    @abstractmethod
    async def create_message(self, chat_id: int, amocrm_message_id: str, role: str, text: str) -> int: pass
