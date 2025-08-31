import os
import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry

from pkg.client.internal.crmessenger_authorization.client import CRMessengerAuthorizationClient
from pkg.client.internal.crmessenger_account.client import CRMessengerAccountClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.authentication.handler import AuthenticationController

from internal.repo.authentication.repo import AuthenticationRepo

from internal.service.authentication.service import AuthenticationService

from internal.app.http.app import NewHTTP
from internal.config.config import Config

cfg = Config()

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
)
db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)

crmessenger_authorization_client = CRMessengerAuthorizationClient(
    tel,
    cfg.crmessenger_authorization_host,
    cfg.crmessenger_authorization_port
)

crmessenger_account_client = CRMessengerAccountClient(
    tel,
    cfg.crmessenger_account_host,
    cfg.crmessenger_account_port,
    cfg.inter_server_secret_key
)

authentication_repo = AuthenticationRepo(tel, db)

authentication_service = AuthenticationService(
    tel,
    authentication_repo,
    crmessenger_authorization_client,
    crmessenger_account_client,
    cfg.password_secret_key
)

authentication_controller = AuthenticationController(
    tel,
    authentication_service,
    cfg.domain,
)
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        authentication_controller,
        http_middleware,
        cfg.prefix
    )
    uvicorn.run(app, host="0.0.0.0", port=cfg.http_port, access_log=False)
