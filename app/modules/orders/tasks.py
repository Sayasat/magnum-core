import asyncio
from uuid import UUID

from app.core.celery import celery_app
from app.db.session import AsyncSessionLocal
from app.modules.orders.repository import OrderRepository


@celery_app.task(name="send_order_notification")
def send_order_notification(order_id: str) -> str:
    """
    Пример фоновой задачи: отправка уведомления о новом заказе
    """
    return asyncio.run(_send_order_notification(order_id))


async def _send_order_notification(order_id: str) -> str:
    async with AsyncSessionLocal() as session:
        repo = OrderRepository(session)
        order = await repo.get_by_id(UUID(order_id))

        if order:
            # Здесь можно подключить email, push или другие уведомления
            print(f"[Celery] Sending notification for order {order.id}")
            return f"notification sent for order {order.id}"

        return f"order {order_id} not found"
