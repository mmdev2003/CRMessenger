from opentelemetry.trace import Status, StatusCode, SpanKind

from .model import *
from internal import interface


class AmocrmController(interface.IAmocrmController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_service: interface.IAmocrmService,
            userbot_service: interface.IUserbotService,
    ):
        self.tracer = tel.tracer()
        self.amocrm_service = amocrm_service
        self.userbot_service = userbot_service

    async def send_message_from_amocrm_to_telegram(self, body: TextMessageFromAmoCrmBody):
        text = body.message.message["text"]
        amocrm_message_id = body.message.message["id"]
        amocrm_chat_id = body.message.conversation["id"]
        amocrm_external_id = body.message.source["external_id"]

        with self.tracer.start_as_current_span(
                "AmocrmSourceController.send_message_from_amocrm_to_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "text": text,
                    "amocrm_message_id": amocrm_message_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_external_id": amocrm_external_id
                }
        ) as span:
            try:
                # первыми мы пока писать не умеем, поэтому эти сущности должны быть 100%
                amocrm_source = (await self.amocrm_service.amocrm_source_by_amocrm_external_id(amocrm_external_id))[0]
                chat = (await self.amocrm_service.chat_by_amocrm_chat_id(amocrm_chat_id))[0]
                contact = (await self.amocrm_service.contact_by_id(chat.contact_id))[0]

                await self.userbot_service.send_message_to_telegram(
                    amocrm_source.userbot_tg_user_id,
                    contact.tg_chat_id,
                    text,
                )
                message_id = await self.amocrm_service.create_message(
                    chat.id,
                    amocrm_message_id,
                    "manager",
                    text,
                )

                span.set_attribute("message_id", message_id)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def create_amocrm_source(self, body: CreateAmocrmSourceBody):
        userbot_tg_user_id = body.userbot_tg_user_id
        amocrm_pipeline_id = body.amocrm_pipeline_id
        with self.tracer.start_as_current_span(
                "AmocrmSourceController.create_amocrm_source",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id
                }
        ) as span:
            try:
                await self.amocrm_service.create_amocrm_source(
                    body.userbot_tg_user_id
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def delete_amocrm_source(self, body: DeleteAmocrmSourceBody):
        with self.tracer.start_as_current_span(
                "AmocrmSourceController.delete_amocrm_source",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_subdomain": body.amocrm_subdomain,
                    "amocrm_source_id": body.amocrm_source_id
                }
        ) as span:
            try:
                await self.amocrm_service.delete_amocrm_source(
                    body.amocrm_token,
                    body.amocrm_subdomain,
                    body.amocrm_source_id
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
