from fastapi import APIRouter, status, Depends, Query, Header, Request, Response
from typing import Optional, List
from src.security.controllers import (
    health_check,
    get_users,
    search_catalog,
    generate_heavy_report,
    flaky_endpoint,
    create_item,
    insecure_hash_and_logging,
    evaluate_excessive_cyclomatic_complexity,
    open_redirect_endpoint,
    ssrf_endpoint,
    ping_command_injection,
    insecure_cookie_login,
    xxe_parse,
    ItemPayload,
    secure_health_check,
    get_secure_users,
    secure_cryptographic_hash,
    evaluate_modular_maintainable_logic,
    secure_search_catalog,
    SecureUserResponse,
    SecurePasswordRequest,
    require_authenticated_user
)

# Vulnerable benchmark router (v1 & unversioned baseline triggers)
security_v1_routes = APIRouter(tags=["Security Benchmark - Vulnerable (v1)"])

# 1. Baseline Route with Information Leakage (CWE-200)
security_v1_routes.get("/health", status_code=status.HTTP_200_OK)(health_check)
security_v1_routes.get("/api/v1/health", status_code=status.HTTP_200_OK)(health_check)

# 2. Broken Object Level Authorization & Data Exposure (CWE-200, CWE-639, OWASP A01:2021)
security_v1_routes.get("/api/v1/users", status_code=status.HTTP_200_OK)(get_users)
security_v1_routes.get("/api/v1/users/{user_id}", status_code=status.HTTP_200_OK)(get_users)

# 3. Reflected Cross-Site Scripting (XSS) & SQLi Trigger (CWE-79, CWE-89, OWASP A03:2021)
security_v1_routes.get("/api/v1/search")(search_catalog)

# 4. Sensitive File Inclusion / Path Traversal Trigger (CWE-22, OWASP A01:2021)
security_v1_routes.get("/api/v1/reports/heavy")(generate_heavy_report)

# 5. Stack Trace / Internal Error Disclosure (CWE-209, CWE-388)
security_v1_routes.get("/api/v1/unstable")(flaky_endpoint)

# 6. Unvalidated Input & Command Injection Simulation (CWE-78, CWE-20)
security_v1_routes.post("/api/v1/items", status_code=status.HTTP_201_CREATED)(create_item)

# 7. ISO 27001 Annex A.10.1.1: Weak/Deprecated Cryptography & Plaintext PII Logging
security_v1_routes.post("/api/v1/auth/insecure-hash")(insecure_hash_and_logging)

# 8. ISO 25010 Maintainability: Extreme Cyclomatic Complexity (> 20 Threshold)
security_v1_routes.get("/api/v1/admin/complex-logic")(evaluate_excessive_cyclomatic_complexity)

# Additional OWASP ZAP Targeted DAST Endpoints:
# 9. Open Redirect (CWE-601)
security_v1_routes.get("/api/v1/redirect")(open_redirect_endpoint)

# 10. SSRF / Cloud Metadata Service Trigger (CWE-918)
security_v1_routes.get("/api/v1/fetch")(ssrf_endpoint)

# 11. Command Injection via GET Query Parameter (CWE-78)
security_v1_routes.get("/api/v1/tools/ping")(ping_command_injection)

# 12. Insecure Cookie issuance without flags (CWE-614, CWE-1004)
security_v1_routes.post("/api/v1/auth/login-cookie")(insecure_cookie_login)

# 13. XML External Entity (XXE) Injection (CWE-611)
security_v1_routes.post("/api/v1/xml-parse")(xxe_parse)


# ==============================================================================
# COMPLIANT REFERENCE IMPLEMENTATIONS (v2)
# ==============================================================================
security_v2_routes = APIRouter(prefix="/api/v2", tags=["Security Benchmark - Compliant (v2)"])

# Compliant 1: Secure Zero-Leakage Health Check
security_v2_routes.get("/health/secure")(secure_health_check)

# Compliant 2: Authenticated User Inventory
security_v2_routes.get("/users/secure", response_model=List[SecureUserResponse])(get_secure_users)

# Compliant 3: Secure Key Derivation (PBKDF2-HMAC-SHA256)
security_v2_routes.post("/auth/secure-hash")(secure_cryptographic_hash)

# Compliant 4: Low-Complexity Modular Logic
security_v2_routes.get("/admin/modular-logic")(evaluate_modular_maintainable_logic)

# Compliant 5: Safe Input-Bounded Search
security_v2_routes.get("/catalog/optimized-search")(secure_search_catalog)
