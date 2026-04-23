from fastapi import FastAPI
import uvicorn
from src.user.routes import user_routes
from src.product.routes import product_routes
from src.order.routes import order_routes

app = FastAPI(title="Multi-Module API", description="API with three modules")

# Include all routes
app.include_router(user_routes)
app.include_router(product_routes)
app.include_router(order_routes)

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Module API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)