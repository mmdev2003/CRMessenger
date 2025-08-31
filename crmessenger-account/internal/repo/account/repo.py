from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import model
from internal import interface
from .query import *

class AccountRepo(interface.IAccountRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_account(self, account_id: int, login: str) -> int:
        with self.tracer.start_as_current_span(
                "AccountRepo.create_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "login": login
                }
        ) as span:
            try:
                args = {"account_id": account_id, "login": login}
                account_id = await self.db.insert(create_account, args)
                return account_id

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def account_by_id(self, account_id: int) -> list[model.Account]:
        with self.tracer.start_as_current_span(
                "AccountRepo.account_by_id",
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

                return rows

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
