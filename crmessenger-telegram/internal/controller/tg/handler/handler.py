from opentelemetry.trace import Status, StatusCode, Span, SpanKind
from telethon import TelegramClient, events
from telethon.tl.types import Chat, User
from telethon.types import Message

from internal import interface
from internal import model
from internal import common


class UserbotTgController(interface.IUserbotTgController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_service: interface.IAmocrmService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.amocrm_service = amocrm_service

    async def message_handler(self, event: events):
        with self.tracer.start_as_current_span(
                "UserbotController.message_handler",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                event = event.NewMessage.Event
                chat = await event.get_chat()
                me = await event.client.get_me()
                amocrm_source = (await self.amocrm_service.amocrm_source_by_userbot_tg_user_id(me.id))[0]

                if isinstance(chat, Chat):
                    if event.message.out:
                        self.logger.info("Исходящее сообщение из группового чата")
                        span.set_attribute(common.TELEGRAM_MESSAGE_DIRECTION_KEY, "outgoing")

                        await self.amocrm_service.import_message_from_userbot_to_amocrm(
                            amocrm_source.amocrm_scope_id,
                            amocrm_source.amocrm_pipeline_id,
                            amocrm_source.amocrm_external_id,
                            amocrm_source.userbot_tg_user_id,
                            chat.title,
                            chat.id,
                            chat.title,
                            chat.title,
                            event.message.message,
                        )
                    else:
                        self.logger.info("Входящее сообщение из группового чата")
                        span.set_attribute(common.TELEGRAM_MESSAGE_DIRECTION_KEY, "ingoing")

                        sender = await event.get_sender()
                        await self.amocrm_service.send_message_from_contact_to_amocrm(
                            amocrm_source.amocrm_scope_id,
                            amocrm_source.amocrm_pipeline_id,
                            amocrm_source.amocrm_external_id,
                            amocrm_source.userbot_tg_user_id,
                            sender.username,
                            chat.id,
                            sender.first_name,
                            sender.last_name,
                            event.message.message,
                            is_group_chat=True,
                        )
                elif isinstance(chat, User):
                    if event.message.out:
                        self.logger.info("Исходящее сообщение из личного чата")
                        span.set_attribute(common.TELEGRAM_MESSAGE_DIRECTION_KEY, "outgoing")

                        await self.amocrm_service.import_message_from_userbot_to_amocrm(
                            amocrm_source.amocrm_scope_id,
                            amocrm_source.amocrm_pipeline_id,
                            amocrm_source.amocrm_external_id,
                            amocrm_source.userbot_tg_user_id,
                            chat.username,
                            chat.id,
                            chat.first_name,
                            chat.last_name,
                            event.message.message,
                        )
                    else:
                        self.logger.info("Входящее сообщение из личного чата")
                        span.set_attribute(common.TELEGRAM_MESSAGE_DIRECTION_KEY, "ingoing")

                        sender = await event.get_sender()
                        await self.amocrm_service.send_message_from_contact_to_amocrm(
                            amocrm_source.amocrm_scope_id,
                            amocrm_source.amocrm_pipeline_id,
                            amocrm_source.amocrm_external_id,
                            amocrm_source.userbot_tg_user_id,
                            sender.username,
                            chat.id,
                            sender.first_name,
                            sender.last_name,
                            event.message.message
                        )

                else:
                    # events from TG CHANNELS or smt like this
                    pass
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def joined_chat(self, event: events):
        with self.tracer.start_as_current_span(
                "UserbotController.joined_chat",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                event = event.ChatAction.Event
                chat = await event.get_chat()
                me = await event.client.get_me()

                amocrm_source = await self.amocrm_service.amocrm_source_by_userbot_tg_user_id(me.id)

                contact_tg_chat_id = chat.id
                contact_tg_username = chat.title
                contact_first_name = chat.title
                contact_last_name = str(chat.id)

                if contact_last_name is None:
                    contact_last_name = "Фамилия"
                if contact_tg_username is None:
                    contact_tg_username = "tg_username"

                if amocrm_source:
                    self.logger.info("Оповещаем Amocrm о новом чате")
                    span.set_attribute(common.CRM_SYSTEM_NAME_KEY, "amocrm")

                    amocrm_source = amocrm_source[0]
                    await self.amocrm_service.new_chat(
                        amocrm_source.amocrm_scope_id,
                        amocrm_source.amocrm_pipeline_id,
                        contact_tg_username,
                        contact_first_name,
                        contact_last_name,
                        contact_tg_chat_id,
                    )

                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
