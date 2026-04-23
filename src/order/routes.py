# from fastapi import APIRouter
# from order.controllers import get_order, delete, get_all_orders

# router = APIRouter()
# order_routes = APIRouter(prefix="/order")

# @order_routes.get("/")
# async def get_all_orders():
#     return get_all_orders()

# @order_routes.get("/{order_id}")
# async def get_order(order_id: str):
#     return get_order(order_id)

# @order_routes.delete("/{order_id}")
# async def cancel_order(order_id: str):
#     return delete({"order_id": order_id})
from fastapi import APIRouter
from src.order.controllers import get_orders, get_order, cancel_order

order_routes = APIRouter(prefix="/api/orders", tags=["Orders"])

order_routes.get("/")(get_orders)
order_routes.get("/{order_id}")(get_order)
order_routes.delete("/{order_id}")(cancel_order)