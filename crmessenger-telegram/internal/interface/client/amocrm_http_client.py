from abc import abstractmethod
from typing import Protocol


class IAmocrmClient(Protocol):
    @abstractmethod
    async def create_source(
            self,
            amocrm_source_name: str,
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