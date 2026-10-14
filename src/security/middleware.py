import logging
from fastapi import Request, Response

async def add_security_misconfigurations(request: Request, call_next):
    """
    Middleware that introduces specific security misconfigurations for OWASP ZAP passive scanning.
    For compliant endpoints (/api/v2/*), proper security headers are maintained.
    For vulnerable endpoints, banners and overly permissive headers are injected.
    """
    response: Response = await call_next(request)

    # Compliant v2 scope: Provide standard security headers and omit server banners
    if request.url.path.startswith("/api/v2"):
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        return response

    # Vulnerable scope (default):
    # 1. Expose underlying server banner (Information Disclosure - CWE-200)
    response.headers["Server"] = "Werkzeug/2.0.1 Python/3.13.0 Custom-Debug-Build"
    response.headers["X-Powered-By"] = "FastAPI/Starlette-Debug"

    # 2. Overly permissive CORS wildcard allowing credentials (CORS Misconfiguration - CWE-942)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    # 3. Explicitly omit CSP, HSTS, and X-Content-Type-Options / X-Frame-Options to trigger ZAP passive scanner rules
    if "Content-Security-Policy" in response.headers:
        del response.headers["Content-Security-Policy"]
    if "X-Frame-Options" in response.headers:
        del response.headers["X-Frame-Options"]
    if "X-Content-Type-Options" in response.headers:
        del response.headers["X-Content-Type-Options"]
    if "Strict-Transport-Security" in response.headers:
        del response.headers["Strict-Transport-Security"]

    return response
