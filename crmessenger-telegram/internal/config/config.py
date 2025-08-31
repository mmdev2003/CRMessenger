import os


class Config:
    db_pass: str = os.environ.get('CRMESSENGER_TELEGRAM_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('CRMESSENGER_TELEGRAM_POSTGRES_USER')
    db_name: str = os.environ.get('CRMESSENGER_TELEGRAM_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('CRMESSENGER_TELEGRAM_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    messenger = "Telegram"
    amocrm_api_platform_base_url: str = os.environ.get("AMOCRM_API_PLATFORM_BASE_URL")
    amocrm_api_chats_url: str = os.environ.get("AMOCRM_API_CHATS_BASE_URL")
    amocrm_bot_name: str = os.environ.get("AMOCRM_TELEGRAM_BOT_NAME")
    amocrm_bot_id: str = os.environ.get("AMOCRM_TELEGRAM_BOT_ID")
    amocrm_channel_secret: str = os.environ.get("AMOCRM_TELEGRAM_CHANNEL_SECRET")
    amocrm_channel_id: str = os.environ.get("AMOCRM_TELEGRAM_CHANNEL_ID")
    amocrm_channel_code: str = os.environ.get("AMOCRM_TELEGRAM_CHANNEL_CODE")
    amocrm_pipeline_id: int = int(os.environ.get("AMOCRM_TELEGRAM_PIPELINE_ID"))

    tg_api_id: int = int(os.environ.get("TELEGRAM_API_ID"))
    tg_hash_id: str = os.environ.get("TELEGRAM_HASH_ID")

    prefix = "/api/telegram"
    http_port: int = os.environ.get('CRMESSENGER_TELEGRAM_PORT')
    service_name = "crmessenger-telegram"

    root_path = "/app"
    service_version = "0.0.1"
    otlp_host: str = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("CRMESSENGER_OTEL_COLLECTOR_GRPC_PORT")

    environment = os.environ.get('ENVIRONMENT')
    log_level = os.environ.get('LOG_LEVEL')
