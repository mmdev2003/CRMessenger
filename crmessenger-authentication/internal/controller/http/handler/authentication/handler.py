from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from datetime import timedelta, UTC

from internal import model
from internal import interface
from internal import common
from .model import *


class AuthenticationController(interface.IAuthenticationController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            authentication_service: interface.IAuthenticationService,
            domain: str
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.authentication_service = authentication_service
        self.domain = domain

    async def register(self, body: RegisterBody):
        email = body.email
        password = body.password

        with self.tracer.start_as_current_span(
                "AuthenticationController.register",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email,
                }
        ) as span:
            try:
                authorization_data = await self.authentication_service.register(
                    email,
                    password,
                )

                response = JSONResponse(
                    status_code=200,
                    content=RegisterResponse(account_id=authorization_data.account_id).model_dump(),
                )
                response.set_cookie(
                    key="Access-Token",
                    value=authorization_data.access_token,
                    expires=datetime.now(UTC) + timedelta(minutes=15),
                    httponly=True,
                    path="/",
                    domain=self.domain
                )
                response.set_cookie(
                    key="Refresh-Token",
                    value=authorization_data.refresh_token,
                    expires=datetime.now(UTC) + timedelta(hours=1),
                    httponly=True,
                    path="/",
                    domain=self.domain
                )

                span.set_status(StatusCode.OK)
                return response
            except common.ErrInvalidEmail as e:
                self.logger.warning("Неверный email")
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                return JSONResponse(
                    status_code=404,
                    content={"message": "Invalid email"}
                )
            except common.ErrAccountCreate as e:
                self.logger.warning("Аккаунт уже создан")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=404,
                    content={"message": "Unable to create account"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def confirm_register(self, account_id: int):
        with self.tracer.start_as_current_span(
                "AuthenticationController.confirm_register",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                await self.authentication_service.confirm_register(account_id)
                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def login(self, body: LoginBody):
        email = body.email
        password = body.password

        with self.tracer.start_as_current_span(
                "AuthenticationController.login",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email,
                }
        ) as span:
            try:
                authorization_data = await self.authentication_service.login(
                    email,
                    password,
                )

                response = JSONResponse(
                    status_code=200,
                    content=LoginResponse(
                        account_id=authorization_data.account_id,
                    ).model_dump(),
                )
                response.set_cookie(
                    key="Access-Token",
                    value=authorization_data.access_token,
                    expires=datetime.now(UTC) + timedelta(minutes=15),
                    httponly=True,
                    path="/",
                    domain=self.domain
                )
                response.set_cookie(
                    key="Refresh-Token",
                    value=authorization_data.refresh_token,
                    expires=datetime.now(UTC) + timedelta(hours=1),
                    httponly=True,
                    path="/",
                    domain=self.domain
                )

                span.set_status(Status(StatusCode.OK))
                return response
            except common.ErrAccountNotFound as e:
                self.logger.warn("Неверный email")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=404,
                    content={"message": "Account not found"}
                )

            except common.ErrInvalidPassword as e:
                self.logger.warning("Неверный пароль")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=403,
                    content={"message": "Invalid password"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def generate_two_fa(self, request: Request):
        with self.tracer.start_as_current_span(
                "AuthenticationController.generate_two_fa",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    self.logger.warning("Не авторизован пользователь")
                    raise common.ErrUnauthorized

                two_fa_key, qr_code = await self.authentication_service.generate_two_fa_key(
                    authorization_data.account_id)

                span.set_status(Status(StatusCode.OK))
                return StreamingResponse(
                    status_code=200,
                    content=qr_code,
                    headers={
                        "Two-Fa-Key": two_fa_key,
                        "Content-Type": "image/png"
                    }
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def set_two_fa(self, request: Request, body: SetTwoFaBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.set_two_fa",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    self.logger.warning("Не авторизован пользователь")
                    raise common.ErrUnauthorized

                await self.authentication_service.set_two_fa_key(
                    authorization_data.account_id,
                    body.two_fa_key,
                    body.two_fa_code
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "ok"}
                )
            except common.ErrTwoFaAlreadyEnabled as e:
                self.logger.warning("2FA уже включен")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=400,
                    content={"message": "Two-fa is already enabled"}
                )
            except common.ErrTwoFaCodeInvalid as e:
                self.logger.warning("Неверный 2FA код")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=403,
                    content={"message": "Two-fa code is invalid"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def delete_two_fa(self, request: Request, body: DeleteTwoFaBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.delete_two_fa",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    raise common.ErrUnauthorized
                await self.authentication_service.delete_two_fa_key(authorization_data.account_id, body.two_fa_code)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "ok"}
                )
            except common.ErrTwoFaNotEnabled as e:
                self.logger.warning("2FA не включен")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=400,
                    content={"message": "Two-fa is not enabled"}
                )
            except common.ErrTwoFaCodeInvalid as e:
                self.logger.warning("Неверный 2FA код")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=403,
                    content={"message": "Two-fa code is invalid"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def verify_two_fa(self, request: Request, body: VerifyTwoFaBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.verify_two_fa",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    raise common.ErrUnauthorized
                is_two_fa_verified = await self.authentication_service.verify_two_fa_key(authorization_data.account_id,
                                                                                         body.two_fa_code)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content=VerifyTwoFaResponse(is_two_fa_verified=is_two_fa_verified).model_dump()
                )
            except common.ErrTwoFaNotEnabled as e:
                self.logger.warning("2FA не включен")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=400,
                    content={"message": "Two-fa is not enabled"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

    async def forget_password(self, body: ForgotPasswordBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.forgot_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                await self.authentication_service.forget_password(body.email)
                span.set_status(StatusCode.OK)
            except common.ErrAccountNotFound():
                return JSONResponse(
                    status_code=404,
                    content={"message": "Account not found"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise e

    async def forgot_password_confirm(self, token: str):
        with self.tracer.start_as_current_span(
                "AuthenticationController.forgot_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                await self.authentication_service.forgot_password_confirmation(token)
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise e

    async def recovery_password(self, request: Request, body: RecoveryPasswordBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.recovery_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    raise common.ErrUnauthorized

                await self.authentication_service.recovery_password(
                    authorization_data.account_id,
                    body.new_password
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "ok"}
                )
            except common.ErrTwoFaNotEnabled as e:
                self.logger.warning("2FA не включен")
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                return JSONResponse(
                    status_code=400,
                    content={"message": "Two-fa is not enabled"}
                )
            except common.ErrTwoFaCodeInvalid as e:
                self.logger.warning("Неверный 2FA код")
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                return JSONResponse(
                    status_code=403,
                    content={"message": "Two-fa code is invalid"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise e

    async def change_password(self, request: Request, body: ChangePasswordBody):
        with self.tracer.start_as_current_span(
                "AuthenticationController.change_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                authorization_data: model.AuthorizationData = request.state.authorization_data
                if authorization_data.account_id == 0:
                    raise common.ErrUnauthorized

                await self.authentication_service.change_password(
                    authorization_data.account_id,
                    body.old_password,
                    body.new_password
                )

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=200,
                    content={"message": "ok"}
                )
            except common.ErrInvalidPassword as e:
                self.logger.warning("Неверный пароль")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return JSONResponse(
                    status_code=403,
                    content={"message": "Invalid password"}
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e
