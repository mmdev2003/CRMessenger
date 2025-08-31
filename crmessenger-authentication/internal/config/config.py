import os

class Config:
    db_pass: str = os.environ.get('CRMESSENGER_AUTHENTICATION_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('CRMESSENGER_AUTHENTICATION_POSTGRES_USER')
    db_name: str = os.environ.get('CRMESSENGER_AUTHENTICATION_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('CRMESSENGER_AUTHENTICATION_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    prefix = "/api/authentication"
    domain: str = os.environ.get('CRMESSENGER_DOMAIN')
    http_port: int = int(os.environ.get('CRMESSENGER_AUTHENTICATION_PORT'))
    service_name = "crmessenger-authentication"

    password_secret_key: str = os.environ.get('CRMESSENGER_PASSWORD_SECRET_KEY')
    inter_server_secret_key: str = os.environ.get('CRMESSENGER_INTER_SERVER_SECRET_KEY')

    crmessenger_authorization_host: str = os.environ.get('CRMESSENGER_AUTHORIZATION_CONTAINER_NAME')
    crmessenger_authorization_port: int = os.environ.get('CRMESSENGER_AUTHORIZATION_PORT')

    crmessenger_account_host: str = os.environ.get('CRMESSENGER_ACCOUNT_CONTAINER_NAME')
    crmessenger_account_port: int = os.environ.get('CRMESSENGER_ACCOUNT_PORT')

    inter_server_secret_key: str = os.environ.get("CRMESSENGER_INTER_SERVER_SECRET_KEY")

    root_path = "/app"
    service_version = "0.0.1"
    otlp_host: str = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_GRPC_PORT")

    environment = os.environ.get('ENVIRONMENT')
    log_level = os.environ.get('LOG_LEVEL')

