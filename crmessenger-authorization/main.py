import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry

from internal.controller.http.middleware.middleware import HttpMiddleware

from internal.controller.http.handler.authorization.authorization import AuthorizationController

from internal.repo.authorization.repo import AuthorizationRepo

from internal.service.authorization.service import AuthorizationService

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

authorization_repo = AuthorizationRepo(db, tel)

authorization_service = AuthorizationService(tel, authorization_repo, cfg.jwt_secret_key)
authorization_controller = AuthorizationController(tel, authorization_service, cfg.domain)
http_middleware = HttpMiddleware(tel, cfg.prefix)


if __name__ == "__main__":
    app = NewHTTP(
        db,
        authorization_controller,
        http_middleware,
        cfg.prefix
    )
    uvicorn.run(app, host="0.0.0.0", port=cfg.http_port, access_log=False)
