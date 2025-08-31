import base64
import uuid

from opentelemetry.trace import Status, StatusCode, SpanKind

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.auth import ExportLoginTokenRequest
from telethon.tl.types.auth import LoginToken, LoginTokenSuccess
from telethon.errors import (
    AuthTokenExpiredError,
    AuthTokenAlreadyAcceptedError,
    AuthTokenInvalidError,
)
from internal import interface, model, common

class UserbotService(interface.IUserbotService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            userbot_repo: interface.IUserbotRepo,
            amocrm_service: interface.IAmocrmService,
            message_handler: interface.ITgMiddleware,
            joined_chat__handler: interface.ITgMiddleware,
            api_id: int,
            api_hash: str,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.message_handler = message_handler.get_event_handler()
        self.joined_chat_handler = joined_chat__handler.get_event_handler()

        self.userbot_repo = userbot_repo
        self.amocrm_service = amocrm_service

        self.api_id = api_id
        self.api_hash = api_hash

        self.qr_sessions: dict[str, model.QrSession] = {}
        self.active_userbots: dict[int, TelegramClient] = {}


    async def generate_qr_code(self) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "UserbotService.generate_qr_code",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                session = StringSession()
                client = TelegramClient(session, self.api_id, self.api_hash)
                await client.connect()

                qr_session_id = str(uuid.uuid4())
                qr_session = model.QrSession(
                    client=client,
                    string_session=session,
                    status=common.QRCodeStatus.PENDING
                )
                self.qr_sessions[qr_session_id] = qr_session

                auth_result = await client(ExportLoginTokenRequest(
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    except_ids=[]
                ))

                token_b64url = base64.urlsafe_b64encode(auth_result.token).decode().rstrip('=')
                qr_url = f"tg://login?token={token_b64url}"

                span.set_status(StatusCode.OK)
                return qr_session_id, qr_url
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def qr_code_status(self, session_id: str) -> tuple[str, str | None]:
        with self.tracer.start_as_current_span(
                "UserbotService.qr_code_status",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                qr_session = self.qr_sessions.get(session_id)
                if not qr_session:
                    return common.QRCodeStatus.ERROR, None

                auth_result = await qr_session.client(ExportLoginTokenRequest(
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    except_ids=[]
                ))

                if isinstance(auth_result, LoginTokenSuccess):
                    self.logger.info("QRCode успешно подтвержден")

                    qr_session.client.add_event_handler(self.message_handler, events.NewMessage())
                    qr_session.client.add_event_handler(self.joined_chat_handler, events.NewMessage())
                    del self.qr_sessions[session_id]

                    user = auth_result.authorization.user
                    session_string = qr_session.string_session.save()
                    await self.userbot_repo.create_userbot(user.id, session_string, user.phone)
                    self.active_userbots[user.id] = qr_session.client

                    await self.amocrm_service.create_amocrm_source(user.id)

                    span.set_status(StatusCode.OK)
                    return common.QRCodeStatus.CONFIRMED, user.first_name
                else:
                    return common.QRCodeStatus.PENDING, None

            except AuthTokenExpiredError:
                print("⏰ Токен истек")
                return common.QRCodeStatus.EXPIRED, None
            except AuthTokenAlreadyAcceptedError:
                print("✅ Токен уже принят!")
                return common.QRCodeStatus.ERROR, None
            except AuthTokenInvalidError:
                print("❌ Недействительный токен")
                return common.QRCodeStatus.ERROR, None
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise

    async def start_all(self):
        with self.tracer.start_as_current_span(
                "UserbotService.start_all",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                userbots = await self.userbot_repo.all_userbot()
                for userbot in userbots:
                    client = TelegramClient(StringSession(userbot.session_string), self.api_id, self.api_hash)
                    client.add_event_handler(self.message_handler, events.NewMessage())
                    client.add_event_handler(self.joined_chat_handler, events.NewMessage())

                    await client.connect()
                    self.active_userbots[userbot.tg_user_id] = client

                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def send_message_to_telegram(self, userbot_tg_user_id: int, tg_chat_id: int, text: str):
        with self.tracer.start_as_current_span(
                "UserbotService.send_message_to_telegram",
                kind=SpanKind.INTERNAL,
                attributes={
                    "userbot_tg_user_id": userbot_tg_user_id,
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                userbot = self.active_userbots.get(userbot_tg_user_id)
                if not userbot:
                    self.logger.warn("Не найден активный userbot")
                    return

                await userbot.send_message(tg_chat_id, text)
                self.logger.debug("Отправили сообщение в телеграм")

                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise
