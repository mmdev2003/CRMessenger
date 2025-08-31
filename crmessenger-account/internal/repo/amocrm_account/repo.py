from opentelemetry.trace import SpanKind, StatusCode, Status

from internal import model
from internal import interface
from .query import *


class AmocrmAccountRepo(interface.IAmocrmAccountRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def create_amocrm_account(
            self,
            account_id: int,
            amocrm_subdomain: str,
            amocrm_token: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmAccountRepo.create_amocrm_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "amocrm_subdomain": amocrm_subdomain
                }
        ) as span:
            try:
                args = {
                    "account_id": account_id,
                    "amocrm_subdomain": amocrm_subdomain,
                    "amocrm_token": amocrm_token
                }
                amocrm_account_id = await self.db.insert(create_amocrm_account, args)

                return amocrm_account_id

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def amocrm_account_by_id(self, amocrm_account_id: int) -> list[model.AmocrmAccount]:
        with self.tracer.start_as_current_span(
                "AmocrmAccountRepo.amocrm_account_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_account_id": amocrm_account_id,
                }
        ) as span:
            try:
                args = {"amocrm_account_id": amocrm_account_id}
                rows = await self.db.select(amocrm_account_by_id, args)
                if rows:
                    rows = model.AmocrmAccount.serialize(rows)

                return rows

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
