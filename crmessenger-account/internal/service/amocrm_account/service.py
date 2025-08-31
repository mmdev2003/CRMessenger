from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import model
from internal import interface


class AmocrmAccountService(interface.IAmocrmAccountService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_account_repo: interface.IAmocrmAccountRepo,
    ):
        self.tracer = tel.tracer()
        self.amocrm_account_repo = amocrm_account_repo

    async def create_amocrm_account(
            self,
            account_id: int,
            amocrm_subdomain: str,
            amocrm_token: str
    ) -> int:
        with self.tracer.start_as_current_span(
                "AmocrmAccountService.create_amocrm_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "amocrm_subdomain": amocrm_subdomain
                }
        ) as span:
            try:
                amocrm_account_id = await self.amocrm_account_repo.create_amocrm_account(
                    account_id,
                    amocrm_subdomain,
                    amocrm_token,
                )

                span.set_status(Status(StatusCode.OK))
                return amocrm_account_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

