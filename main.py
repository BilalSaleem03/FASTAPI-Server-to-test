from fastapi import FastAPI
import uvicorn
from src.user.routes import user_routes
from src.product.routes import product_routes
from src.order.routes import order_routes
from src.flask_apis.routes import flask_routes
from src.performance.routes import performance_routes
from src.product.controllers import app as legacy_product_app
from src.security.routes import security_v1_routes, security_v2_routes
from src.security.middleware import add_security_misconfigurations

app = FastAPI(
    title="Comprehensive Compliance, Security & Performance Benchmark",
    description="Dual-state benchmark with both intentionally vulnerable and compliant reference implementations for OWASP ZAP and Nova verification.",
    version="1.0.0"
)

# OWASP ZAP Security Misconfiguration Middleware
app.middleware("http")(add_security_misconfigurations)

# Include all routers
app.include_router(user_routes)
app.include_router(product_routes)
app.include_router(order_routes)
app.include_router(flask_routes)
app.include_router(performance_routes)
app.include_router(legacy_product_app.router)
app.include_router(security_v1_routes)
app.include_router(security_v2_routes)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Multi-Module API & Security Benchmark",
        "docs": "/docs",
        "vulnerable_endpoints": "/api/v1",
        "compliant_endpoints": "/api/v2"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)