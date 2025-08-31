from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi.responses import JSONResponse
from .model import *
from internal import interface


class UserbotHttpController(interface.IUserbotHttpController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            userbot_service: interface.IUserbotService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.userbot_service = userbot_service


    async def generate_qr_code(self):
        with self.tracer.start_as_current_span(
                "UserbotHttpController.generate_qr_code",
                kind=SpanKind.INTERNAL,
                attributes={
                }
        ) as span:
            try:
                session_id, qr_url = await self.userbot_service.generate_qr_code()

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=200,
                    content={
                        "session_id": session_id,
                        "qr_url": qr_url
                    }
                )

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def qr_code_status(self, session_id: str):
        with self.tracer.start_as_current_span(
                "UserbotHttpController.qr_code_status",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                qr_status, tg_username =await self.userbot_service.qr_code_status(session_id)

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=200,
                    content={
                        "qr_status": qr_status,
                        "tg_username": tg_username
                    }
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise e


