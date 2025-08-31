from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import common
from pkg.client.client import AsyncHTTPClient


class CRMessengerAccountClient(interface.ICRMessengerAccountClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            inter_server_secret_key: str
    ):
        self.inter_server_secret_key = inter_server_secret_key
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/account",
            use_tracing=True,
            logger=self.logger,
        )

    async def create_account(self, account_id: int, login: str) -> None:
        with self.tracer.start_as_current_span(
                "CRMessengerAccountClient.create_account",
                kind=SpanKind.CLIENT,
                attributes={
                    "account_id": account_id,
                    "login": login
                }
        ) as span:
            try:
                body = {
                    "account_id": account_id,
                    "login": login,
                    "inter_server_secret_key": self.inter_server_secret_key
                }

                response = await self.client.post(
                    "/create",
                    json=body
                )
                if response.status_code > 299:
                    err = common.ErrAccountCreate()
                    span.record_exception(err)
                    span.set_status(Status(StatusCode.ERROR, str(err)))
                    raise err

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
