import uuid

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model

from internal import interface


class AmocrmService(interface.IAmocrmService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_repo: interface.IAmocrmRepo,
            amocrm_client: interface.IAmocrmClient,
            amocrm_pipeline_id: int
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.amocrm_repo = amocrm_repo
        self.amocrm_client = amocrm_client
        self.amocrm_pipeline_id = amocrm_pipeline_id

    async def create_amocrm_source(
            self,
            userbot_tg_user_id: int,
    ):
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.create_amocrm_source",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                }
        ) as span:
            try:
                amocrm_external_id = str(uuid.uuid4())

                amocrm_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjVmYjAwMWM1OGY0YzFkN2NhMzQ4NmQ2NTk5NGM0MzczY2JiNzFhY2MxMzliNjE3NWFhZTg5MDY0OGU4ZTc2OWQ1NGYwZDRhMGZiMjEyNDZlIn0.eyJhdWQiOiI1MTllMjY2NC00Yjk1LTQxYjItYjE3YS1mZWQ1ZDJiNjFiNDIiLCJqdGkiOiI1ZmIwMDFjNThmNGMxZDdjYTM0ODZkNjU5OTRjNDM3M2NiYjcxYWNjMTM5YjYxNzVhYWU4OTA2NDhlOGU3NjlkNTRmMGQ0YTBmYjIxMjQ2ZSIsImlhdCI6MTc0ODc2OTUxNCwibmJmIjoxNzQ4NzY5NTE0LCJleHAiOjE3NjE4Njg4MDAsInN1YiI6IjEyNTEwODQ2IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyNDI3ODI2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYjA3MmMyYmItMGViYi00YzE1LThhMTQtMjJiMDkxZTM4NTMzIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.N2b6luLb0SSlrilMLUf-0bIgUUeCdvkQMQYD0SYPZaerxaqsmD7sCeZ8zozWp6GPgvjn2jCMgjLJE08nkxdtVKPVEvx4Ac1B37A4u1Ok2meGEqtOlnWp8Sfons5b34JEEFfsJTvIv2d4o4v28ejfxEkd-ri6u764uReBsAvmRtUQOaBT-md-q4T2jwcrrxLW65vFevIAKhxsHkQpUT1J2BVl6uBInLubwB2fxqLUKJINSw42qQK10YdH_gWrzU07FRe2QKM4Phr4DegjIJeO1oXlZ0UjkgUyUQtObvx_VHJluiaefFK9l0ouLMdQGIFqLo-ZMF7KdCbyxjfe7viiyQ"
                amocrm_subdomain = "mmdev2003yandexru"
                amocrm_source_name = "+79219855083"
                span.set_attribute("amocrm_subdomain", amocrm_subdomain)
                span.set_attribute("amocrm_source_name", amocrm_source_name)
                span.set_attribute("amocrm_external_id", amocrm_external_id)

                amocrm_source_id = await self.amocrm_client.create_source(
                    amocrm_source_name,
                    self.amocrm_pipeline_id,
                    amocrm_external_id,
                    amocrm_token,
                    amocrm_subdomain
                )
                self.logger.debug("Создали источник в Amocrm")
                span.set_attribute("amocrm_source_id", amocrm_source_id)

                amocrm_scope_id = await self.amocrm_client.connect_channel_to_account(
                    amocrm_token,
                    amocrm_subdomain,
                )
                self.logger.debug("Подключили источник в аккаунту в Amocrm")
                span.set_attribute("amocrm_scope_id", amocrm_scope_id)

                await self.amocrm_repo.create_amocrm_source(
                    userbot_tg_user_id,
                    amocrm_source_id,
                    self.amocrm_pipeline_id,
                    amocrm_external_id,
                    amocrm_scope_id,
                )
                self.logger.debug("Создали источник в БД")

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def delete_amocrm_source(self, amocrm_token: str, amocrm_subdomain: str, amocrm_source_id: int):
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.delete_amocrm_source",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_source_id": amocrm_source_id,
                }
        ) as span:
            try:
                await self.amocrm_client.delete_source(amocrm_token, amocrm_subdomain, amocrm_source_id)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def amocrm_source_by_amocrm_external_id(self, amocrm_external_id: str) -> list[model.AmocrmSource]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.amocrm_source_by_amocrm_external_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_external_id": amocrm_external_id,
                }
        ) as span:
            try:
                amocrmSource = await self.amocrm_repo.amocrm_source_by_amocrm_external_id(amocrm_external_id)
                span.set_status(Status(StatusCode.OK))
                return amocrmSource
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def amocrm_source_by_userbot_tg_user_id(self, userbot_tg_user_id: int) -> list[model.AmocrmSource]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.amocrm_source_by_userbot_tg_user_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                }
        ) as span:
            try:
                amocrmSource = await self.amocrm_repo.amocrm_source_by_userbot_tg_user_id(userbot_tg_user_id)
                span.set_status(Status(StatusCode.OK))
                return amocrmSource
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def create_message(self, chat_id: int, amocrm_message_id: str, role: str, text: str) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.amocrm_source_by_userbot_tg_user_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "amocrm_message_id": amocrm_message_id,
                    "role": role,
                    "text": text,
                }
        ) as span:
            try:
                message_id = await self.amocrm_repo.create_message(chat_id, amocrm_message_id, role, text)
                self.logger.debug("Создали сообщение в БД")
                span.set_attribute("message_id", message_id)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

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
    ):
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.import_message_from_userbot_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "contact_tg_username": contact_tg_username,
                    "contact_tg_chat_id": contact_tg_chat_id,
                    "contact_first_name": contact_first_name,
                    "contact_last_name": contact_last_name,
                    "text": text,
                }
        ) as span:
            try:
                if contact_last_name is None:
                    self.logger.debug("Фамилия не указана, устанавливаем фамилию 'Фамилия'")
                    contact_last_name = "Фамилия"

                contact_name = contact_first_name + " " + contact_last_name

                contact = await self.amocrm_repo.contact_by_tg_chat_id(contact_tg_chat_id)
                if not contact:
                    self.logger.debug("Мы написали первые, контакта не было до этого")
                    amocrm_contact_id, amocrm_conversation_id, amocrm_chat_id, chat_id = await self.new_chat(
                        amocrm_scope_id,
                        amocrm_pipeline_id,
                        contact_name,
                        contact_first_name,
                        contact_last_name,
                        contact_tg_chat_id,
                    )
                else:
                    chat = (await self.amocrm_repo.chat_by_contact_id(contact[0].id))[0]
                    amocrm_conversation_id = chat.amocrm_conversation_id
                    amocrm_contact_id = contact[0].amocrm_contact_id
                    amocrm_chat_id = chat.amocrm_chat_id
                    chat_id = chat.id

                span.set_attributes({
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "chat_id": chat_id,
                })

                amocrm_message_id = await self.amocrm_client.import_message_from_userbot_to_amocrm(
                    amocrm_conversation_id,
                    amocrm_chat_id,
                    amocrm_contact_id,
                    amocrm_external_id,
                    amocrm_scope_id,
                    userbot_tg_user_id,
                    contact_name,
                    text,
                )
                self.logger.debug("Создали сообщение в Amocrm")
                span.set_attribute("amocrm_message_id", amocrm_message_id)

                message_id = await self.amocrm_repo.create_message(chat_id, amocrm_message_id, "manager", text)
                self.logger.debug("Создали сообщение в БД")
                span.set_attribute("message_id", message_id)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

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
    ):
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.send_message_from_contact_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "contact_tg_username": contact_tg_username,
                    "contact_tg_chat_id": contact_tg_chat_id,
                    "contact_first_name": contact_first_name,
                    "contact_last_name": contact_last_name,
                    "text": text,
                    "is_group_chat": is_group_chat,
                }
        ) as span:
            try:
                if contact_last_name is None:
                    contact_last_name = "Фамилия"

                contact_name = contact_first_name + " " + contact_last_name

                contact = await self.amocrm_repo.contact_by_tg_chat_id(contact_tg_chat_id)
                # никогда не будет такого, что нам пишут из группового, чата,
                # а его нет в базе, ведь есть new_group_chat_handler
                if not is_group_chat and not contact:
                    self.logger.debug("Мы написали первые, контакта не было до этого")
                    amocrm_contact_id, amocrm_conversation_id, amocrm_chat_id, chat_id = await self.new_chat(
                        amocrm_scope_id,
                        amocrm_pipeline_id,
                        contact_name,
                        contact_first_name,
                        contact_last_name,
                        contact_tg_chat_id,
                    )
                else:
                    chat = (await self.amocrm_repo.chat_by_contact_id(contact[0].id))[0]
                    amocrm_conversation_id = chat.amocrm_conversation_id
                    amocrm_chat_id = chat.amocrm_chat_id
                    amocrm_contact_id = contact[0].amocrm_contact_id
                    chat_id = chat.id

                span.set_attributes({
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_chat_id": amocrm_chat_id,
                    "chat_id": chat_id,
                })

                if is_group_chat:
                    text = f"Отправитель: {contact_first_name} {contact_last_name}\n\n" + text
                    self.logger.debug("Дополнили сообщение метадатой для группы")

                amocrm_message_id = await self.amocrm_client.send_message_from_contact(
                    amocrm_contact_id,
                    amocrm_conversation_id,
                    amocrm_chat_id,
                    amocrm_scope_id,
                    amocrm_external_id,
                    contact_name,
                    text,
                )
                self.logger.debug("Создали сообщение в Amocrm")
                span.set_attribute("amocrm_message_id", amocrm_message_id)

                message_id = await self.amocrm_repo.create_message(chat_id, amocrm_message_id, "contact", text)
                self.logger.debug("Создали сообщение в БД")
                span.set_attribute("message_id", message_id)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def new_chat(
            self,
            amocrm_scope_id: str,
            amocrm_pipeline_id: int,
            contact_name: str,
            contact_first_name: str,
            contact_last_name: str,
            contact_tg_chat_id: int,
    ) -> tuple[int, str, str, int]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.new_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_scope_id": amocrm_scope_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "contact_name": contact_name,
                    "contact_first_name": contact_first_name,
                    "contact_last_name": contact_last_name,
                    "contact_tg_chat_id": contact_tg_chat_id
                }
        ) as span:
            try:
                amocrm_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjVmYjAwMWM1OGY0YzFkN2NhMzQ4NmQ2NTk5NGM0MzczY2JiNzFhY2MxMzliNjE3NWFhZTg5MDY0OGU4ZTc2OWQ1NGYwZDRhMGZiMjEyNDZlIn0.eyJhdWQiOiI1MTllMjY2NC00Yjk1LTQxYjItYjE3YS1mZWQ1ZDJiNjFiNDIiLCJqdGkiOiI1ZmIwMDFjNThmNGMxZDdjYTM0ODZkNjU5OTRjNDM3M2NiYjcxYWNjMTM5YjYxNzVhYWU4OTA2NDhlOGU3NjlkNTRmMGQ0YTBmYjIxMjQ2ZSIsImlhdCI6MTc0ODc2OTUxNCwibmJmIjoxNzQ4NzY5NTE0LCJleHAiOjE3NjE4Njg4MDAsInN1YiI6IjEyNTEwODQ2IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyNDI3ODI2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYjA3MmMyYmItMGViYi00YzE1LThhMTQtMjJiMDkxZTM4NTMzIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.N2b6luLb0SSlrilMLUf-0bIgUUeCdvkQMQYD0SYPZaerxaqsmD7sCeZ8zozWp6GPgvjn2jCMgjLJE08nkxdtVKPVEvx4Ac1B37A4u1Ok2meGEqtOlnWp8Sfons5b34JEEFfsJTvIv2d4o4v28ejfxEkd-ri6u764uReBsAvmRtUQOaBT-md-q4T2jwcrrxLW65vFevIAKhxsHkQpUT1J2BVl6uBInLubwB2fxqLUKJINSw42qQK10YdH_gWrzU07FRe2QKM4Phr4DegjIJeO1oXlZ0UjkgUyUQtObvx_VHJluiaefFK9l0ouLMdQGIFqLo-ZMF7KdCbyxjfe7viiyQ"
                amocrm_subdomain = "mmdev2003yandexru"
                amocrm_conversation_id = str(uuid.uuid4())
                span.set_attribute("amocrm_conversation_id", amocrm_conversation_id)
                span.set_attribute("amocrm_subdomain", amocrm_subdomain)

                amocrm_contact_id, amocrm_chat_id = await self.__create_amocrm_entities(
                    amocrm_token,
                    amocrm_subdomain,
                    amocrm_scope_id,
                    amocrm_conversation_id,
                    amocrm_pipeline_id,
                    contact_name,
                    contact_first_name,
                    contact_last_name,
                )
                self.logger.debug("Создали сущности в Amocrm")
                span.set_attributes({
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_chat_id": amocrm_chat_id,
                })

                contact_id = await self.amocrm_repo.create_contact(
                    contact_first_name,
                    contact_last_name,
                    contact_tg_chat_id,
                    amocrm_contact_id,
                )
                self.logger.debug("Создали контакт в БД")
                span.set_attribute("contact_id", contact_id)

                chat_id = await self.amocrm_repo.create_chat(
                    contact_id,
                    amocrm_conversation_id,
                    amocrm_chat_id,
                )
                self.logger.debug("Создали чат в БД")
                span.set_attribute("chat_id", chat_id)

                span.set_status(Status(StatusCode.OK))
                return amocrm_contact_id, amocrm_conversation_id, amocrm_chat_id, chat_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def chat_by_amocrm_chat_id(self, amocrm_chat_id: int) -> list[model.Chat]:
        return await self.amocrm_repo.chat_by_amocrm_chat_id(amocrm_chat_id)

    async def contact_by_id(self, contact_id: int) -> list[model.Contact]:
        return await self.amocrm_repo.contact_by_id(contact_id)

    async def __create_amocrm_entities(
            self,
            amocrm_token: str,
            amocrm_subdomain: str,
            amocrm_scope_id: str,
            amocrm_conversation_id: str,
            amocrm_pipeline_id: int,
            contact_name: str,
            contact_first_name: str,
            contact_last_name: str,
    ) -> tuple[int, str]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceService.__create_amocrm_entities",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_subdomain": amocrm_subdomain,
                    "amocrm_scope_id": amocrm_scope_id,
                    "amocrm_conversation_id": amocrm_conversation_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "contact_name": contact_name,
                    "contact_first_name": contact_first_name,
                    "contact_last_name": contact_last_name
                }
        ) as span:
            try:
                amocrm_contact_id = await self.amocrm_client.create_contact(
                    amocrm_token,
                    amocrm_subdomain,
                    contact_name,
                    contact_first_name,
                    contact_last_name,
                )
                self.logger.debug("Создали контакт в Amocrm")
                span.set_attribute("amocrm_contact_id", amocrm_contact_id)

                amocrm_chat_id = await self.amocrm_client.create_chat(
                    amocrm_conversation_id,
                    amocrm_contact_id,
                    amocrm_scope_id,
                    contact_name,
                )
                self.logger.debug("Создали чат в Amocrm")
                span.set_attribute("amocrm_chat_id", amocrm_chat_id)

                await self.amocrm_client.assign_chat_to_contact(
                    amocrm_token,
                    amocrm_subdomain,
                    amocrm_chat_id,
                    amocrm_contact_id
                )
                self.logger.debug("Привязали чат к контакту в Amocrm")

                amocrm_lead_id = await self.amocrm_client.create_lead(
                    amocrm_token,
                    amocrm_subdomain,
                    amocrm_contact_id,
                    amocrm_pipeline_id,
                )
                self.logger.debug("Создали лид в Amocrm")
                span.set_attribute("amocrm_lead_id", amocrm_lead_id)

                span.set_status(Status(StatusCode.OK))
                return amocrm_contact_id, amocrm_chat_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
