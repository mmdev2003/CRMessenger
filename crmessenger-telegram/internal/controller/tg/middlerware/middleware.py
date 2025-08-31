import time
from typing import Callable, Any

from opentelemetry import propagate
from opentelemetry.trace import SpanKind, Status, StatusCode
from telethon import events

from telethon.events import NewMessage, ChatAction
from typing_extensions import Awaitable

from internal import interface
from internal import common


class EventContextExtractor:

    @staticmethod
    async def extract_context(event: events) -> dict:
        context = {
            'chat_id': None,
            'user_id': None,
            'username': None,
            'message_text': '',
            'message_id': None,
            'client_user_id': None,
            'event_type': 'unknown'
        }

        client = event.client

        if isinstance(event, NewMessage.Event):
            context['event_type'] = 'message'
            message = event.message
            context['chat_id'] = message.chat_id
            context['user_id'] = message.sender_id
            context['message_text'] = message.text or ''
            context['message_id'] = message.id

        elif isinstance(event, ChatAction.Event):
            context['event_type'] = 'chat_action'
            context['chat_id'] = event.chat_id
            context['user_id'] = getattr(event, 'user_id', None)
            context['message_id'] = getattr(event, 'action_message', {}).get('id', None)

        else:
            context['chat_id'] = getattr(event, 'chat_id', None)
            context['user_id'] = getattr(event, 'sender_id', None)
            context['message_text'] = getattr(event, 'text', '')
            context['message_id'] = getattr(event, 'id', None)

        try:
            if hasattr(event, 'get_sender'):
                sender = await event.get_sender()
                context['username'] = getattr(sender, 'username', None)
        except Exception:
            pass

        try:
            if not hasattr(client, '_cached_user_id'):
                me = await client.get_me()
                client._cached_user_id = me.id
            context['client_user_id'] = client._cached_user_id
        except Exception:
            pass

        return context


class TgMiddleware(interface.ITgMiddleware):
    def __init__(self, tel: interface.ITelemetry, handler: Callable[[events], Awaitable[Any]]):
        self.tel = tel
        self.meter = tel.meter()
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.handler = handler
        self.context_extractor = EventContextExtractor()

        self._init_metrics()

    def _init_metrics(self):
        self.ok_message_counter = self.meter.create_counter(
            name=common.OK_MESSAGE_TOTAL_METRIC,
            description="Total count of successful message processing",
            unit="1"
        )

        self.error_message_counter = self.meter.create_counter(
            name=common.ERROR_MESSAGE_TOTAL_METRIC,
            description="Total count of failed message processing",
            unit="1"
        )

        self.ok_join_chat_counter = self.meter.create_counter(
            name=common.OK_JOIN_CHAT_TOTAL_METRIC,
            description="Total count of successful chat join processing",
            unit="1"
        )

        self.error_join_chat_counter = self.meter.create_counter(
            name=common.ERROR_JOIN_CHAT_TOTAL_METRIC,
            description="Total count of failed chat join processing",
            unit="1"
        )

        self.message_duration = self.meter.create_histogram(
            name=common.REQUEST_DURATION_METRIC,
            description="Event processing duration in seconds",
            unit="s"
        )

        self.active_messages = self.meter.create_up_down_counter(
            name=common.ACTIVE_REQUESTS_METRIC,
            description="Number of active event processing",
            unit="1"
        )

    def get_event_handler(self) -> Callable[[events], Awaitable[Any]]:
        return self._process_event

    async def _process_event(self, event: events):
        context = await self.context_extractor.extract_context(event)

        await self._trace_middleware(event, context)

    async def _trace_middleware(self, event: events, context: dict):
        span_attributes = {
            common.TELEGRAM_USERBOT_USER_ID_KEY: context['client_user_id'],
            common.TELEGRAM_UPDATE_TYPE_KEY: context['event_type'],
            common.TELEGRAM_CHAT_ID_KEY: context['chat_id'],
            common.TELEGRAM_USER_USERNAME_KEY: context['username'],
            common.TELEGRAM_USER_MESSAGE_KEY: context['message_text'],
            common.TELEGRAM_MESSAGE_ID_KEY: context['message_id'],
        }

        with self.tracer.start_as_current_span(
                "Telegram.Update",
                context=propagate.extract({}),
                kind=SpanKind.SERVER,
                attributes=span_attributes
        ) as root_span:
            span_ctx = root_span.get_span_context()
            trace_id = format(span_ctx.trace_id, '032x')
            span_id = format(span_ctx.span_id, '016x')

            try:
                await self._metric_middleware(event, context, trace_id, span_id)
                root_span.set_status(Status(StatusCode.OK))
            except Exception as error:
                root_span.record_exception(error)
                root_span.set_status(Status(StatusCode.ERROR, str(error)))
                root_span.set_attribute(common.ERROR_KEY, True)
                raise

    async def _metric_middleware(self, event: events, context: dict, trace_id: str, span_id: str):
        start_time = time.time()
        self.active_messages.add(1)

        metric_attributes = {
            common.TELEGRAM_USERBOT_USER_ID_KEY: context['client_user_id'],
            common.TELEGRAM_UPDATE_TYPE_KEY: context['event_type'],
            common.TELEGRAM_CHAT_ID_KEY: context['chat_id'],
            common.TELEGRAM_USER_USERNAME_KEY: context['username'],
            common.TELEGRAM_USER_MESSAGE_KEY: context['message_text'],
            common.TELEGRAM_MESSAGE_ID_KEY: context['message_id'],
            common.TRACE_ID_KEY: trace_id,
            common.SPAN_ID_KEY: span_id
        }

        try:
            await self._logger_middleware(event, context, trace_id, span_id)

            duration_seconds = time.time() - start_time
            metric_attributes[common.TELEGRAM_MESSAGE_DURATION_KEY] = duration_seconds

            is_join_event = self._is_join_event(event, context)

            if is_join_event:
                self.ok_join_chat_counter.add(1, attributes=metric_attributes)
            else:
                self.ok_message_counter.add(1, attributes=metric_attributes)
                self.message_duration.record(duration_seconds, attributes=metric_attributes)

        except Exception as e:
            duration_seconds = time.time() - start_time
            metric_attributes[common.HTTP_STATUS_KEY] = 500
            metric_attributes[common.ERROR_KEY] = str(e)

            is_join_event = self._is_join_event(event, context)

            if is_join_event:
                self.error_join_chat_counter.add(1, attributes=metric_attributes)
            else:
                self.error_message_counter.add(1, attributes=metric_attributes)
                self.message_duration.record(duration_seconds, attributes=metric_attributes)
            raise
        finally:
            self.active_messages.add(-1)

    def _is_join_event(self, event: events, context: dict) -> bool:
        if isinstance(event, ChatAction.Event):
            return getattr(event, 'user_joined', False)

        if isinstance(event, NewMessage.Event) and hasattr(event.message, 'new_chat_members'):
            client_user_id = context['client_user_id']
            if event.message.new_chat_members and client_user_id:
                return any(user.id == client_user_id for user in event.message.new_chat_members)

        return False

    async def _logger_middleware(self, event: events, context: dict, trace_id: str, span_id: str):
        start_time = time.time()

        log_context = {
            common.TELEGRAM_USERBOT_USER_ID_KEY: context['client_user_id'],
            common.TELEGRAM_UPDATE_TYPE_KEY: context['event_type'],
            common.TELEGRAM_CHAT_ID_KEY: context['chat_id'],
            common.TELEGRAM_USER_USERNAME_KEY: context['username'],
            common.TELEGRAM_USER_MESSAGE_KEY: context['message_text'],
            common.TELEGRAM_MESSAGE_ID_KEY: context['message_id'],
            common.TRACE_ID_KEY: trace_id,
            common.SPAN_ID_KEY: span_id
        }

        try:
            self.logger.info("Начали обработку события", log_context)
            await self.handler(event)

            log_context[common.TELEGRAM_MESSAGE_DURATION_KEY] = int((time.time() - start_time) * 1000)
            self.logger.info("Завершили обработку события", log_context)

        except Exception as e:
            log_context[common.TELEGRAM_MESSAGE_DURATION_KEY] = int((time.time() - start_time) * 1000)
            self.logger.error(f"Ошибка обработки события: {str(e)}", log_context)
            raise
