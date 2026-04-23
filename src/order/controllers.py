

# def get_order(order_id: str):
#     return {"order_id": order_id, "total_amount": 250.50, "status": "processing", "items": 5}

# def delete(order_data: dict):
#     return {"message": "Order deleted successfully", "order_id": order_data.get("order_id"), "status": "deleted"}

# def get_all_orders():
#     return {"orders": ["ORDER-001", "ORDER-002", "ORDER-003"], "total": 3, "status": "available"}

async def get_orders():
    return {"orders": ["ORDER-001", "ORDER-002", "ORDER-003"], "total": 3}

async def get_order(order_id: str):
    return {"order_id": order_id, "total_amount": 250.50, "status": "processing"}

async def cancel_order(order_id: str):
    return {"message": f"Order {order_id} cancelled", "cancelled": True}