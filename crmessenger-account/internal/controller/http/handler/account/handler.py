from fastapi import Request
from fastapi.responses import JSONResponse
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface

from .model import *


class AccountController(interface.IAccountController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            account_service: interface.IAccountService,
            inter_server_secret_key: str
    ):
        self.tracer = tel.tracer()
        self.account_service = account_service
        self.inter_server_secret_key = inter_server_secret_key

    async def create_account(self, body: CreateAccountBody):
        with self.tracer.start_as_current_span(
                "AccountController.create_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": body.account_id,
                    "login": body.login
                }
        ) as span:
            try:
                if body.inter_server_secret_key != self.inter_server_secret_key:
                    return JSONResponse(status_code=403, content={"message": "Wrong interserver secret key"})
                await self.account_service.create_account(body.account_id, body.login)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(status_code=200, content={"message": "Account successfully created"})
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
