import bcrypt
import pyotp
import qrcode
import io

from opentelemetry.trace import Status, StatusCode, SpanKind
import email_validator

from internal import interface
from internal import model
from internal import common


class AuthenticationService(interface.IAuthenticationService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            authentication_repo: interface.IAuthenticationRepo,
            crmessenger_authorization_client: interface.ICRMessengerAuthorizationClient,
            crmessenger_account_client: interface.ICRMessengerAccountClient,
            smtp_client: interface.ISmtpClient,
            password_secret_key: str
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.authentication_repo = authentication_repo
        self.crmessenger_authorization_client = crmessenger_authorization_client
        self.crmessenger_account_client = crmessenger_account_client
        self.password_secret_key = password_secret_key
        self.smtp_client = smtp_client

    async def register(self, email: str, password: str) -> model.AuthorizationDataDTO:
        with self.tracer.start_as_current_span(
                "AuthenticationService.register",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email
                }
        ) as span:
            try:
                hashed_password = self.__hash_password(password)

                account_id = await self.authentication_repo.create_account(email, hashed_password)

                jwt_token = await self.crmessenger_authorization_client.authorization(account_id)

                await self.crmessenger_account_client.create_account(account_id, email)

                await self.__send_email_confirmation(account_id, email)

                span.set_status(StatusCode.OK)
                return model.AuthorizationDataDTO(
                    account_id=account_id,
                    access_token=jwt_token.access_token,
                    refresh_token=jwt_token.refresh_token,
                )
            except email_validator.EmailNotValidError:
                raise common.ErrInvalidEmail()
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise

    async def confirm_register(self, account_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.confirm_register",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                await self.authentication_repo.update_email_two_fa(account_id, True)
                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def login(self, email: str, password: str) -> model.AuthorizationDataDTO | None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.login",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email
                }
        ) as span:
            try:
                account = await self.authentication_repo.account_by_email(email)
                if not account:
                    raise common.ErrAccountNotFound()
                account = account[0]

                if not self.__verify_password(account.password, password):
                    raise common.ErrInvalidPassword()

                jwt_token = await self.crmessenger_authorization_client.authorization(account.id)

                span.set_status(Status(StatusCode.OK))
                return model.AuthorizationDataDTO(
                    account_id=account.id,
                    access_token=jwt_token.access_token,
                    refresh_token=jwt_token.refresh_token,
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def generate_two_fa_key(self, account_id: int) -> tuple[str, io.BytesIO]:
        with self.tracer.start_as_current_span(
                "AuthenticationService.generate_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                two_fa_key = pyotp.random_base32()
                totp_auth = pyotp.totp.TOTP(two_fa_key).provisioning_uri(
                    name=f"account_id-{account_id}",
                    issuer_name="crmessenger"
                )

                qr_image = io.BytesIO()
                qrcode.make(totp_auth).save(qr_image)
                qr_image.seek(0)

                span.set_status(Status(StatusCode.OK))
                return two_fa_key, qr_image
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def set_two_fa_key(self, account_id: int, two_fa_key: str, two_fa_code: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.set_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                account = (await self.authentication_repo.account_by_id(account_id))[0]

                if account.email_two_fa:
                    raise common.ErrTwoFaAlreadyEnabled()

                is_two_fa_verified = self.__verify_two_fa(two_fa_code, two_fa_key)
                if not is_two_fa_verified:
                    raise common.ErrTwoFaCodeInvalid()

                await self.authentication_repo.set_two_fa_key(account_id, two_fa_key)

                span.set_status(Status(StatusCode.OK))
                return None
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def delete_two_fa_key(self, account_id: int, two_fa_code: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.delete_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                account = (await self.authentication_repo.account_by_id(account_id))[0]
                if not account.email_two_fa:
                    raise common.ErrTwoFaNotEnabled()

                is_two_fa_verified = self.__verify_two_fa(two_fa_code, account.email_two_fa)
                if not is_two_fa_verified:
                    raise common.ErrTwoFaCodeInvalid()

                await self.authentication_repo.delete_two_fa_key(account_id)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def verify_two_fa_key(self, account_id: int, two_fa_code: str) -> bool:
        with self.tracer.start_as_current_span(
                "AuthenticationService.verify_two_fa_key",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                account = (await self.authentication_repo.account_by_id(account_id))[0]
                if not account.email_two_fa:
                    raise common.ErrTwoFaNotEnabled()

                is_two_fa_verified = self.__verify_two_fa(two_fa_code, account.two_fa_key)

                span.set_status(Status(StatusCode.OK))
                return is_two_fa_verified
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def forget_password(self, email: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.forgot_password",
                kind=SpanKind.INTERNAL,
                attributes={
                    "email": email
                }
        ) as span:
            try:
                account = await self.authentication_repo.account_by_email(email)
                if not account:
                    raise common.ErrAccountNotFound()
                account = account[0]

                if account.email_two_fa:
                    jwt_token = await self.crmessenger_authorization_client.authorization(account.id)

                    forgot_password_link = "https://wazzio.ru/api/authentication/password/forgot/confirmation?token="

                    forgot_password_text = common.forgot_password_text + forgot_password_link + str(jwt_token.access_token)
                    self.smtp_client.send_message(email, forgot_password_text)

                span.set_status(StatusCode.OK)
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise

    async def forgot_password_confirmation(self, token: str) -> model.AuthorizationDataDTO:
        with self.tracer.start_as_current_span(
                "AuthenticationService.forgot_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                resp = await self.crmessenger_authorization_client.check_authorization(token)
                jwt_token = await self.crmessenger_authorization_client.authorization(resp.account_id)

                return model.AuthorizationDataDTO(
                    account_id=resp.account_id,
                    access_token=jwt_token.access_token,
                    refresh_token=jwt_token.refresh_token,
                )
            except Exception as e:
                span.record_exception(e)
                span.set_status(StatusCode.ERROR, str(e))
                raise

    async def recovery_password(self, account_id: int, new_password: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.recovery_password",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                new_hashed_password = self.__hash_password(new_password)
                await self.authentication_repo.update_password(account_id, new_hashed_password)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def change_password(self, account_id: int, new_password: str, old_password: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.change_password",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                account = (await self.authentication_repo.account_by_id(account_id))[0]

                if not self.__verify_password(account.password, old_password):
                    raise common.ErrInvalidPassword()

                new_hashed_password = self.__hash_password(new_password)
                await self.authentication_repo.update_password(account_id, new_hashed_password)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def __send_email_confirmation(self, account_id: int, email: str) -> None:
        with self.tracer.start_as_current_span(
                "AuthenticationService.__verify_password",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                email_validator.validate_email(email)
                confirmation_text = common.email_confirmation_text + common.email_confirmation_link + str(account_id)
                self.smtp_client.send_message(email, confirmation_text)

                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def __verify_password(self, hashed_password: str, password: str) -> bool:
        with self.tracer.start_as_current_span(
                "AuthenticationService.__verify_password",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                peppered_password = self.password_secret_key + password

                span.set_status(Status(StatusCode.OK))
                return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed_password.encode('utf-8'))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def __verify_two_fa(self, two_fa_code: str, two_fa_key: str) -> bool:
        with self.tracer.start_as_current_span(
                "AuthenticationService.__verify_two_fa",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                totp = pyotp.TOTP(two_fa_key)

                span.set_status(Status(StatusCode.OK))
                return totp.verify(two_fa_code)
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    def __hash_password(self, password: str) -> str:
        with self.tracer.start_as_current_span(
                "AuthenticationService.__hash_password",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                peppered_password = self.password_secret_key + password
                hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())

                span.set_status(Status(StatusCode.OK))
                return hashed_password.decode('utf-8')
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
