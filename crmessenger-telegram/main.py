import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry

from pkg.client.external.amocrm.client import AmocrmClient

from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.controller.tg.middlerware.middleware import TgMiddleware

from internal.controller.http.handler.userbot.handler import UserbotHttpController
from internal.controller.tg.handler.handler import UserbotTgController
from internal.controller.http.handler.amocrm.handler import AmocrmController

from internal.service.amocrm.service import AmocrmService
from internal.service.userbot.service import UserbotService

from internal.repo.amocrm.repo import AmocrmRepo
from internal.repo.userbot.repo import UserbotRepo

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

amocrm_client = AmocrmClient(
    tel,
    cfg.messenger,
    cfg.amocrm_api_platform_base_url,
    cfg.amocrm_api_chats_url,
    cfg.amocrm_bot_name,
    cfg.amocrm_bot_id,
    cfg.amocrm_channel_secret,
    cfg.amocrm_channel_id,
    cfg.amocrm_channel_code,
)

amocrm_repo = AmocrmRepo(db, tel)
userbot_repo = UserbotRepo(db, tel)

amocrm_service = AmocrmService(tel, amocrm_repo, amocrm_client, cfg.amocrm_pipeline_id)
userbot_tg_controller = UserbotTgController(tel, amocrm_service)

message_tg_middleware = TgMiddleware(tel, userbot_tg_controller.message_handler)
joined_chat_tg_middleware = TgMiddleware(tel, userbot_tg_controller.joined_chat)

userbot_service = UserbotService(
    tel,
    userbot_repo,
    amocrm_service,
    message_tg_middleware,
    joined_chat_tg_middleware,
    cfg.tg_api_id,
    cfg.tg_hash_id
)

amocrm_controller = AmocrmController(tel, amocrm_service, userbot_service)
userbot_http_controller = UserbotHttpController(tel, userbot_service)
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        http_middleware,
        amocrm_controller,
        userbot_http_controller,
        userbot_service,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)
