from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model

from .sql_query import *


class AuthenticationRepo(interface.IAuthenticationRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_account(self, email: str, password: str) -> int:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.create_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email
                }
        ) as span:
            try:
                args = {
                    "email": email,
                    "password": password,
                }
                account_id = await self.db.insert(create_account, args)
                return account_id

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def update_email_two_fa(self, account_id: int, email_two_fa: bool) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.update_email_two_fa",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "email_two_fa": email_two_fa
                }
        ) as span:
            try:
                args = {
                    "account_id": account_id,
                    "email_two_fa": email_two_fa
                }

                await self.db.update(update_email_two_fa, args)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def account_by_id(self, account_id: int) -> list[model.Account]:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.account_by_id",
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

    async def account_by_email(self, email: str) -> list[model.Account]:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.account_by_email",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email,
                }
        ) as span:
            try:
                args = {"email": email}
                rows = await self.db.select(account_by_email, args)
                if rows:
                    rows = model.Account.serialize(rows)
                return rows

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def set_two_fa_key(self, account_id: int, two_fa_key: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.set_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                }
        ) as span:
            try:
                args = {
                    "account_id": account_id,
                    "two_fa_key": two_fa_key
                }
                await self.db.update(set_two_fa_key, args)

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def delete_two_fa_key(self, account_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.delete_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                }
        ) as span:
            try:
                args = {"account_id": account_id}
                await self.db.update(delete_two_fa_key, args)

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def update_password(self, account_id: int, new_password: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationRepo.update_password",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                }
        ) as span:
            try:
                args = {"account_id": account_id, "new_password": new_password}
                await self.db.update(update_password, args)

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise