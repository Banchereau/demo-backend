import os
from dataclasses import dataclass


APP_NAME = "demo-backend"
APP_VERSION = "1.0.0"


@dataclass(frozen=True)
class Settings:
    app_name: str = APP_NAME
    app_version: str = APP_VERSION

    db_host: str = os.environ["DB_HOST"]
    db_port: str = os.environ.get("DB_PORT", "5432")
    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]


settings = Settings()
