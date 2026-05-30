import logging
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import settings


def init_sentry(app: FastAPI):
    """
    Инициализация Sentry для FastAPI
    """
    # Логирование ошибок в Sentry
    sentry_logging = LoggingIntegration(
        level=logging.INFO,       # INFO и выше отправляется в Sentry
        event_level=logging.ERROR # только ошибки будут событиями
    )

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,# DSN из .env
        integrations=[sentry_logging],
        traces_sample_rate=1.0,   # для мониторинга производительности
        send_default_pii=True,    # отправлять данные о пользователях
    )

    # Middleware перехватывает все необработанные исключения FastAPI
    app.add_middleware(SentryAsgiMiddleware)