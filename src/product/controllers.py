

# def get_product(product_id: int):
#     return {"product_id": product_id, "name": f"Product {product_id}", "price": 99.99, "in_stock": True}

# def update_product(product_data: dict):
#     return {"message": "Product created successfully", "product_id": 123, "status": "created"}

# def get_all_products():
#     return {"products": ["Laptop", "Mouse", "Keyboard"], "total": 3, "status": "available"}

async def get_products():
    return {"products": ["Laptop", "Mouse", "Keyboard"], "total": 3}

async def get_product(product_id: int):
    return {"product_id": product_id, "name": f"Product {product_id}", "price": 99.99}

async def update_product(product_id: int):
    return {"message": f"Product {product_id} updated successfully", "updated": True}