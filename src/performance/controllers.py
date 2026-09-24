import asyncio
import time
import random
from fastapi import HTTPException

# Module-level state to simulate resource exhaustion and memory leak
_request_counter = 0
_leak_buffer = []
_last_request_time = 0.0
_burst_counter = 0


async def get_healthy_fast():
    """Baseline healthy endpoint: Returns 200 OK instantly with sub-5ms latency."""
    return {
        "status": "healthy",
        "service": "performance-monitor",
        "timestamp": time.time(),
        "message": "Fast response under load",
    }


async def get_crash_under_load():
    """
    PERFORMANCE VULNERABILITY 1: Connection Pool / Thread Starvation (HTTP 500)
    Simulates database connection pool exhaustion or deadlock under concurrent load.
    Fails ~35-40% of the time with 500 Internal Server Error, driving Locust's
    server_errors_count and server_error_rate up to breach SLA thresholds.
    """
    global _request_counter
    _request_counter += 1

    # Simulate connection pool timeout or race failure under load
    if _request_counter % 3 == 0 or random.random() < 0.35:
        raise HTTPException(
            status_code=500,
            detail="SERVER_CRASH: Database connection pool exhausted - timeout waiting for available connection",
        )

    return {
        "status": "success",
        "data": f"Acquired DB connection for transaction #{_request_counter}",
    }


async def get_heavy_computation():
    """
    PERFORMANCE VULNERABILITY 2: Event-Loop Blocking & High Latency (SLA Breach)
    Calls synchronous time.sleep() directly inside an async handler, freezing
    the single-threaded asyncio event loop. Under Locust load (concurrency > 10),
    queued requests will suffer massive latency (> 2500ms - 4000ms), triggering
    the 'BREAKING POINT: Latency SLA saturation' and 'Critical Latency' bottlenecks.
    """
    # Synchronously blocking the async event loop (classic performance anti-pattern)
    time.sleep(1.8)
    return {
        "status": "completed",
        "latency_profile": "high-cpu-event-loop-starvation",
        "processed_records": 10000,
    }


async def get_memory_leak():
    """
    PERFORMANCE VULNERABILITY 3: Unbounded Memory Growth & Worker Exhaustion (HTTP 503)
    Simulates a memory leak by appending byte buffers on each request.
    Once memory threshold is reached, begins shedding load with 503 Service Unavailable.
    """
    global _leak_buffer
    # Leak 200 KB per request
    _leak_buffer.append(b"X" * (200 * 1024))

    if len(_leak_buffer) > 25:
        # Simulate worker OOM threshold
        if random.random() < 0.6:
            raise HTTPException(
                status_code=503,
                detail="SERVER_CRASH: Worker Out of Memory - Heap allocation threshold exceeded",
            )

    return {
        "status": "success",
        "current_leak_buffer_chunks": len(_leak_buffer),
        "total_leaked_kb": len(_leak_buffer) * 200,
    }


async def get_flaky_gateway():
    """
    PERFORMANCE VULNERABILITY 4: Downstream Microservice Failure (HTTP 504 / 502)
    Simulates an unstable third-party dependency (e.g. payment gateway or external CRM).
    Adds synthetic network delay and returns 504 Gateway Timeout on 30% of requests.
    """
    await asyncio.sleep(0.3)
    if random.random() < 0.30:
        raise HTTPException(
            status_code=504,
            detail="SERVER_CRASH: Downstream Gateway Timeout - Partner service did not respond in time",
        )

    return {"status": "success", "gateway": "payment-upstream", "state": "acknowledged"}


async def get_rate_limit_failure():
    """
    PERFORMANCE VULNERABILITY 5: Aggressive Rate-Limiting Rejection (HTTP 429)
    Simulates strict rate limits that reject legitimate load once burst rate spikes.
    Returns HTTP 429, which Locust records under client_errors_count (4xx failure).
    """
    global _last_request_time, _burst_counter
    current_time = time.time()

    if current_time - _last_request_time < 1.0:
        _burst_counter += 1
    else:
        _burst_counter = 1
        _last_request_time = current_time

    if _burst_counter > 5:
        raise HTTPException(
            status_code=429,
            detail="CLIENT_MISCONFIG: 429 Too Many Requests - Rate limit burst threshold exceeded",
        )

    return {"status": "ok", "burst_counter": _burst_counter}
