from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model

from .sql_query import *


class AuthorizationRepo(interface.IAuthorizationRepo):
    def __init__(self, db: interface.IDB, tel: interface.ITelemetry):
        self.db = db
        self.tracer = tel.tracer()

    async def create_account(self, account_id: int, two_fa_status: bool) -> None:
        with self.tracer.start_as_current_span(
                "AuthorizationRepo.create_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "two_fa_status": two_fa_status,
                }
        ) as span:

            try:
                args = {"account_id": account_id, "two_fa_status": two_fa_status}
                await self.db.insert(create_account, args)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def account_by_id(self, account_id: int) -> list[model.Account]:
        with self.tracer.start_as_current_span(
                "AuthorizationRepo.account_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                }
        ) as span:

            try:
                args = {"account_id": account_id}
                rows = await self.db.select(account_by_id, args)
                if rows:
                    rows = model.Account.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def account_by_refresh_token(self, refresh_token: str) -> list[model.Account]:
        with self.tracer.start_as_current_span(
                "AuthorizationRepo.account_by_refresh_token",
                kind=SpanKind.INTERNAL
        ) as span:

            try:
                args = {"refresh_token": refresh_token}
                rows = await self.db.select(account_by_refresh_token, args)
                if rows:
                    rows = model.Account.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def update_refresh_token(self, account_id: int, refresh_token: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthorizationRepo.update_refresh_token",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                }
        ) as span:

            try:
                args = {"account_id": account_id, "refresh_token": refresh_token}
                await self.db.update(update_refresh_token, args)
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
