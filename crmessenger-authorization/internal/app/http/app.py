from fastapi import FastAPI

from internal import interface
from internal import model


def NewHTTP(
        db: interface.IDB,
        authorization_controller: interface.IAuthorizationController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_http_handler(
        app,
        authorization_controller,
        prefix,
    )

    return app

def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_http_handler(
        app: FastAPI,
        authorization_controller: interface.IAuthorizationController,
        prefix: str,
):
    app.add_api_route(prefix + "/", authorization_controller.authorization, methods=["POST"])
    app.add_api_route(prefix + "/check", authorization_controller.check_authorization, methods=["GET"])
    app.add_api_route(prefix + "/refresh", authorization_controller.refresh_token, methods=["GET"])


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
