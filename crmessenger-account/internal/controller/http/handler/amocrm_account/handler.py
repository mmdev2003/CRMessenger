from fastapi import Request
from fastapi.responses import JSONResponse
from opentelemetry.trace import SpanKind, StatusCode, Status

from internal import model
from internal import interface
from internal import common
from .model import *


class AmocrmAccountController(interface.IAmocrmAccountController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_account_service: interface.IAmocrmAccountService,
    ):
        self.tracer = tel.tracer()
        self.amocrm_account_service = amocrm_account_service

    async def create_amocrm_account(self, request: Request, body: CreateAmocrmAccountBody):
        with self.tracer.start_as_current_span(
                "AmocrmAccountController.create_amocrm_account",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_subdomain": body.amocrm_subdomain
                }
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    raise common.ErrUnauthorized

                await self.amocrm_account_service.create_amocrm_account(
                    authorization_data.account_id,
                    body.amocrm_subdomain,
                    body.amocrm_token
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "Amocrm account successfully created"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
