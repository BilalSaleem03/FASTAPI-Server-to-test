from fastapi import FastAPI
import uvicorn
from src.user.routes import user_routes
from src.product.routes import product_routes
from src.order.routes import order_routes
from src.flask_apis.routes import flask_routes
from src.performance.routes import performance_routes
from src.product.controllers import app as legacy_product_app

app = FastAPI(title="Multi-Module API", description="API with performance and security test suites")

# Include all routers
app.include_router(user_routes)
app.include_router(product_routes)
app.include_router(order_routes)
app.include_router(flask_routes)
app.include_router(performance_routes)
app.include_router(legacy_product_app.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Module API"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)