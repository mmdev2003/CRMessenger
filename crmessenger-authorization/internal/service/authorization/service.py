import jwt
import time

from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import common
from internal import model


class AuthorizationService(interface.IAuthorizationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            authorization_repo: interface.IAuthorizationRepo,
            jwt_secret_key: str,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.authorization_repo = authorization_repo
        self.jwt_secret_key = jwt_secret_key

    async def create_tokens(self, account_id: int, two_fa_status: bool) -> model.JWTToken:
        with self.tracer.start_as_current_span(
                "AuthorizationService.create_tokens",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "two_fa_status": two_fa_status,
                }
        ) as span:
            try:
                account = await self.authorization_repo.account_by_id(account_id)
                if not account:
                    await self.authorization_repo.create_account(account_id, two_fa_status)
                    self.logger.info("Создали новый аккаунт")

                    account = await self.authorization_repo.account_by_id(account_id)
                account = account[0]

                access_token = await self.__create_jwt_token(account.id, account.two_fa_status, minutes=15)
                refresh_token = await self.__create_jwt_token(account.id, account.two_fa_status, minutes=30)

                await self.authorization_repo.update_refresh_token(account.id, refresh_token)
                self.logger.debug("Обновили refresh токен в БД")

                span.set_status(Status(StatusCode.OK))
                return model.JWTToken(access_token, refresh_token)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def check_token(self, token: str) -> model.TokenPayload:
        with self.tracer.start_as_current_span(
                "AuthorizationService.check_token",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                payload = jwt.decode(
                    jwt=token,
                    key=self.jwt_secret_key,
                    algorithms=["HS256"]
                )
                self.logger.debug("Расшифровали access токен")

                span.set_status(Status(StatusCode.OK))
                return model.TokenPayload(
                    account_id=int(payload["account_id"]),
                    two_fa_status=bool(payload["two_fa_status"]),
                    exp=int(payload["exp"]),
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def refresh_token(self, refresh_token: str) -> model.JWTToken:
        with self.tracer.start_as_current_span(
                "AuthorizationService.refresh_token",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                account = await self.authorization_repo.account_by_refresh_token(refresh_token)
                if not account:
                    raise common.ErrAccountNotFound()

                token_payload = await self.check_token(refresh_token)
                jwt_token = await self.create_tokens(
                    token_payload.account_id,
                    token_payload.two_fa_status,
                )

                span.set_status(Status(StatusCode.OK))
                return jwt_token
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def __create_jwt_token(self, account_id: int, two_fa_status: bool, minutes: int) -> str:
        with self.tracer.start_as_current_span(
                "AuthorizationService.__create_jwt_token",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "two_fa_status": two_fa_status,
                    "minutes": minutes,
                }
        ) as span:
            try:
                claims = {
                    "account_id": account_id,
                    "two_fa_status": two_fa_status,
                    "exp": int(time.time()) + minutes * 60,
                }
                jwt_token = jwt.encode(claims, self.jwt_secret_key, algorithm="HS256")
                self.logger.debug("Создали токен")

                span.set_status(Status(StatusCode.OK))
                return jwt_token

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
