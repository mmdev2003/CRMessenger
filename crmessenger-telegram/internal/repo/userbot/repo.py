from opentelemetry.trace import SpanKind, Status, StatusCode

from .sql_query import *
from internal import model
from internal import interface


class UserbotRepo(interface.IUserbotRepo):
    def __init__(self, db: interface.IDB, tel: interface.ITelemetry):
        self.db = db
        self.tracer = tel.tracer()

    async def create_userbot(
            self,
            tg_user_id: int,
            session_string: str,
            tg_phone_number: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "UserbotRepo.create_userbot",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_user_id": tg_user_id,
                    "tg_phone_number": tg_phone_number
                }
        ) as span:
            try:
                args = {
                    "tg_user_id": tg_user_id,
                    "session_string": session_string,
                    "tg_phone_number": tg_phone_number
                }
                userbot_id = await self.db.insert(create_userbot, args)

                span.set_status(Status(StatusCode.OK))
                return userbot_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def all_userbot(self) -> list[model.Userbot]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.all_userbot",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(all_userbot, {})
                if rows:
                    rows = model.Userbot.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def userbot_by_tg_user_id(self, userbot_tg_user_id: int) -> list[model.Userbot]:
        with self.tracer.start_as_current_span(
                "AmocrmSourceRepo.all_userbot",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(
                    userbot_by_tg_user_id,
                    {"tg_user_id": userbot_tg_user_id}
                )
                if rows:
                    rows = model.Userbot.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise