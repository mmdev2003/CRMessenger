import time
import hmac
import json
import hashlib
from email.utils import format_datetime
from zoneinfo import ZoneInfo

import requests
from uuid import uuid4
from datetime import datetime

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface


class AmocrmClient(interface.IAmocrmClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            messenger: str,
            amocrm_api_platform_base_url: str,
            amocrm_api_chats_url: str,
            amocrm_bot_name: str,
            amocrm_bot_id: str,
            amocrm_channel_secret: str,
            amocrm_channel_id: str,
            amocrm_channel_code: str
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.amocrm_api_platform_base_url = amocrm_api_platform_base_url
        self.amocrm_api_chats_url = amocrm_api_chats_url
        self.messenger = messenger
        self.amocrm_bot_name = amocrm_bot_name
        self.amocrm_bot_id = amocrm_bot_id
        self.amocrm_channel_secret = amocrm_channel_secret
        self.amocrm_channel_id = amocrm_channel_id
        self.amocrm_channel_code = amocrm_channel_code

    async def create_source(
            self,
            amocrm_source_name: str,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            amocrm_token: str,
            amocrm_subdomain: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_source_name": amocrm_source_name,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "amocrm_external_id": amocrm_external_id,
                    "amocrm_subdomain": amocrm_subdomain,
                }
        ) as span:
            try:
                body = [{
                    "name": amocrm_source_name,
                    "pipeline_id": amocrm_pipeline_id,
                    "external_id": f"{amocrm_external_id}",
                    "default": False,
                    "origin_code": self.amocrm_channel_code,
                }]

                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/sources",
                    "POST",
                    body
                )

                source_id = response["_embedded"]["sources"][0]["id"]

                span.set_status(Status(StatusCode.OK, "OK"))
                return source_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def connect_channel_to_account(
            self,
            amocrm_token: str,
            amocrm_subdomain: str
    ) -> str:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_subdomain": amocrm_subdomain,
                }
        ) as span:
            try:
                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/account?with=amojo_id",
                    "GET",
                    {}
                )
                amocrm_chat_account_id = response["amojo_id"]

                body = {
                    "account_id": amocrm_chat_account_id,
                    "title": self.messenger,
                    "hook_api_version": "v2",
                }
                span.set_attribute("amocrm_chat_account_id", amocrm_chat_account_id)

                response = await self.__request_api_chats(
                    body,
                    f"/{self.amocrm_channel_id}/connect",
                    "POST",
                )

                span.set_status(Status(StatusCode.OK, "OK"))
                return response["scope_id"]
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def create_contact(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            contact_name: str,
            first_name: str,
            last_name: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_subdomain": amocrm_subdomain,
                    "contact_name": contact_name,
                    "first_name": first_name,
                    "last_name": last_name
                }
        ) as span:
            try:
                body = [{
                    "name": contact_name,
                    "first_name": first_name,
                    "last_name": last_name,
                }]

                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/contacts",
                    "POST",
                    body
                )

                span.set_status(Status(StatusCode.OK, "OK"))
                return response["_embedded"]["contacts"][0]["id"]
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def create_lead(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            amocrm_contact_id: int,
            amocrm_pipeline_id: int
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_subdomain": amocrm_subdomain,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id
                }
        ) as span:
            try:
                body = [{
                    "pipeline_id": amocrm_pipeline_id,
                    "_embedded": {"contacts": [{"id": amocrm_contact_id}]}
                }]

                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/leads",
                    "POST",
                    body
                )

                span.set_status(Status(StatusCode.OK, "OK"))
                return response["_embedded"]["leads"][0]["id"]
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def update_message_status(
            self,
            message_id: str,
            status: int,
            amocrm_scope_id: str,
            error_code: int = None,
            error: str = None
    ) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "message_id": message_id,
                    "status": status,
                    "amocrm_scope_id": amocrm_scope_id,
                }
        ) as span:
            try:
                body = {
                    "msgid": message_id,
                    "delivery_status": status,
                    "error_code": error_code,
                    "error": error
                }

                await self.__request_api_chats(
                    body,
                    f"/{amocrm_scope_id}/{message_id}/delivery_status",
                    "POST",
                )

                span.set_status(Status(StatusCode.OK, "OK"))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def create_chat(
            self,
            amocrm_conversation_id: str,
            amocrm_contact_id: int,
            amocrm_scope_id: str,
            contact_name: str,
    ) -> str:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_scope_id": amocrm_scope_id,
                    "contact_name": contact_name,
                }
        ) as span:
            try:
                body = {
                    "conversation_id": amocrm_conversation_id,
                    "user": {
                        "id": str(amocrm_contact_id),
                        "name": str(contact_name),
                    },
                }

                response = await self.__request_api_chats(
                    body,
                    f"/{amocrm_scope_id}/chats",
                    "POST",
                )

                span.set_status(Status(StatusCode.OK, "OK"))
                return response["id"]
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def assign_chat_to_contact(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            amocrm_chat_id: str,
            amocrm_contact_id: int
    ) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_subdomain": amocrm_subdomain,
                }
        ) as span:
            try:
                body = [
                    {
                        "contact_id": amocrm_contact_id,
                        "chat_id": amocrm_chat_id,
                    }
                ]

                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/contacts/chats",
                    "POST",
                    body,
                )

                span.set_status(Status(StatusCode.OK, "OK"))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def send_message_from_contact(
            self,
            amocrm_contact_id: int,
            amocrm_conversation_id: str,
            amocrm_chat_id: str,
            amocrm_scope_id: str,
            amocrm_external_id: str,
            contact_name: str,
            text: str,
    ) -> str:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_scope_id": amocrm_scope_id,
                    "amocrm_external_id": amocrm_external_id,
                    "contact_name": contact_name,
                    "text": text,
                }
        ) as span:
            try:
                body = {
                    "event_type": "new_message",
                    "payload": {
                        "timestamp": int(time.time()),
                        "msec_timestamp": int(time.time() * 1000),
                        "msgid": str(uuid4()),
                        "conversation_id": amocrm_conversation_id,
                        "conversation_ref_id": amocrm_chat_id,
                        "sender": {
                            "id": str(amocrm_contact_id),
                            "name": contact_name,
                        },
                        "message": {
                            "type": "text",
                            "text": text,
                        },
                        "silent": False,
                        "source": {
                            "external_id": amocrm_external_id,
                        },
                    },
                }

                response = await self.__request_api_chats(
                    body,
                    f"/{amocrm_scope_id}",
                    "POST",
                )

                amocrm_message_id = response["new_message"]["msgid"]

                span.set_status(Status(StatusCode.OK, "OK"))
                return amocrm_message_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


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
    ) -> str:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_external_id": amocrm_external_id,
                    "amocrm_scope_id": amocrm_scope_id,
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "contact_name": contact_name,
                    "text": text,
                }
        ) as span:
            try:
                body = {
                    "event_type": "new_message",
                    "payload": {
                        "timestamp": int(time.time()),
                        "msec_timestamp": int(time.time() * 1000),
                        "msgid": str(uuid4()),
                        "conversation_id": amocrm_conversation_id,
                        "conversation_ref_id": amocrm_chat_id,
                        "sender": {
                            "id": str(uuid4()),
                            "name": self.amocrm_bot_name,
                            "ref_id": self.amocrm_bot_id,
                        },
                        "receiver": {
                            "id": str(amocrm_contact_id),
                            "name": contact_name,
                        },
                        "message": {
                            "type": "text",
                            "text": text,
                        },
                        "silent": True,
                        "source": {
                            "external_id": amocrm_external_id,
                        },
                    },
                }

                response = await self.__request_api_chats(
                    body,
                    f"/{amocrm_scope_id}",
                    "POST",
                )

                amocrm_message_id = response["new_message"]["msgid"]

                span.set_status(Status(StatusCode.OK, "OK"))
                return amocrm_message_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def delete_source(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            source_id: int,
    ):
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "source_id": source_id,
                    "amocrm_subdomain": amocrm_subdomain,
                }
        ) as span:
            try:
                body = [{
                    "id": source_id,
                }]

                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/sources",
                    "DELETE",
                    body,
                )

                span.set_status(Status(StatusCode.OK, "OK"))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def all_source(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
    ) -> dict:
        with self.tracer.start_as_current_span(
                "AmocrmClient.send_message_from_amocrm_to_telegram",
                kind=SpanKind.CLIENT,
                attributes={
                    "amocrm_subdomain": amocrm_subdomain,
                }
        ) as span:
            try:
                response = await self.__request_subdomain(
                    amocrm_token,
                    amocrm_subdomain + self.amocrm_api_platform_base_url + "/sources",
                    "GET",
                    {},
                )

                span.set_status(Status(StatusCode.OK, "OK"))
                return response
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e


    async def __request_subdomain(self, amocrm_token: str, url: str, http_method: str, body: list[dict] | dict) -> dict:
        self.logger.debug(f"Запрос на: {url}", {"request_body": body})
        json_body = json.dumps(body)

        headers = {
            "Authorization": f"Bearer {amocrm_token}",
            "Content-Type": "application/json",
        }

        response = requests.request(http_method, "https://" + url, headers=headers, data=json_body)
        response = response.json()
        self.logger.debug(f"Ответ от {url}", {"response_body": response})

        return response

    async def __request_api_chats(
            self,
            body: dict,
            path: str,
            http_method: str,
    ) -> dict:
        self.logger.debug(f"Запрос на: {self.amocrm_api_chats_url + path,}", {"request_body": body})
        json_body = json.dumps(body)
        body_checksum = self.__create_body_checksum(json_body)
        date = format_datetime(datetime.now(tz=ZoneInfo("Europe/Moscow")))

        signature = self.__create_signature(
            self.amocrm_channel_secret,
            body_checksum,
            path,
            date,
            http_method,
        )

        headers = self.__prepare_headers(
            body_checksum,
            signature,
            date,
        )

        response = requests.request(
            http_method,
            self.amocrm_api_chats_url + path,
            headers=headers,
            data=json_body,
        )

        try:
            response = response.json()
        except:
            response = response.text

        self.logger.debug(f"Ответ от {self.amocrm_api_chats_url + path}", {"response_body": response})
        return response

    @staticmethod
    def __create_body_checksum(
            body: str
    ) -> str:
        body_checksum = hashlib.md5(body.encode('utf-8')).hexdigest()
        return body_checksum

    @staticmethod
    def __create_signature(
            amocrm_channel_secret: str,
            body_checksum: str,
            path: str,
            date: str,
            http_method: str,
    ) -> str:
        string_to_hash = "\n".join([
            http_method.upper(),
            body_checksum,
            "application/json",
            date,
            "/v2/origin/custom" + path,
        ])

        signature = hmac.new(
            amocrm_channel_secret.encode('utf-8'),
            string_to_hash.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()

        return signature

    @staticmethod
    def __prepare_headers(body_checksum: str, signature: str, date: str) -> dict[str, str]:
        headers = {
            "Date": date,
            "Content-Type": "application/json",
            "Content-MD5": body_checksum.lower(),
            "X-Signature": signature.lower(),
        }

        return headers
