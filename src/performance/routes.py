from fastapi import APIRouter
from src.performance.controllers import (
    get_healthy_fast,
    get_crash_under_load,
    get_heavy_computation,
    get_memory_leak,
    get_flaky_gateway,
    get_rate_limit_failure,
)

performance_routes = APIRouter(prefix="/api/performance", tags=["Performance Testing"])

@performance_routes.get("/healthy")
async def healthy_endpoint():
    return await get_healthy_fast()

@performance_routes.get("/crash-under-load")
async def crash_under_load_endpoint():
    return await get_crash_under_load()

@performance_routes.get("/heavy-computation")
async def heavy_computation_endpoint():
    return await get_heavy_computation()

@performance_routes.get("/memory-leak")
async def memory_leak_endpoint():
    return await get_memory_leak()

@performance_routes.get("/flaky-gateway")
async def flaky_gateway_endpoint():
    return await get_flaky_gateway()

@performance_routes.get("/rate-limit")
async def rate_limit_endpoint():
    return await get_rate_limit_failure()
