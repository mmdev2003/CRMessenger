from fastapi import FastAPI

from internal import model
from internal import interface

PREFIX = "/api/account"


def NewHTTP(
        db: interface.IDB,
        account_controller: interface.IAccountController,
        amocrm_account_controller: interface.IAmocrmAccountController,
        http_middleware: interface.IHttpMiddleware,
        crmessenger_authorization_client: interface.ICRMessengerAuthorizationClient,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware , crmessenger_authorization_client)

    include_db_handler(app, db, prefix)
    include_http_account_handler(app, account_controller, prefix)
    include_http_amocrm_account_handler(app, amocrm_account_controller, prefix)
    return app

def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware,
        crmessenger_authorization_client: interface.ICRMessengerAuthorizationClient
):
    http_middleware.authorization_middleware04(app, crmessenger_authorization_client)
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_http_account_handler(
        app: FastAPI,
        account_controller: interface.IAccountController,
        prefix: str
):
    app.add_api_route(
        prefix + "/create",
        account_controller.create_account,
        methods=["POST"]
    )


def include_http_amocrm_account_handler(
        app: FastAPI,
        amocrm_account_controller: interface.IAmocrmAccountController,
        prefix: str
):
    app.add_api_route(
        prefix + "/amocrm/create",
        amocrm_account_controller.create_amocrm_account,
        methods=["POST"]
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
