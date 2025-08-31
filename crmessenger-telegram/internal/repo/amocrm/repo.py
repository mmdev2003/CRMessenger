from opentelemetry.trace import Status, StatusCode, SpanKind

from .sql_query import *
from internal import interface
from internal import model


class AmocrmRepo(interface.IAmocrmRepo):
    def __init__(self, db: interface.IDB, tel: interface.ITelemetry):
        self.db = db
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    async def create_amocrm_source(
            self,
            userbot_tg_user_id: int,
            amocrm_source_id: int,
            amocrm_pipeline_id: int,
            amocrm_external_id: str,
            amocrm_scope_id: str,
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.create_amocrm_source",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_source_id": amocrm_source_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "amocrm_external_id": amocrm_external_id,
                    "amocrm_scope_id": amocrm_scope_id,
                    "userbot_tg_user_id": userbot_tg_user_id,
                }
        ) as span:
            try:
                args = {
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "amocrm_source_id": amocrm_source_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "amocrm_external_id": amocrm_external_id,
                    "amocrm_scope_id": amocrm_scope_id,
                }
                amocrm_id = await self.db.insert(create_amocrm_source, args)

                span.set_status(StatusCode.OK)
                return amocrm_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def amocrm_source_by_userbot_tg_user_id(self, userbot_tg_user_id: int) -> list[model.AmocrmSource]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.amocrm_source_by_userbot_tg_user_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                }
        ) as span:
            try:
                args = {
                    "userbot_tg_user_id": userbot_tg_user_id,
                }
                rows = await self.db.select(amocrm_source_by_userbot_tg_user_id, args)
                if rows:
                    rows = model.AmocrmSource.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def create_chat(self, contact_id: int, amocrm_conversation_id: str, amocrm_chat_id: str):
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "contact_id": contact_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_chat_id": amocrm_chat_id
                }
        ) as span:
            try:
                args = {
                    'contact_id': contact_id,
                    'amocrm_conversation_id': amocrm_conversation_id,
                    'amocrm_chat_id': amocrm_chat_id
                }
                chat_id = await self.db.insert(create_chat, args)

                span.set_status(StatusCode.OK)
                return chat_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def amocrm_source_by_amocrm_external_id(self, amocrm_external_id: str) -> list[model.AmocrmSource]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.amocrm_source_by_amocrm_external_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_external_id": amocrm_external_id,
                }
        ) as span:
            try:
                args = {
                    "amocrm_external_id": amocrm_external_id,
                }
                rows = await self.db.select(amocrm_source_by_amocrm_external_id, args)
                if rows:
                    rows = model.AmocrmSource.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def chat_by_contact_id(self, contact_id: int) -> list[model.Chat]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.chat_by_contact_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "contact_id": contact_id,
                }
        ) as span:
            try:
                args = {'contact_id': contact_id}
                rows = await self.db.select(chat_by_contact_id, args)
                if rows:
                    rows = model.Chat.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def chat_by_amocrm_chat_id(self, amocrm_chat_id: int) -> list[model.Chat]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.chat_by_amocrm_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                }
        ) as span:
            try:
                args = {'amocrm_chat_id': amocrm_chat_id}
                rows = await self.db.select(chat_by_amocrm_chat_id, args)
                if rows:
                    rows = model.Chat.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def create_contact(
            self,
            first_name: str,
            last_name: str,
            tg_chat_id: int,
            amocrm_contact_id: int,
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.create_contact",
                kind=SpanKind.INTERNAL,
                attributes={
                    "first_name": first_name,
                    "last_name": last_name,
                    "tg_chat_id": tg_chat_id,
                    "amocrm_contact_id": amocrm_contact_id,
                }
        ) as span:
            try:
                args = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'tg_chat_id': tg_chat_id,
                    'amocrm_contact_id': amocrm_contact_id
                }
                contact_id = await self.db.insert(create_contact, args)

                span.set_status(StatusCode.OK)
                return contact_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def contact_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Contact]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.contact_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                args = {'tg_chat_id': tg_chat_id}
                rows = await self.db.select(contact_by_tg_chat_id, args)
                if rows:
                    rows = model.Contact.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def contact_by_id(self, contact_id: int) -> list[model.Contact]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.contact_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "contact_id": contact_id,
                }
        ) as span:
            try:
                args = {'contact_id': contact_id}
                rows = await self.db.select(contact_by_id, args)
                if rows:
                    rows = model.Contact.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def create_message(self, chat_id: int, amocrm_message_id: str, role: str, text: str) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.create_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "amocrm_message_id": amocrm_message_id,
                    "role": role,
                    "text": text
                }
        ) as span:
            try:
                args = {
                    "chat_id": chat_id,
                    "amocrm_message_id": amocrm_message_id,
                    "role": role,
                    "text": text
                }
                message_id = await self.db.insert(create_message, args)

                span.set_status(StatusCode.OK)
                return message_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
