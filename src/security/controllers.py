import time
import random
import traceback
import hashlib
import hmac
import os
import logging
import re
from fastapi import HTTPException, status, Request, Response, Header, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List

security_bearer = HTTPBearer(auto_error=False)

# ==============================================================================
# ORIGINAL MOCK DATA & SCHEMAS
# ==============================================================================

USERS_DB = [
    {"id": 1, "username": "alice", "role": "admin", "password_hash": "$2b$12$e8Y7z9j1...mockHashAdmin", "email": "alice@nova.io"},
    {"id": 2, "username": "bob", "role": "developer", "password_hash": "$2b$12$k10Px8a2...mockHashDev", "email": "bob@nova.io"},
    {"id": 3, "username": "carol", "role": "tester", "password_hash": "$2b$12$q41Lo9c3...mockHashTester", "email": "carol@nova.io"}
]

ITEMS_DB = []


class ItemPayload(BaseModel):
    name: str
    price: float


# ==============================================================================
# INTENTIONAL STATIC SECRETS (ISO 27001 Annex A.9.4.3 / CWE-798)
# ==============================================================================

JWT_STATIC_SECRET = "secret_key = 'super_insecure_jwt_hardcoded_token_xyz987'"
STRIPE_API_KEY = "api_key = 'sk_live_51AbcDefGhIjKlMnOpQrStUvWxYz123456'"


# ==============================================================================
# VULNERABLE CONTROLLERS (OWASP ZAP / DAST / SAST TRIGGERS)
# ==============================================================================

# 1. Baseline Route with Information Leakage (CWE-200)
async def health_check():
    """Returns baseline status while exposing internal debug configs and private IPs."""
    return {
        "status": "healthy",
        "service": "security-bench",
        "debug_mode": True,
        "internal_ip": "10.0.4.15",
        "db_connection_string": "postgresql://postgres:admin_root_pass@127.0.0.1:5432/nova_db"
    }


# 2. Broken Object Level Authorization & Data Exposure (CWE-200, CWE-639, OWASP A01:2021)
async def get_users(user_id: Optional[int] = None):
    """Exposes all user data including passwords and roles without authentication."""
    if isinstance(user_id, int):
        user = next((u for u in USERS_DB if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    return {"total": len(USERS_DB), "data": USERS_DB}


# 3. Reflected Cross-Site Scripting (XSS) & SQLi Trigger (CWE-79, CWE-89, OWASP A03:2021)
async def search_catalog(query: str = "default"):
    """
    1. Triggers SQL Injection alerts if query contains SQL syntax characters (' OR 1=1, --, UNION, SELECT).
    2. Returns raw unsanitized HTML to trigger Reflected XSS alerts (<script>, <img>, etc.).
    """
    time.sleep(0.1)

    # Simulated SQL Injection Error Leakage (CWE-89)
    sqli_markers = [
        "'", '"', "--", "/*", "*/", "UNION", "SELECT", "OR 1=1", "OR '1'='1",
        "DROP", "SLEEP(", "BENCHMARK(", "WAITFOR DELAY"
    ]
    if any(marker.lower() in query.lower() for marker in sqli_markers):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Syntax error in SQL statement near: '" + query + "'",
                "driver_error": "psycopg2.errors.SyntaxError: unterminated quoted string at or near " + query,
                "executed_query": f"SELECT * FROM catalog WHERE item_name ILIKE '%{query}%'"
            }
        )

    # Reflected XSS (CWE-79): Renders query straight into unescaped HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head><title>Search Results</title></head>
        <body>
            <h2>Search results for: {query}</h2>
            <div id="results">
                <p>Showing matching catalog items for {query}</p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# 4. Sensitive File Inclusion / Path Traversal Trigger (CWE-22, OWASP A01:2021)
async def generate_heavy_report(file_path: Optional[str] = None):
    """Simulates directory traversal / arbitrary file read trigger for Linux & Windows."""
    if file_path:
        fp_lower = file_path.lower()
        if ".." in file_path or "/etc/" in fp_lower or "win.ini" in fp_lower or "passwd" in fp_lower:
            if "win.ini" in fp_lower or "boot.ini" in fp_lower:
                return Response(
                    content="[fonts]\r\nArial=arial.ttf\r\n[extensions]\r\n[mci extensions]\r\n",
                    media_type="text/plain",
                    status_code=200
                )
            return Response(
                content="root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\n",
                media_type="text/plain",
                status_code=200
            )
    time.sleep(2.1)  # Synthetic blocking delay: triggers ISO 25010 Time Behavior violation
    return {"report": "generated", "status": "completed"}


# 5. Stack Trace / Internal Error Disclosure (CWE-209, CWE-388)
async def flaky_endpoint(trigger_crash: bool = True):
    """Leaks raw internal stack traces and environment data upon failure."""
    if trigger_crash:
        try:
            raise RuntimeError("Database pool connection refused on internal port 5432")
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "exception_type": "RuntimeError",
                    "traceback": traceback.format_exc(),
                    "environment": {
                        "SECRET_KEY": "super_secret_production_jwt_key_12345",
                        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE"
                    }
                }
            )
    return {"status": "success"}


# 6. Unvalidated Input & Command Injection Simulation (CWE-78, CWE-20)
async def create_item(item: ItemPayload, x_forwarded_host: Optional[str] = Header(None)):
    """Validates item while checking for command injection and host header injection."""
    if any(char in item.name for char in [";", "|", "&", "`", "$"]):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Command execution failed",
                "output": f"/bin/sh: 1: {item.name}: not found"
            }
        )
    item_dict = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    ITEMS_DB.append(item_dict)
    return {"status": "created", "item": item, "processed_by_host": x_forwarded_host}


# 7. ISO 27001 Annex A.10.1.1: Weak/Deprecated Cryptography & Plaintext PII Logging
async def insecure_hash_and_logging(password: str, user_email: str):
    """
    1. Triggers COMP-PRIV-003: MD5/SHA1 usage breaches cryptographic controls.
    2. Triggers COMP-PRIV-002: Logging plaintext sensitive credentials/PII.
    """
    print(f"[SECURITY AUDIT] Received login attempt for user password: {password}")
    logging.info(f"Processing secret data for email: {user_email}")

    # Deprecated hashing primitive (triggers ISO 27001 Annex A.10.1.1)
    weak_md5_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    weak_sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()

    return {
        "md5": weak_md5_hash,
        "sha1": weak_sha1_hash,
        "status": "insecure_hashing_completed"
    }


# 8. ISO 25010 Maintainability: Extreme Cyclomatic Complexity (> 20 Threshold)
async def evaluate_excessive_cyclomatic_complexity(level: int = 1):
    """
    Triggers ISO 25010 Maintainability violation by introducing 24 branch conditions.
    Threshold is capped at 20.
    """
    score = 0
    if level == 1: score += 1
    if level == 2: score += 2
    if level == 3: score += 3
    if level == 4: score += 4
    if level == 5: score += 5
    if level == 6: score += 6
    if level == 7: score += 7
    if level == 8: score += 8
    if level == 9: score += 9
    if level == 10: score += 10
    if level == 11: score += 11
    if level == 12: score += 12
    if level == 13: score += 13
    if level == 14: score += 14
    if level == 15: score += 15
    if level == 16: score += 16
    if level == 17: score += 17
    if level == 18: score += 18
    if level == 19: score += 19
    if level == 20: score += 20
    if level == 21: score += 21
    if level == 22: score += 22
    if level == 23: score += 23
    if level == 24: score += 24

    return {"calculated_score": score, "complexity": "exceeds_threshold_20"}


# ==============================================================================
# ADDITIONAL OWASP ZAP SPECIALIZED ACTIVE VULNERABILITY TARGETS
# ==============================================================================

# 9. Open Redirect (CWE-601)
async def open_redirect_endpoint(url: str = Query("https://google.com")):
    """CWE-601: Open Redirect allowing user-controlled URL in HTTP 302 redirection."""
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# 10. SSRF / Cloud Metadata Service Trigger (CWE-918)
async def ssrf_endpoint(url: str = Query("http://example.com")):
    """CWE-918: Server-Side Request Forgery mimicking AWS/GCP internal metadata leakage."""
    url_lower = url.lower()
    if "169.254.169.254" in url_lower or "metadata.google" in url_lower:
        return Response(
            content="ami-id: ami-0123456789abcdef0\ninstance-id: i-0abcdef1234567890\nsecurity-credentials: nova-admin-role\n",
            media_type="text/plain"
        )
    if "localhost" in url_lower or "127.0.0.1" in url_lower:
        return {
            "status": "internal_loopback_accessed",
            "open_services": ["5432:postgresql", "6379:redis", "27017:mongodb"]
        }
    return {"status": "fetched", "target_url": url, "simulated_bytes": 1024}


# 11. Command Injection via Query Param (CWE-78)
async def ping_command_injection(host: str = Query("127.0.0.1")):
    """CWE-78: Simulates ping tool vulnerable to command injection via GET request."""
    if any(char in host for char in [";", "|", "&", "`", "$"]):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Command execution failed",
                "output": f"uid=0(root) gid=0(root) groups=0(root)\n/bin/sh: 1: {host}: not found"
            }
        )
    return {"host": host, "ping_output": f"64 bytes from {host}: icmp_seq=1 ttl=64 time=0.035 ms"}


# 12. Insecure Cookie without HttpOnly, Secure, or SameSite (CWE-614, CWE-1004)
async def insecure_cookie_login(response: Response, username: str = "guest"):
    """CWE-614 / CWE-1004: Insecure cookie issuance flagged by OWASP ZAP passive scanner."""
    response.set_cookie(
        key="session_token",
        value="INSECURE_SESSION_XYZ_987654321",
        httponly=False,
        secure=False,
        samesite=None
    )
    return {"message": "Authenticated", "user": username, "cookie_security": "insecure"}


# 13. XML External Entity (XXE) Trigger (CWE-611)
async def xxe_parse(request: Request):
    """CWE-611: Simulated XML entity expansion / XXE vulnerability."""
    raw_body = (await request.body()).decode("utf-8", errors="ignore")
    if "<!ENTITY" in raw_body or "SYSTEM" in raw_body:
        return Response(
            content="root:x:0:0:root:/root:/bin/bash\n[XXE: External Entity Successfully Resolved]\n",
            media_type="text/plain"
        )
    return {"status": "xml_received", "length": len(raw_body)}


# ==============================================================================
# COMPLIANT REFERENCE IMPLEMENTATIONS (PASSING CONTROLS FOR BALANCED SCORE)
# ==============================================================================

class SecureUserResponse(BaseModel):
    id: int
    username: str
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    role: str


class SecurePasswordRequest(BaseModel):
    user_email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, description="Secure password minimum 8 chars")


class SecureItemPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0.0)


def require_authenticated_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> dict:
    """ISO 27001 Annex A.9.4.2: Enforces valid bearer token dependency."""
    if not credentials or not credentials.credentials or credentials.credentials == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing or invalid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": 1, "username": "alice", "role": "admin"}


# Compliant 1: Secure, Zero-Leakage Health Check (ISO 25010 Time Behavior Passing)
async def secure_health_check():
    """ISO 25010 Compliant: Sub-millisecond response without config leakage."""
    return {"status": "healthy", "service": "nova-core", "code": 200}


# Compliant 2: Authenticated User Inventory (ISO 27001 Access Control Passing)
async def get_secure_users(
    user_id: Optional[int] = Query(None, ge=1),
    auth_user: dict = Depends(require_authenticated_user)
):
    """ISO 27001 Compliant: Sanitized user data protected by authorization."""
    results = [
        {"id": u["id"], "username": u["username"], "email": u.get("email", f"{u['username']}@nova.io"), "role": u["role"]}
        for u in USERS_DB
    ]
    if isinstance(user_id, int):
        filtered = [u for u in results if u["id"] == user_id]
        if not filtered:
            raise HTTPException(status_code=404, detail="User not found")
        return filtered
    return results


# Compliant 3: Secure Key Derivation (ISO 27001 Cryptography Control Passing)
async def secure_cryptographic_hash(payload: SecurePasswordRequest):
    """
    ISO 27001 (Annex A.10.1.1 / CWE-327 Compliant):
    Uses PBKDF2 HMAC-SHA256 with 100,000 iterations and a cryptographically secure random salt.
    """
    dynamic_salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        payload.password.encode("utf-8"),
        dynamic_salt,
        100_000
    )
    return {
        "status": "secure_hashing_completed",
        "algorithm": "PBKDF2-HMAC-SHA256",
        "iterations": 100_000,
        "key_fingerprint": derived_key.hex()[:16]
    }


# Compliant 4: Low-Complexity Modular Logic (ISO 25010 Maintainability Passing)
async def evaluate_modular_maintainable_logic(
    level: int = Query(1, ge=1, le=50),
    auth_user: dict = Depends(require_authenticated_user)
):
    """
    ISO 25010 Maintainability Compliant:
    Uses mathematical mapping instead of nested branch statements (Cyclomatic Complexity = 1).
    """
    lvl = level if isinstance(level, int) else 1
    calculated_score = (lvl * (lvl + 1)) // 2
    return {
        "calculated_score": calculated_score,
        "cyclomatic_complexity": 1,
        "status": "within_threshold"
    }


# Compliant 5: Safe Query Processing (ISO 25010 Time Behavior & OWASP A03 Passing)
async def secure_search_catalog(
    query: str = Query("default", min_length=1, max_length=50),
    auth_user: dict = Depends(require_authenticated_user)
):
    """ISO 25010 Compliant: Zero artificial delay, input bounded, authenticated."""
    return {
        "query": query,
        "results_count": 2,
        "results": [f"Item matching '{query}' - A", f"Item matching '{query}' - B"]
    }
