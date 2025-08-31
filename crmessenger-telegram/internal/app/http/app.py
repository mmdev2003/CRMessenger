from contextlib import asynccontextmanager
from fastapi import FastAPI

from internal import model
from internal import interface


def NewHTTP(
        db: interface.IDB,
        http_middleware: interface.IHttpMiddleware,
        amocrm_controller: interface.IAmocrmController,
        userbot_http_controller: interface.IUserbotHttpController,
        userbot_service: interface.IUserbotService,
        prefix: str,
):
    app = FastAPI(lifespan=on_startup(userbot_service))
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_amocrm_source_handlers(app, amocrm_controller, prefix)
    include_userbot_handlers(app, userbot_http_controller, prefix)

    return app


def on_startup(userbot_service: interface.IUserbotService):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await userbot_service.start_all()
        yield

    return lifespan


def include_middleware(app: FastAPI, http_middleware: interface.IHttpMiddleware):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_amocrm_source_handlers(
        app: FastAPI,
        amocrm_controller: interface.IAmocrmController,
        prefix: str,
):
    app.add_api_route(
        prefix + "/amocrm/source/create",
        amocrm_controller.create_amocrm_source,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/amocrm/source/delete",
        amocrm_controller.delete_amocrm_source,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/send/from/amocrm/{scope_id}",
        amocrm_controller.send_message_from_amocrm_to_telegram,
        methods=["POST"],
    )


def include_userbot_handlers(
        app: FastAPI,
        userbot_http_controller: interface.IUserbotHttpController,
        prefix: str,
):
    app.add_api_route(
        prefix + "/qr/generate",
        userbot_http_controller.generate_qr_code,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/qr/status/{session_id}",
        userbot_http_controller.qr_code_status,
        methods=["GET"],
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_queries)
        except Exception as e:
            raise e

    return create_table


def drop_table_handler(db: interface.IDB):
    async def delete_table():
        try:
            await db.multi_query(model.drop_queries)
        except Exception as e:
            raise e

    return delete_table
