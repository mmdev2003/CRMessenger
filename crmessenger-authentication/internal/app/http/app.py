from fastapi import FastAPI

from internal import interface
from internal import model


def NewHTTP(
        db: interface.IDB,
        authentication_controller: interface.IAuthenticationController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str,
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_authentication_handler(app, authentication_controller, prefix)
    return app

def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware,
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_authentication_handler(
        app: FastAPI,
        authentication_controller: interface.IAuthenticationController,
        prefix: str
):
    app.add_api_route(
        prefix + "/register",
        authentication_controller.register,
        methods=["POST"]
    )
    app.add_api_route(
        prefix + "/register/confirm/{account_id}",
        authentication_controller.confirm_register,
        methods=["GET"]
    )
    app.add_api_route(
        prefix + "/password/forget",
        authentication_controller.forget_password,
    )
    app.add_api_route(
        prefix + "/password/forget/confirmation&token={token}",
        authentication_controller.forgot_password_confirm,
    )
    app.add_api_route(
        prefix + "/password/recovery",
        authentication_controller.recovery_password,
        methods=["POST"]
    )
    app.add_api_route(
        prefix + "/password/change",
        authentication_controller.change_password,
        methods=["POST"]
    )
    app.add_api_route(
        prefix + "/login",
        authentication_controller.login,
        methods=["POST"]
    )

    app.add_api_route(
        prefix + "/2fa/generate",
        authentication_controller.generate_two_fa,
        methods=["GET"]
    )
    app.add_api_route(
        prefix + "/2fa/set",
        authentication_controller.set_two_fa,
        methods=["POST"]
    )
    app.add_api_route(
        prefix + "/2fa/del",
        authentication_controller.delete_two_fa,
        methods=["POST"]
    )
    app.add_api_route(
        prefix + "/2fa/verify",
        authentication_controller.verify_two_fa,
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
