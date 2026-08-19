import os
from dataclasses import dataclass

APP_NAME = "demo-backend"
APP_VERSION = "1.0.0"


@dataclass(frozen=True)
class Settings:
    app_name: str = APP_NAME
    app_version: str = APP_VERSION

    db_host: str = os.environ.get("DB_HOST", "")
    db_port: str = os.environ.get("DB_PORT", "5432")
    db_name: str = os.environ.get("DB_NAME", "")
    db_user: str = os.environ.get("DB_USER", "")
    db_password: str = os.environ.get("DB_PASSWORD", "")
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(
        os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    exec_allowed_namespaces: tuple[str, ...] = tuple(
        namespace.strip()
        for namespace in os.environ.get(
            "EXEC_ALLOWED_NAMESPACES",
            "default",
        ).split(",")
        if namespace.strip()
    )

    max_deployment_replicas: int = int(
        os.environ.get("MAX_DEPLOYMENT_REPLICAS", "5")
    )


settings = Settings()
