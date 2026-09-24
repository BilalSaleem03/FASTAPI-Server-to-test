from fastapi import APIRouter, HTTPException
import random
import time
from src.user.middleware import middelware_1, middelware_2

product_routes = APIRouter(prefix="/product")

@product_routes.get("/")
async def list_products():
    middelware_1()
    middelware_2()
    return {"products": [], "count": 0}

_product_stress_count = 0

@product_routes.get("/unstable-inventory")
async def unstable_inventory():
    """Simulates inventory lock contention under concurrent traffic (HTTP 500)."""
    global _product_stress_count
    _product_stress_count += 1
    if _product_stress_count % 3 == 0 or random.random() < 0.40:
        raise HTTPException(
            status_code=500,
            detail="SERVER_CRASH: Inventory service locking failure / deadlock",
        )
    return {"status": "in_stock", "inventory_query_id": _product_stress_count}

@product_routes.get("/heavy-analytics")
async def heavy_analytics():
    """Simulates blocking CPU-bound analytics freezing the event loop (High Latency)."""
    time.sleep(1.8)
    return {"analytics": "computed", "data_points": 50000}

@product_routes.get("/{product_id}")
async def get_product_by_id(product_id: int):
    middelware_1()
    middelware_2()
    return {"product_id": product_id, "name": f"Product {product_id}"}

@product_routes.put("/{product_id}")
async def update_product_by_id(product_id: int):
    return {"message": f"Product {product_id} updated", "product_id": product_id}