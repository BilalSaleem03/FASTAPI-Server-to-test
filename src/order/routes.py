from fastapi import APIRouter
from src.order.controllers import get_orders, get_order, cancel_order

order_routes = APIRouter(prefix="/api/orders", tags=["Orders"])

order_routes.get("/")(get_orders)
order_routes.get("/{order_id}")(get_order)
order_routes.delete("/{order_id}")(cancel_order)