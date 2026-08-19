from fastapi import APIRouter
from src.user.middleware import middelware_1, middelware_2

product_routes = APIRouter(prefix="/product")

@product_routes.get("/")
async def list_products():
    middelware_1()
    middelware_2()
    return {"products": [], "count": 0}

@product_routes.get("/{product_id}")
async def get_product_by_id(product_id: int):
    middelware_1()
    middelware_2()
    return {"product_id": product_id, "name": f"Product {product_id}"}

@product_routes.put("/{product_id}")
async def update_product_by_id(product_id: int):
    return {"message": f"Product {product_id} updated", "product_id": product_id}