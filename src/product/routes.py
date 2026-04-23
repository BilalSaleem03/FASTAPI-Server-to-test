# from fastapi import APIRouter
# from product.controllers import get_product, update_product, get_all_products

# router = APIRouter()
# product_routes = APIRouter(prefix="/product")

# @product_routes.get("/")
# async def get_all_products():
#     return get_all_products()

# @product_routes.get("/{product_id}")
# async def get_product(product_id: int):
#     return get_product(product_id)

# @product_routes.put("/{product_id}")
# async def update_product(product_id: int):
#     return update_product()

from fastapi import APIRouter
from src.product.controllers import get_products, get_product, update_product

product_routes = APIRouter(prefix="/api/products", tags=["Products"])

product_routes.get("/")(get_products)
product_routes.get("/{product_id}")(get_product)
product_routes.put("/{product_id}")(update_product)