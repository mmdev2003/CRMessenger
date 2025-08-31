import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry

from pkg.client.internal.crmessenger_authorization.client import CRMessengerAuthorizationClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.account.handler import AccountController
from internal.controller.http.handler.amocrm_account.handler import AmocrmAccountController

from internal.repo.account.repo import AccountRepo
from internal.repo.amocrm_account.repo import AmocrmAccountRepo

from internal.service.account.service import AccountService
from internal.service.amocrm_account.service import AmocrmAccountService

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

account_repo = AccountRepo(tel, db)
amocrm_account_repo = AmocrmAccountRepo(tel, db)

account_service = AccountService(tel, account_repo)
amocrm_account_service = AmocrmAccountService(tel, amocrm_account_repo)

account_controller = AccountController(tel, account_service, cfg.inter_server_secret_key)
amocrm_account_controller = AmocrmAccountController(tel, amocrm_account_service)
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        account_controller,
        amocrm_account_controller,
        http_middleware,
        crmessenger_authorization_client,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=cfg.http_port, access_log=False)
