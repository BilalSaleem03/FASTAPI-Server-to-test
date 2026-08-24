from fastapi import APIRouter
from src.order.controllers import (
	create_order,
	export_orders,
	generate_order_token,
	get_order,
	get_orders,
	order_debug_info,
	search_orders,
	cancel_order,
)

order_routes = APIRouter(prefix="/api/orders", tags=["Orders"])

order_routes.get("/")(get_orders)
order_routes.get("/search")(search_orders)
order_routes.post("/export")(export_orders)
order_routes.get("/generate-token")(generate_order_token)
order_routes.post("/")(create_order)
order_routes.get("/debug/info")(order_debug_info)
order_routes.get("/{order_id}")(get_order)
order_routes.delete("/{order_id}")(cancel_order)
# order_route.delete("/all-orders")
# order_route.delete("/all-orders-of-one-user")
