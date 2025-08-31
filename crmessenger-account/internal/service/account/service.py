from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface

class AccountService(interface.IAccountService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            account_repo: interface.IAccountRepo,
    ):
        self.tracer = tel.tracer()
        self.account_repo = account_repo

    async def create_account(self, account_id: int, login: str) -> int:
        with self.tracer.start_as_current_span(
                "AccountService.create_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "login": login
                }
        ) as span:
            try:
                return await self.account_repo.create_account(account_id, login)

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
