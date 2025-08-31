import os

class Config:
    db_pass: str = os.environ.get('CRMESSENGER_AUTHORIZATION_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('CRMESSENGER_AUTHORIZATION_POSTGRES_USER')
    db_name: str = os.environ.get('CRMESSENGER_AUTHORIZATION_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('CRMESSENGER_AUTHORIZATION_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    prefix = "/api/authorization"
    domain: str = os.environ.get('CRMESSENGER_DOMAIN')
    http_port: int = int(os.environ.get('CRMESSENGER_AUTHORIZATION_PORT'))
    service_name = "crmessenger-authorization"

    jwt_secret_key: str = os.environ.get('CRMESSENGER_JWT_SECRET_KEY')

    root_path = "/app"
    service_version = "0.0.1"
    otlp_host: str = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_GRPC_PORT")

    environment = os.environ.get('ENVIRONMENT')
    log_level = os.environ.get('LOG_LEVEL')
