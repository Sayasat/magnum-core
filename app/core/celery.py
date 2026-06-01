from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "app.core.celery",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    backend="rpc://",
    include=["app.modules.orders.tasks"],
    broker_connection_retry_on_startup=True,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
